"""
ANÁLISE DE PALAVRAS RESERVADAS - GRÁFICOS SEPARADOS
Versão para dissertação - apenas gráficos mais relevantes
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from networkx.algorithms import community

# Configurações
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# ============================================
# 1. CARREGAR DADOS
# ============================================

def carregar_logs(caminho_base):
    """Carrega todos os JSONs do diretório"""
    caminho = Path(caminho_base)
    arquivos_json = list(caminho.rglob('*.json'))
    
    print(f"Encontrados {len(arquivos_json)} arquivos JSON")
    
    todos_logs = []
    
    for arquivo in arquivos_json:
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                
                if isinstance(dados, list):
                    for log in dados:
                        if isinstance(log, dict) and 'keyword' in log:
                            log['arquivo_origem'] = arquivo.name
                            log['repositorio'] = arquivo.parent.name
                            todos_logs.append(log)
        except Exception as e:
            print(f"Erro em {arquivo.name}: {e}")
    
    df = pd.DataFrame(todos_logs)
    print(f"Total de registros: {len(df)}")
    print(f"Palavras únicas: {df['keyword'].nunique()}")
    
    return df

# Carregar seus dados
caminho = "/home/gilmar/Documents/algoritmos/logado-utfpr-ifam/logado-students"
df = carregar_logs(caminho)

# Converter timestamp
if 'timestamp' in df.columns and len(df) > 0:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['data'] = df['timestamp'].dt.date
    df['hora'] = df['timestamp'].dt.hour
    df['dia_semana'] = df['timestamp'].dt.day_name()
    df['semana'] = df['timestamp'].dt.isocalendar().week

# ============================================
# 2. GRÁFICO 1: TOP 20 PALAVRAS-CHAVE
# ============================================

def grafico_top20_keywords(df):
    """Gráfico de barras horizontal com top 20 palavras"""
    plt.figure(figsize=(10, 8))
    
    top20 = df['keyword'].value_counts().head(20)
    
    # Cores gradiente
    cores = plt.cm.viridis(np.linspace(0.2, 0.8, len(top20)))
    
    bars = plt.barh(range(len(top20)), top20.values, color=cores)
    plt.yticks(range(len(top20)), top20.index)
    plt.xlabel('Frequência', fontsize=12)
    plt.ylabel('Palavra-chave', fontsize=12)
    plt.title('Top 20 Palavras-chave Mais Frequentes', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    
    # Adicionar valores nas barras
    for i, (bar, val) in enumerate(zip(bars, top20.values)):
        plt.text(val + 5, i, f'{val}', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('figura_resultado_01_top20_keywords.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ Salvo: figura_resultado_01_top20_keywords.png")

# ============================================
# 3. GRÁFICO 2: DISTRIBUIÇÃO POR ARQUIVO
# ============================================

def grafico_distribuicao_arquivos(df):
    """Gráfico de pizza com top arquivos"""
    plt.figure(figsize=(10, 8))
    
    top_arquivos = df['file'].value_counts().head(8)
    
    # Cores personalizadas
    cores = plt.cm.Set3(np.linspace(0, 1, len(top_arquivos)))
    
    wedges, texts, autotexts = plt.pie(top_arquivos.values, 
                                        labels=top_arquivos.index, 
                                        autopct='%1.1f%%',
                                        colors=cores,
                                        explode=[0.02] * len(top_arquivos))
    
    # Ajustar fonte dos textos
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.title('Distribuição de Logs por Arquivo', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('figura_resultado_02_distribuicao_arquivos.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ Salvo: figura_resultado_02_distribuicao_arquivos.png")

# ============================================
# 4. GRÁFICO 3: OCORRÊNCIA POR HORA
# ============================================

def grafico_ocorrencia_hora(df):
    """Gráfico de barras com ocorrências por hora"""
    plt.figure(figsize=(10, 6))
    
    hora_counts = df['hora'].value_counts().sort_index()
    
    # Destacar horário de pico
    cores = ['coral' if h in [8, 9, 10, 14, 15, 16] else 'lightgray' for h in hora_counts.index]
    
    plt.bar(hora_counts.index, hora_counts.values, color=cores, alpha=0.8, edgecolor='black')
    plt.xlabel('Hora do Dia', fontsize=12)
    plt.ylabel('Número de Ocorrências', fontsize=12)
    plt.title('Ocorrência de Logs por Hora do Dia', fontsize=14, fontweight='bold')
    plt.xticks(range(0, 24, 2))
    plt.grid(axis='y', alpha=0.3)
    
    # Adicionar valores no topo das barras
    for i, (hora, val) in enumerate(zip(hora_counts.index, hora_counts.values)):
        if val > 0:
            plt.text(hora, val + 2, str(val), ha='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('figura_resultado_03_ocorrencia_hora.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ Salvo: figura_resultado_03_ocorrencia_hora.png")

# ============================================
# 5. GRÁFICO 4: REDE DE CO-OCORRÊNCIA
# ============================================

def construir_rede_coocorrencia(df, window=3):
    """Constrói rede de co-ocorrência entre palavras"""
    G = nx.Graph()
    
    # Adicionar nós com peso (frequência)
    freq = df['keyword'].value_counts()
    for palavra, f in freq.items():
        G.add_node(palavra, weight=f)
    
    # Calcular co-ocorrências
    co_ocorrencias = defaultdict(int)
    
    for arquivo in df['file'].unique():
        palavras = df[df['file'] == arquivo]['keyword'].tolist()
        
        for i in range(len(palavras)):
            for j in range(i+1, min(i+window, len(palavras))):
                if palavras[i] != palavras[j]:
                    par = tuple(sorted([palavras[i], palavras[j]]))
                    co_ocorrencias[par] += 1
    
    # Adicionar arestas (apenas co-ocorrências > 1)
    for (p1, p2), peso in co_ocorrencias.items():
        if peso >= 2:
            G.add_edge(p1, p2, weight=peso)
    
    print(f"Rede: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas")
    return G

def grafico_rede_coocorrencia(G, max_nodes=35):
    """Visualiza a rede de co-ocorrência"""
    # Filtrar nós mais conectados
    if G.number_of_nodes() > max_nodes:
        degrees = dict(G.degree())
        top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:max_nodes]
        G = G.subgraph(top_nodes)
    
    # Calcular comunidades
    try:
        communities_generator = community.greedy_modularity_communities(G)
        comunidades = {node: i for i, com in enumerate(communities_generator) for node in com}
    except:
        comunidades = {node: 0 for node in G.nodes()}
    
    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Figura
    plt.figure(figsize=(14, 12))
    
    # Nós - tamanho baseado na frequência
    node_sizes = [G.nodes[n].get('weight', 1) * 15 for n in G.nodes()]
    node_colors = [comunidades[n] for n in G.nodes()]
    
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, 
                           cmap='tab20', alpha=0.8)
    
    # Arestas - espessura baseada no peso
    edge_weights = [G.edges[e].get('weight', 1) for e in G.edges()]
    if edge_weights:
        edge_widths = [w / max(edge_weights) * 3 for w in edge_weights]
    else:
        edge_widths = [1] * len(G.edges())
    
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.3, edge_color='gray')
    
    # Labels
    labels = {n: n for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
    
    plt.title(f'Rede de Co-ocorrência de Palavras Reservadas\n({G.number_of_nodes()} nós, {G.number_of_edges()} arestas)', 
              fontsize=14, fontweight='bold')
    plt.axis('off')
    
    plt.tight_layout()
    plt.savefig('figura_resultado_04_rede_coocorrencia.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ Salvo: figura_resultado_04_rede_coocorrencia.png")
    
    return G

# ============================================
# 6. GRÁFICO 5: CENTRALIDADE DAS PALAVRAS
# ============================================

def grafico_centralidade(G):
    """Gráfico das palavras com maior centralidade de grau"""
    
    degree_cent = dict(G.degree())
    
    # Top 15 por centralidade de grau
    top_grau = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:15]
    
    plt.figure(figsize=(10, 8))
    
    palavras = [p for p, _ in top_grau]
    valores = [v for _, v in top_grau]
    
    # Cores gradiente
    cores = plt.cm.plasma(np.linspace(0.2, 0.8, len(palavras)))
    
    bars = plt.barh(range(len(palavras)), valores, color=cores)
    plt.yticks(range(len(palavras)), palavras)
    plt.xlabel('Centralidade de Grau (número de conexões)', fontsize=12)
    plt.ylabel('Palavra-chave', fontsize=12)
    plt.title('Palavras com Maior Centralidade na Rede de Co-ocorrência', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    
    # Adicionar valores
    for i, (bar, val) in enumerate(zip(bars, valores)):
        plt.text(val + 0.2, i, f'{val}', va='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('figura_resultado_05_centralidade.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ Salvo: figura_resultado_05_centralidade.png")

# ============================================
# 7. GRÁFICO 6: PALAVRAS EMERGENTES
# ============================================

def grafico_palavras_emergentes(df):
    """Identifica e plota palavras com maior crescimento ao longo do tempo"""
    
    # Agrupar por semana
    df['semana'] = df['timestamp'].dt.isocalendar().week
    
    # Calcular frequência por semana
    freq_semanal = df.groupby(['semana', 'keyword']).size().reset_index(name='count')
    
    # Para cada palavra, calcular crescimento
    palavras_emergentes = []
    
    for palavra in df['keyword'].unique():
        dados_palavra = freq_semanal[freq_semanal['keyword'] == palavra].sort_values('semana')
        if len(dados_palavra) >= 2:
            # Calcular crescimento da primeira para a última semana
            primeiro = dados_palavra.iloc[0]['count']
            ultimo = dados_palavra.iloc[-1]['count']
            if primeiro > 0:
                growth = (ultimo - primeiro) / primeiro * 100
                if growth > 50:  # Crescimento > 50%
                    palavras_emergentes.append((palavra, growth, ultimo))
    
    palavras_emergentes = sorted(palavras_emergentes, key=lambda x: x[1], reverse=True)[:12]
    
    if palavras_emergentes:
        plt.figure(figsize=(12, 8))
        
        palavras = [p for p, _, _ in palavras_emergentes]
        crescimentos = [c for _, c, _ in palavras_emergentes]
        
        # Cores baseadas no crescimento
        cores = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(palavras)))
        
        bars = plt.barh(range(len(palavras)), crescimentos, color=cores)
        plt.yticks(range(len(palavras)), palavras)
        plt.xlabel('Crescimento Percentual (%)', fontsize=12)
        plt.ylabel('Palavra-chave', fontsize=12)
        plt.title('Palavras com Maior Crescimento ao Longo das Semanas', fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()
        
        # Adicionar valores
        for i, (bar, val) in enumerate(zip(bars, crescimentos)):
            plt.text(val + 2, i, f'{val:.0f}%', va='center', fontsize=10)
        
        plt.tight_layout()
        plt.savefig('figura_resultado_06_palavras_emergentes.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Salvo: figura_resultado_06_palavras_emergentes.png")
    else:
        print("Nenhuma palavra com crescimento significativo encontrada")

# ============================================
# 8. EXECUTAR TODOS OS GRÁFICOS
# ============================================

if len(df) > 0:
    print("\n" + "="*50)
    print("GERANDO GRÁFICOS PARA DISSERTAÇÃO")
    print("="*50 + "\n")
    
    # Gráfico 1: Top 20 palavras
    grafico_top20_keywords(df)
    
    # Gráfico 2: Distribuição por arquivo
    grafico_distribuicao_arquivos(df)
    
    # Gráfico 3: Ocorrência por hora
    grafico_ocorrencia_hora(df)
    
    # Gráficos 4 e 5: Rede e centralidade
    G = construir_rede_coocorrencia(df, window=3)
    grafico_rede_coocorrencia(G, max_nodes=35)
    grafico_centralidade(G)
    
    # Gráfico 6: Palavras emergentes
    grafico_palavras_emergentes(df)
    
    print("\n" + "="*50)
    print("✅ TODOS OS GRÁFICOS FORAM GERADOS!")
    print("="*50)
    print("\n📁 Arquivos gerados:")
    print("   - figura_resultado_01_top20_keywords.png")
    print("   - figura_resultado_02_distribuicao_arquivos.png")
    print("   - figura_resultado_03_ocorrencia_hora.png")
    print("   - figura_resultado_04_rede_coocorrencia.png")
    print("   - figura_resultado_05_centralidade.png")
    print("   - figura_resultado_06_palavras_emergentes.png")
else:
    print("❌ Nenhum dado encontrado para processar!")
