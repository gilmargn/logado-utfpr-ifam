import json
import pandas as pd
from pathlib import Path
from collections import defaultdict, Counter

def gerar_csv_para_vosviewer(caminho_json, output_dir="vosviewer_csv"):
    """
    Gera arquivos CSV que o VOSviewer consegue ler facilmente
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 1. Carregar dados
    print("📂 Carregando JSONs...")
    todos_logs = []
    for arquivo in Path(caminho_json).rglob('*.json'):
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            if isinstance(dados, list):
                todos_logs.extend(dados)
    
    if not todos_logs:
        print("❌ Nenhum dado encontrado")
        return
    
    df = pd.DataFrame(todos_logs)
    print(f"✅ {len(df)} registros carregados")
    
    # 2. Criar matriz de co-ocorrência
    print("🔗 Calculando co-ocorrências...")
    co_occ = defaultdict(Counter)
    
    for arquivo in df['file'].unique():
        palavras = df[df['file'] == arquivo]['keyword'].tolist()
        for i in range(len(palavras)):
            for j in range(i+1, min(i+5, len(palavras))):
                if palavras[i] != palavras[j]:
                    p1, p2 = sorted([palavras[i], palavras[j]])
                    co_occ[p1][p2] += 1
    
    # 3. Criar arquivo de network (lista de arestas)
    print("💾 Gerando arquivos CSV...")
    
    # Arquivo de arestas (edges)
    edges_data = []
    for p1, conexoes in co_occ.items():
        for p2, peso in conexoes.items():
            edges_data.append({
                'source': p1,
                'target': p2,
                'weight': peso
            })
    
    edges_df = pd.DataFrame(edges_data)
    edges_df.to_csv(output_path / 'network.csv', index=False)
    print(f"✅ {len(edges_df)} conexões salvas em network.csv")
    
    # 4. Criar arquivo de nós (nodes) com frequências
    freq_palavras = df['keyword'].value_counts()
    nodes_data = []
    for palavra, freq in freq_palavras.items():
        nodes_data.append({
            'id': palavra,
            'label': palavra,
            'weight': freq,
            'cluster': 1  # Inicialmente todos no mesmo cluster
        })
    
    nodes_df = pd.DataFrame(nodes_data)
    nodes_df.to_csv(output_path / 'nodes.csv', index=False)
    print(f"✅ {len(nodes_df)} nós salvos em nodes.csv")
    
    # 5. Gerar instruções
    print("\n" + "="*60)
    print("✅ ARQUIVOS PRONTOS!")
    print("="*60)
    print(f"\n📁 Pasta: {output_path.absolute()}")
    print("\n📄 Arquivos gerados:")
    print("   - nodes.csv     (lista de palavras)")
    print("   - network.csv   (conexões entre palavras)")
    
    print("\n" + "="*60)
    print("🔧 COMO IMPORTAR NO VOSVIEWER")
    print("="*60)
    print("""
    1. Abra o VOSviewer
    2. Clique em Create → Create a map based on network data
    3. Selecione "Network data" como tipo de arquivo
    4. Clique em "Next"
    5. Em "Files", selecione:
       - Network data file: caminho/para/network.csv
       - (opcional) Node data file: caminho/para/nodes.csv
    6. Clique em "Next"
    7. Configure:
       - Source column: source
       - Target column: target
       - Weight column: weight
    8. Clique em "Next" e depois "Finish"
    """)
    
    # Salvar instruções
    with open(output_path / 'INSTRUCOES_VOSVIEWER.txt', 'w', encoding='utf-8') as f:
        f.write("INSTRUÇÕES PARA IMPORTAR NO VOSVIEWER\n")
        f.write("="*40 + "\n\n")
        f.write("1. Abra o VOSviewer\n")
        f.write("2. Create → Create a map based on network data\n")
        f.write("3. Selecione 'Network data'\n")
        f.write("4. Em 'Files', selecione network.csv\n")
        f.write("5. Configure:\n")
        f.write("   - Source column: source\n")
        f.write("   - Target column: target\n")
        f.write("   - Weight column: weight\n")
        f.write("6. Clique Finish\n")
    
    print(f"\n💾 Instruções salvas em: {output_path}/INSTRUCOES_VOSVIEWER.txt")
    
    return nodes_df, edges_df

# ========== EXECUTAR ==========
if __name__ == "__main__":
    # ALTERE PARA O CAMINHO DOS SEUS JSONS
    caminho = "/home/gilmar/Documents/algoritmos/logado-utfpr-ifam/logado-students"
    
    nodes, edges = gerar_csv_para_vosviewer(caminho, output_dir="vosviewer_ready")
