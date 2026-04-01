import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import List, Dict, Set, Tuple
import sqlite3
from collections import Counter

class JavaScriptReservedWordsAnalyzer:
    def __init__(self, base_path: str, output_dir: str = "analise_logs"):
        self.base_path = Path(base_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Palavras reservadas JavaScript (sua lista original)
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
        
        self.all_logs = []  # Para armazenar todos os logs encontrados
        
    def process_json_file(self, json_file: Path):
        """Processa um arquivo JSON no formato que você mostrou"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Verifica se é uma lista de logs (como no seu exemplo)
            if isinstance(data, list):
                for log_entry in data:
                    # Extrai os campos do seu JSON
                    keyword = log_entry.get('keyword', '')
                    timestamp = log_entry.get('timestamp', '')
                    file_name = log_entry.get('file', '')
                    line = log_entry.get('line', 0)
                    column = log_entry.get('column', 0)
                    
                    # Verifica se a keyword está na nossa lista de palavras reservadas
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
            else:
                print(f"Formato não esperado em {json_file}: não é uma lista")
                
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON em {json_file}: {e}")
        except Exception as e:
            print(f"Erro ao processar {json_file}: {e}")
    
    def analyze_all(self):
        """Analisa todos os arquivos JSON no diretório base"""
        print(f"Analisando arquivos em: {self.base_path}")
        
        json_files = list(self.base_path.rglob('*.json'))
        print(f"Encontrados {len(json_files)} arquivos JSON")
        
        for json_file in json_files:
            print(f"Processando: {json_file}")
            self.process_json_file(json_file)
        
        print(f"Total de entradas de log encontradas: {len(self.all_logs)}")
    
    def get_dataframe(self) -> pd.DataFrame:
        """Retorna os dados como DataFrame pandas"""
        if not self.all_logs:
            return pd.DataFrame()
        return pd.DataFrame(self.all_logs)
    
    def export_results(self):
        """Exporta resultados em múltiplos formatos"""
        if not self.all_logs:
            print("Nenhum resultado para exportar")
            return
        
        df = self.get_dataframe()
        
        # Exporta para CSV
        csv_file = self.output_dir / 'resultados_completos.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"✓ CSV exportado: {csv_file}")
        
        # Exporta para JSON
        json_file = self.output_dir / 'resultados_completos.json'
        df.to_json(json_file, orient='records', force_ascii=False, indent=2)
        print(f"✓ JSON exportado: {json_file}")
        
        # Exporta para Excel (se disponível)
        try:
            excel_file = self.output_dir / 'resultados_completos.xlsx'
            df.to_excel(excel_file, index=False, engine='openpyxl')
            print(f"✓ Excel exportado: {excel_file}")
        except:
            print("⚠ Excel export não disponível (instale openpyxl: pip install openpyxl)")
        
        # Gera resumos
        self.generate_summaries(df)
    
    def generate_summaries(self, df: pd.DataFrame):
        """Gera diversos resumos dos dados"""
        
        # 1. Resumo por keyword (palavra reservada)
        print("\n" + "="*60)
        print("RESUMO POR PALAVRA RESERVADA")
        print("="*60)
        keyword_summary = df['keyword'].value_counts()
        print(keyword_summary.to_string())
        
        # Salva resumo por keyword
        keyword_summary.to_csv(self.output_dir / 'resumo_por_keyword.csv')
        
        # 2. Resumo por arquivo de origem (file_origem)
        print("\n" + "="*60)
        print("RESUMO POR ARQUIVO DE ORIGEM")
        print("="*60)
        file_summary = df['file_origem'].value_counts()
        print(file_summary.to_string())
        
        # 3. Resumo por repositório
        print("\n" + "="*60)
        print("RESUMO POR REPOSITÓRIO")
        print("="*60)
        repo_summary = df['repositorio'].value_counts()
        print(repo_summary.to_string())
        
        # 4. Análise temporal (por hora/dia)
        if 'timestamp' in df.columns:
            df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
            df['data'] = df['timestamp_dt'].dt.date
            df['hora'] = df['timestamp_dt'].dt.hour
            
            print("\n" + "="*60)
            print("OCORRÊNCIAS POR DATA")
            print("="*60)
            date_summary = df['data'].value_counts().sort_index()
            print(date_summary.to_string())
            
            print("\n" + "="*60)
            print("OCORRÊNCIAS POR HORA DO DIA")
            print("="*60)
            hour_summary = df['hora'].value_counts().sort_index()
            print(hour_summary.to_string())
    
    def search_by_keyword(self, keyword: str) -> pd.DataFrame:
        """Busca logs por uma keyword específica"""
        df = self.get_dataframe()
        if df.empty:
            return df
        return df[df['keyword'].str.lower() == keyword.lower()]
    
    def search_by_file(self, file_name: str) -> pd.DataFrame:
        """Busca logs por arquivo de origem"""
        df = self.get_dataframe()
        if df.empty:
            return df
        return df[df['file_origem'].str.contains(file_name, case=False, na=False)]
    
    def search_by_repo(self, repo_name: str) -> pd.DataFrame:
        """Busca logs por repositório"""
        df = self.get_dataframe()
        if df.empty:
            return df
        return df[df['repositorio'].str.contains(repo_name, case=False, na=False)]
    
    def search_by_timerange(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Busca logs por intervalo de tempo"""
        df = self.get_dataframe()
        if df.empty:
            return df
        
        df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
        mask = (df['timestamp_dt'] >= start_date) & (df['timestamp_dt'] <= end_date)
        return df[mask]
    
    def generate_html_report(self):
        """Gera relatório HTML interativo"""
        if not self.all_logs:
            print("Nenhum dado para gerar relatório")
            return
        
        df = self.get_dataframe()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Análise de Palavras Reservadas JavaScript</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
                h2 {{ color: #555; margin-top: 30px; }}
                .summary {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .stats {{ display: flex; gap: 20px; flex-wrap: wrap; }}
                .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; flex: 1; min-width: 150px; }}
                .stat-card h3 {{ margin: 0 0 10px 0; font-size: 14px; opacity: 0.9; }}
                .stat-card .number {{ font-size: 32px; font-weight: bold; margin: 0; }}
                table {{ border-collapse: collapse; width: 100%; background: white; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; cursor: pointer; }}
                th:hover {{ background-color: #45a049; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                tr:hover {{ background-color: #ddd; }}
                .keyword {{ font-weight: bold; color: #4CAF50; }}
                .filter {{ margin: 20px 0; padding: 15px; background: white; border-radius: 8px; }}
                input, select {{ padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }}
                button {{ background-color: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }}
                button:hover {{ background-color: #45a049; }}
            </style>
        </head>
        <body>
            <h1>📊 Análise de Palavras Reservadas JavaScript</h1>
            
            <div class="summary">
                <div class="stats">
                    <div class="stat-card">
                        <h3>Total de Ocorrências</h3>
                        <p class="number">{len(self.all_logs)}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Palavras Únicas</h3>
                        <p class="number">{df['keyword'].nunique()}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Arquivos Analisados</h3>
                        <p class="number">{df['nome_arquivo'].nunique()}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Repositórios</h3>
                        <p class="number">{df['repositorio'].nunique()}</p>
                    </div>
                </div>
            </div>
            
            <div class="summary">
                <h2>📈 Top 10 Palavras Reservadas Mais Frequentes</h2>
                <table>
                    <thead>
                        <tr><th>Palavra</th><th>Frequência</th><th>% do Total</th></tr>
                    </thead>
                    <tbody>
        """
        
        # Top 10 keywords
        top_keywords = df['keyword'].value_counts().head(10)
        total = len(self.all_logs)
        
        for keyword, count in top_keywords.items():
            percentage = (count / total) * 100
            html_content += f"""
                        <tr>
                            <td class="keyword">{keyword}</td>
                            <td>{count}</td>
                            <td>{percentage:.1f}%</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="summary">
                <h2>📁 Top 10 Arquivos com Mais Ocorrências</h2>
                <table>
                    <thead>
                        <tr><th>Arquivo</th><th>Ocorrências</th></tr>
                    </thead>
                    <tbody>
        """
        
        # Top 10 files
        top_files = df['file_origem'].value_counts().head(10)
        for file_name, count in top_files.items():
            html_content += f"""
                        <tr>
                            <td>{file_name}</td>
                            <td>{count}</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="summary">
                <h2>🕒 Últimas 50 Ocorrências</h2>
                <div class="filter">
                    <input type="text" id="searchInput" placeholder="Filtrar por palavra..." onkeyup="filterTable()">
                </div>
                <table id="logsTable">
                    <thead>
                        <tr>
                            <th onclick="sortTable(0)">Timestamp</th>
                            <th onclick="sortTable(1)">Palavra</th>
                            <th onclick="sortTable(2)">Arquivo</th>
                            <th onclick="sortTable(3)">Linha</th>
                            <th onclick="sortTable(4)">Coluna</th>
                            <th onclick="sortTable(5)">Repositório</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Últimas 50 ocorrências (mais recentes primeiro)
        df_sorted = df.sort_values('timestamp', ascending=False).head(50)
        
        for _, row in df_sorted.iterrows():
            html_content += f"""
                        <tr>
                            <td>{row['timestamp']}</td>
                            <td class="keyword">{row['keyword']}</td>
                            <td>{row['file_origem']}</td>
                            <td>{row['linha']}</td>
                            <td>{row['coluna']}</td>
                            <td>{row['repositorio']}</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
            
            <script>
                function filterTable() {
                    var input, filter, table, tr, td, i, txtValue;
                    input = document.getElementById("searchInput");
                    filter = input.value.toUpperCase();
                    table = document.getElementById("logsTable");
                    tr = table.getElementsByTagName("tr");
                    
                    for (i = 0; i < tr.length; i++) {
                        td = tr[i].getElementsByTagName("td")[1];
                        if (td) {
                            txtValue = td.textContent || td.innerText;
                            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                                tr[i].style.display = "";
                            } else {
                                tr[i].style.display = "none";
                            }
                        }
                    }
                }
                
                function sortTable(n) {
                    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
                    table = document.getElementById("logsTable");
                    switching = true;
                    dir = "asc";
                    while (switching) {
                        switching = false;
                        rows = table.rows;
                        for (i = 1; i < (rows.length - 1); i++) {
                            shouldSwitch = false;
                            x = rows[i].getElementsByTagName("TD")[n];
                            y = rows[i + 1].getElementsByTagName("TD")[n];
                            if (dir == "asc") {
                                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                                    shouldSwitch = true;
                                    break;
                                }
                            } else if (dir == "desc") {
                                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                                    shouldSwitch = true;
                                    break;
                                }
                            }
                        }
                        if (shouldSwitch) {
                            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                            switching = true;
                            switchcount++;
                        } else {
                            if (switchcount == 0 && dir == "asc") {
                                dir = "desc";
                                switching = true;
                            }
                        }
                    }
                }
            </script>
        </body>
        </html>
        """
        
        html_file = self.output_dir / 'relatorio_interativo.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ Relatório HTML gerado: {html_file}")

# ========== USO PRÁTICO ==========

if __name__ == "__main__":
    # Caminho onde estão seus arquivos JSON
    # Altere para o caminho correto dos seus repositórios
    repos_path = "/home/gilmar/Documents/algoritmos/logado-utfpr-ifam/logado-students"
    
    # Inicializa o analisador
    analyzer = JavaScriptReservedWordsAnalyzer(
        base_path=repos_path,
        output_dir="analise_logs_js"
    )
    
    # Analisa todos os arquivos JSON
    analyzer.analyze_all()
    
    # Exporta resultados
    analyzer.export_results()
    
    # Gera relatório HTML
    analyzer.generate_html_report()
    
    # Exemplos de consultas específicas
    print("\n" + "="*60)
    print("CONSULTAS ESPECÍFICAS")
    print("="*60)
    
    # Busca por 'if'
    if_logs = analyzer.search_by_keyword('if')
    print(f"\nOcorrências da palavra 'if': {len(if_logs)}")
    if not if_logs.empty:
        print(if_logs[['timestamp', 'file_origem', 'linha', 'coluna']].head(10))
    
    # Busca por 'alert'
    alert_logs = analyzer.search_by_keyword('alert')
    print(f"\nOcorrências da palavra 'alert': {len(alert_logs)}")
    
    # Busca por 'var'
    var_logs = analyzer.search_by_keyword('var')
    print(f"\nOcorrências da palavra 'var': {len(var_logs)}")
    
    # Busca por arquivo específico
    aprovacao_logs = analyzer.search_by_file('aprovacao.js')
    print(f"\nOcorrências no arquivo aprovacao.js: {len(aprovacao_logs)}")
    
    # Análise temporal
    df = analyzer.get_dataframe()
    if not df.empty:
        print("\nPeríodo de análise:")
        print(f"Data mais antiga: {df['timestamp'].min()}")
        print(f"Data mais recente: {df['timestamp'].max()}")
        
        # Palavras mais frequentes
        print("\nTop 10 palavras reservadas mais frequentes:")
        print(df['keyword'].value_counts().head(10))