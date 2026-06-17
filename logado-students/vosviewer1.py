caminho_json = '/home/gilmar/Documents/algoritmos/logado-utfpr-ifam/logado-students'
def gerar_map_network_vosviewer(caminho_json, output_dir="vosviewer_native"):
    """
    Gera arquivos .map e .network no formato nativo do VOSviewer
    """
    import json
    import pandas as pd
    from pathlib import Path
    from collections import defaultdict, Counter
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Carregar dados
    todos_logs = []
    for arquivo in Path(caminho_json).rglob('*.json'):
        with open(arquivo, 'r') as f:
            dados = json.load(f)
            if isinstance(dados, list):
                todos_logs.extend(dados)
    
    df = pd.DataFrame(todos_logs)
    
    # Calcular frequências
    freq = df['keyword'].value_counts()
    
    # Gerar arquivo .map (lista de termos)
    with open(output_path / 'map.txt', 'w', encoding='utf-8') as f:
        f.write("id\tlabel\tweight\tcluster\trelevance\n")
        for i, (palavra, frequencia) in enumerate(freq.items(), 1):
            # Atribuir cluster baseado na frequência (simplificado)
            cluster = 1 if frequencia > 50 else 2 if frequencia > 20 else 3
            relevance = frequencia / len(df)
            f.write(f"{i}\t{palavra}\t{frequencia}\t{cluster}\t{relevance:.6f}\n")
    
    # Calcular co-ocorrências para .network
    co_occ = defaultdict(Counter)
    for arquivo in df['file'].unique():
        palavras = df[df['file'] == arquivo]['keyword'].tolist()
        for i in range(len(palavras)):
            for j in range(i+1, min(i+5, len(palavras))):
                if palavras[i] != palavras[j]:
                    p1, p2 = sorted([palavras[i], palavras[j]])
                    co_occ[p1][p2] += 1
    
    # Mapear palavras para IDs
    word_to_id = {palavra: i+1 for i, palavra in enumerate(freq.index)}
    
    # Gerar arquivo .network (conexões)
    with open(output_path / 'network.network', 'w', encoding='utf-8') as f:
        f.write("*Vertices\n")
        for palavra, id_num in word_to_id.items():
            f.write(f"{id_num} \"{palavra}\"\n")
        
        f.write("*Edges\n")
        for p1, conexoes in co_occ.items():
            for p2, peso in conexoes.items():
                if word_to_id[p1] < word_to_id[p2]:  # Evitar duplicatas
                    f.write(f"{word_to_id[p1]} {word_to_id[p2]} {peso}\n")
    
    print(f"✅ Arquivos gerados em: {output_path}")
    print("   - map.txt (lista de termos)")
    print("   - network.network (conexões)")
    print("\nPara importar no VOSviewer:")
    print("1. Create → Create a map based on network data")
    print("2. Selecione 'VOSviewer files'")
    print("3. Map file: map.txt")
    print("4. Network file: network.network")

# Executar
caminho = '/home/gilmar/Documents/algoritmos/logado-utfpr-ifam/logado-students'
gerar_map_network_vosviewer(caminho)
