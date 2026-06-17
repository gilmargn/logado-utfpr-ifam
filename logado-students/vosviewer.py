import json
import os
import re
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from itertools import combinations

# ============================================
# CLASSE PRINCIPAL - ANALISADOR DE LOGS
# ============================================

class JavaScriptReservedWordsAnalyzer:
    def __init__(self, base_path: str, output_dir: str = "analise_logs"):
        self.base_path = Path(base_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Palavras reservadas JavaScript
        self.reserved_words = {
            'let', 'const', 'var', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 
            'break', 'continue', 'function', 'return', 'new', 'this', 'class', 'try', 
            'catch', 'finally', 'throw', 'null', 'undefined', 'true', 'false', 
            'typeof', 'instanceof', 'console', 'log', 'error', 'warn', 'parseInt', 
            'parseFloat', 'Number', 'String', 'Boolean', 'Array', 'Object', 'Math', 
            'Date', 'JSON', 'push', 'pop', 'shift', 'unshift', 'length', 'forEach', 
            'map', 'filter', 'reduce', 'indexOf', 'includes', 'join', 'slice', 'splice', 
            'charAt', 'concat', 'replace', 'split', 'substring', 'toLowerCase', 
            'toUpperCase', 'trim', 'prompt', 'alert', 'confirm', 'toFixed', 'toPrecision', 
            'toString', 'toExponential', 'toLocaleString', 'valueOf', 'floor', 'ceil', 
            'round', 'random', 'max', 'min', 'abs', 'sqrt', 'pow', 'PI', 'E', 'sin', 
            'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'exp', 'log10', 'log2', 
            'sign', 'trunc', 'cbrt', 'hypot'
        }
        
        self.all_logs = []
    
    def process_json_file(self, json_file: Path):
        """Processa um arquivo JSON existente (seu formato)"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if isinstance(data, list):
                for log_entry in data:
                    keyword = log_entry.get('keyword', '')
                    timestamp = log_entry.get('timestamp', '')
                    file_name = log_entry.get('file', '')
                    line = log_entry.get('line', 0)
                    column = log_entry.get('column', 0)
                    
                    # Verifica se a keyword está na lista
                    if keyword.lower() in self.reserved_words:
                        self.all_logs.append({
                            'repositorio': json_file.parent.name,
                            'caminho_arquivo': str(json_file),
                            'nome_arquivo': json_file.name,
                            'keyword': keyword,
                            'timestamp': timestamp,
                            'file_origem': file_name,
                            'linha': line,
                            'coluna': column,
                            'data_analise': datetime.now().isoformat()
                        })
        except Exception as e:
            print(f"Erro ao processar {json_file}: {e}")
    
    def analyze_all(self):
        """Analisa todos os arquivos JSON"""
        print(f"Analisando arquivos em: {self.base_path}")
        json_files = list(self.base_path.rglob('*.json'))
        print(f"Encontrados {len(json_files)} arquivos JSON")
        
        for json_file in json_files:
            print(f"Processando: {json_file.name}")
            self.process_json_file(json_file)
        
        print(f"Total de entradas: {len(self.all_logs)}")
    
    def get_dataframe(self) -> pd.DataFrame:
        """Retorna DataFrame"""
        if not self.all_logs:
            return pd.DataFrame()
        return pd.DataFrame(self.all_logs)

# ============================================
# CLASSE PARA PREPARAR DADOS PARA VOSVIEWER
# ============================================

class VOSviewerDataPreparer:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.df = analyzer.get_dataframe()
        self.output_dir = Path(analyzer.output_dir) / "vosviewer_data"
        self.output_dir.mkdir(exist_ok=True)
        
    def prepare_co_occurrence_matrix(self, window_size=5):
        """Prepara matriz de co-ocorrência"""
        if self.df.empty:
            print("Sem dados para processar")
            return
        
        print("Preparando matriz de co-ocorrência...")
        
        co_occurrence = defaultdict(Counter)
        
        # Agrupa por arquivo de origem
        for file_name in self.df['file_origem'].unique():
            file_logs = self.df[self.df['file_origem'] == file_name].sort_values('timestamp')
            keywords = file_logs['keyword'].tolist()
            
            # Janela deslizante para co-ocorrência
            for i in range(len(keywords)):
                for j in range(i+1, min(i+window_size, len(keywords))):
                    if keywords[i] != keywords[j]:
                        pair = tuple(sorted([keywords[i], keywords[j]]))
                        co_occurrence[pair[0]][pair[1]] += 1
        
        # Converte para matriz
        all_keywords = sorted(set(self.df['keyword'].unique()))
        matrix = pd.DataFrame(0, index=all_keywords, columns=all_keywords, dtype=int)
        
        for kw1, counter in co_occurrence.items():
            for kw2, count in counter.items():
                matrix.loc[kw1, kw2] = count
                matrix.loc[kw2, kw1] = count
        
        # Salva matriz
        matrix_file = self.output_dir / "co_occurrence_matrix.csv"
        matrix.to_csv(matrix_file)
        print(f"✓ Matriz salva: {matrix_file}")
        
        # Salva no formato VOSviewer
        self._save_vosviewer_format(matrix)
        
        return matrix
    
    def _save_vosviewer_format(self, matrix):
        """Salva nos formatos que o VOSviewer entende"""
        nodes = matrix.index.tolist()
        
        # Arquivo de nós
        nodes_file = self.output_dir / "vosviewer_nodes.net"
        with open(nodes_file, 'w', encoding='utf-8') as f:
            f.write(f"*Vertices {len(nodes)}\n")
            for i, node in enumerate(nodes, 1):
                freq = self.df[self.df['keyword'] == node].shape[0]
                f.write(f'{i} "{node}" ic Red freq {freq}\n')
        
        # Arquivo de arestas
        edges_file = self.output_dir / "vosviewer_edges.net"
        edge_count = 0
        with open(edges_file, 'w', encoding='utf-8') as f:
            for i, kw1 in enumerate(nodes, 1):
                for j, kw2 in enumerate(nodes, 1):
                    if i < j and matrix.loc[kw1, kw2] > 0:
                        if edge_count == 0:
                            f.write(f"*Arcs\n")
                        edge_count += 1
                        f.write(f'{i} {j} {matrix.loc[kw1, kw2]}\n')
        
        print(f"✓ Arquivos VOSviewer: {nodes_file}, {edges_file}")
        print(f"  - {len(nodes)} nós, {edge_count} arestas")
    
    def generate_summary_report(self):
        """Gera relatório resumo"""
        if self.df.empty:
            return
        
        report_file = self.output_dir / "RESUMO_VOSVIEWER.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("DADOS PREPARADOS PARA VOSVIEWER\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Total de logs: {len(self.df)}\n")
            f.write(f"Palavras únicas: {self.df['keyword'].nunique()}\n")
            f.write(f"Arquivos: {self.df['file_origem'].nunique()}\n")
            f.write(f"Repositórios: {self.df['repositorio'].nunique()}\n\n")
            
            f.write("TOP 20 PALAVRAS:\n")
            f.write("-"*40 + "\n")
            for word, count in self.df['keyword'].value_counts().head(20).items():
                f.write(f"  {word}: {count}\n")
            
            f.write("\nCOMO USAR NO VOSVIEWER:\n")
            f.write("-"*40 + "\n")
            f.write("1. Abra o VOSviewer\n")
            f.write("2. Create → Create a map based on network data\n")
            f.write("3. Selecione os arquivos:\n")
            f.write(f"   - Nodes: {self.output_dir}/vosviewer_nodes.net\n")
            f.write(f"   - Edges: {self.output_dir}/vosviewer_edges.net\n")
        
        print(f"✓ Relatório salvo: {report_file}")

# ============================================
# FUNÇÃO MAIN - PONTO DE ENTRADA
# ============================================

def main():
    # ALTERE ESTE CAMINHO PARA O SEU DIRETÓRIO
    repos_path = "/home/gilmar/Documents/algoritmos/logado-utfpr-ifam/logado-students"
    
    print("="*60)
    print("ANALISADOR DE PALAVRAS RESERVADAS JAVASCRIPT")
    print("="*60)
    
    # Passo 1: Analisar os logs
    print("\n[1/3] Analisando arquivos JSON...")
    analyzer = JavaScriptReservedWordsAnalyzer(
        base_path=repos_path,
        output_dir="analise_logs_js"
    )
    analyzer.analyze_all()
    
    # Passo 2: Verificar se encontrou dados
    df = analyzer.get_dataframe()
    if df.empty:
        print("\n❌ Nenhum dado encontrado!")
        print("Verifique se:")
        print("  - O caminho está correto")
        print("  - Existem arquivos JSON no diretório")
        print("  - Os JSONs estão no formato esperado")
        return
    
    # Passo 3: Preparar para VOSviewer
    print("\n[2/3] Preparando dados para VOSviewer...")
    vos_prep = VOSviewerDataPreparer(analyzer)
    vos_prep.prepare_co_occurrence_matrix()
    vos_prep.generate_summary_report()
    
    # Passo 4: Mostrar resumo
    print("\n[3/3] Resumo dos dados:")
    print(f"  - Total de ocorrências: {len(df)}")
    print(f"  - Palavras únicas: {df['keyword'].nunique()}")
    print(f"  - Arquivos analisados: {df['file_origem'].nunique()}")
    print(f"  - Período: {df['timestamp'].min()} a {df['timestamp'].max()}")
    
    print("\n" + "="*60)
    print("✅ PREPARAÇÃO CONCLUÍDA!")
    print("="*60)
    print(f"\nArquivos gerados em: {vos_prep.output_dir}")
    print("\nPara usar no VOSviewer:")
    print("1. Abra o VOSviewer")
    print("2. Create → Create a map based on network data")
    print(f"3. Importe os arquivos da pasta: {vos_prep.output_dir}")

# ============================================
# EXECUTAR
# ============================================

if __name__ == "__main__":
    main()