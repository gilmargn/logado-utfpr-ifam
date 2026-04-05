"""
ANÁLISE COMPLETA DE PALAVRAS RESERVADAS EM PYTHON
Sem dependência de VOSviewer - visualizações diretas em Python
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Visualização
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# Análise de redes
import networkx as nx
from networkx.algorithms import community

# Para gráficos interativos (opcional)
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Plotly não instalado. Instale com: pip install plotly")

# Configurações de estilo
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

if df.empty:
    print("Nenhum dado encontrado! Usando dados de exemplo...")
    # Dados de exemplo para teste
    np.random.seed(42)
    palavras = ['if', 'else', 'for', 'while', 'var', 'let', 'const', 
                'function', 'return', 'alert', 'console', 'log', 'error']
    df = pd.DataFrame({
        'keyword': np.random.choice(palavras, 1000, p=[0.15,0.12,0.10,0.08,0.10,0.08,0.05,0.08,0.07,0.05,0.06,0.04,0.02]),
        'timestamp': pd.date_range('2024-01-01', periods=1000, freq='H'),
        'file': np.random.choice([f'arquivo{i}.js' for i in range(1,21)], 1000),
        'line': np.random.randint(1, 100, 1000),
        'coluna': np.random.randint(1, 50, 1000)
    })

# Converter timestamp
if 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['data'] = df['timestamp'].dt.date
    df['hora'] = df['timestamp'].dt.hour
    df['dia_semana'] = df['timestamp'].dt.day_name()
    df['mes'] = df['timestamp'].dt.month_name()

# ============================================
# 2. ANÁLISE DESCRITIVA E GRÁFICOS BÁSICOS
# ============================================

def analise_descritiva(df):
    """Gráficos básicos de frequência"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Top 20 palavras
    top20 = df['keyword'].value_counts().head(20)
    axes[0,0].barh(range(len(top20)), top20.values, color='steelblue')
    axes[0,0].set_yticks(range(len(top20)))
    axes[0,0].set_yticklabels(top20.index)
    axes[0,0].set_xlabel('Frequência')
    axes[0,0].set_title('Top 20 Palavras Reservadas')
    axes[0,0].invert_yaxis()
    
    # Distribuição por arquivo (top 10)
    top_arquivos = df['file'].value_counts().head(10)
    axes[0,1].pie(top_arquivos.values, labels=top_arquivos.index, autopct='%1.1f%%')
    axes[0,1].set_title('Distribuição por Arquivo')
    
    # Distribuição por hora
    hora_counts = df['hora'].value_counts().sort_index()
    axes[1,0].bar(hora_counts.index, hora_counts.values, color='coral', alpha=0.7)
    axes[1,0].set_xlabel('Hora do Dia')
    axes[1,0].set_ylabel('Ocorrências')
    axes[1,0].set_title('Ocorrências por Hora')
    axes[1,0].set_xticks(range(0, 24, 2))
    
    # Distribuição por dia da semana
    dias_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dia_counts = df['dia_semana'].value_counts().reindex(dias_order)
    axes[1,1].bar(dia_counts.index, dia_counts.values, color='forestgreen', alpha=0.7)
    axes[1,1].set_xlabel('Dia da Semana')
    axes[1,1].set_ylabel('Ocorrências')
    axes[1,1].set_title('Ocorrências por Dia da Semana')
    axes[1,1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('01_analise_descritiva.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("✓ Gráfico salvo: 01_analise_descritiva.png")

analise_descritiva(df)

# ============================================
# 3. ANÁLISE TEMPORAL
# ============================================

def analise_temporal(df):
    """Evolução temporal das palavras"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Evolução diária (top 5 palavras)
    top5 = df['keyword'].value_counts().head(5).index.tolist()
    
    for palavra in top5:
        diario = df[df['keyword'] == palavra].groupby('data').size()
        axes[0,0].plot(diario.index, diario.values, label=palavra, linewidth=2, marker='o', markersize=3)
    
    axes[0,0].set_xlabel('Data')
    axes[0,0].set_ylabel('Ocorrências')
    axes[0,0].set_title('Evolução Temporal - Top 5 Palavras')
    axes[0,0].legend()
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Heatmap por hora do dia (top palavras)
    pivot_hora = pd.crosstab(df['hora'], df['keyword'])
    top10_palavras = df['keyword'].value_counts().head(10).index
    sns.heatmap(pivot_hora[top10_palavras].T, ax=axes[0,1], cmap='YlOrRd', cbar_kws={'label': 'Frequência'})
    axes[0,1].set_title('Heatmap: Palavra vs Hora do Dia')
    axes[0,1].set_xlabel('Hora')
    axes[0,1].set_ylabel('Palavra')
    
    # Tendência semanal (média móvel de 7 dias)
    df['semana'] = df['timestamp'].dt.isocalendar().week
    semanal = df.groupby(['semana', 'keyword']).size().unstack(fill_value=0)
    
    for palavra in top5:
        if palavra in semanal.columns:
            axes[1,0].plot(semanal.index, semanal[palavra].rolling(3, min_periods=1).mean(), 
                          label=palavra, linewidth=2)
    
    axes[1,0].set_xlabel('Semana')
    axes[1,0].set_ylabel('Média Móvel (3 semanas)')
    axes[1,0].set_title('Tendência Semanal - Top 5 Palavras')
    axes[1,0].legend()
    
    # Boxplot por hora
    df_hora_box = df[df['keyword'].isin(top5)]
    data_box = [df_hora_box[df_hora_box['keyword'] == p]['hora'].values for p in top5]
    bp = axes[1,1].boxplot(data_box, labels=top5, patch_artist=True)
    for patch, color in zip(bp['boxes'], sns.color_palette("husl", 5)):
        patch.set_facecolor(color)
    axes[1,1].set_xlabel('Palavra')
    axes[1,1].set_ylabel('Hora do Dia')
    axes[1,1].set_title('Distribuição Horária por Palavra')
    
    plt.tight_layout()
    plt.savefig('02_analise_temporal.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("✓ Gráfico salvo: 02_analise_temporal.png")

analise_temporal(df)

# ============================================
# 4. REDE DE CO-OCORRÊNCIA
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
    
    # Adicionar arestas
    for (p1, p2), peso in co_ocorrencias.items():
        if peso >= 1:
            G.add_edge(p1, p2, weight=peso)
    
    print(f"Rede: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas")
    return G

def visualizar_rede(G, max_nodes=50):
    """Visualiza a rede de co-ocorrência"""
    # Filtrar nós mais conectados
    if G.number_of_nodes() > max_nodes:
        degrees = dict(G.degree())
        top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:max_nodes]
        G = G.subgraph(top_nodes)
    
    # Calcular comunidades
    communities_generator = community.greedy_modularity_communities(G)
    comunidades = {node: i for i, com in enumerate(communities_generator) for node in com}
    
    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Figura
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Nós
    node_sizes = [G.nodes[n].get('weight', 1) * 20 for n in G.nodes()]
    node_colors = [comunidades[n] for n in G.nodes()]
    
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, 
                           cmap='tab20', alpha=0.8, ax=ax)
    
    # Arestas
    edge_weights = [G.edges[e].get('weight', 1) for e in G.edges()]
    edge_widths = [w / max(edge_weights) * 3 for w in edge_weights]
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.3, edge_color='gray', ax=ax)
    
    # Labels
    labels = {n: n for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold', ax=ax)
    
    ax.set_title(f'Rede de Co-ocorrência de Palavras Reservadas\n({G.number_of_nodes()} nós, {G.number_of_edges()} arestas)', 
                 fontsize=14, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('03_rede_coocorrencia.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("✓ Gráfico salvo: 03_rede_coocorrencia.png")

# Construir e visualizar rede
G = construir_rede_coocorrencia(df, window=3)
visualizar_rede(G, max_nodes=40)

# ============================================
# 5. MATRIZ DE CO-OCORRÊNCIA (HEATMAP)
# ============================================

def matriz_coocorrencia(df, top_n=20):
    """Cria heatmap da matriz de co-ocorrência"""
    # Selecionar top N palavras
    top_palavras = df['keyword'].value_counts().head(top_n).index.tolist()
    
    # Criar matriz de adjacência
    matriz = pd.DataFrame(0, index=top_palavras, columns=top_palavras)
    
    for arquivo in df['file'].unique():
        palavras = df[df['file'] == arquivo]['keyword'].tolist()
        
        for i in range(len(palavras)):
            for j in range(i+1, min(i+3, len(palavras))):
                if palavras[i] in top_palavras and palavras[j] in top_palavras:
                    if palavras[i] != palavras[j]:
                        matriz.loc[palavras[i], palavras[j]] += 1
                        matriz.loc[palavras[j], palavras[i]] += 1
    
    # Heatmap
    fig, ax = plt.subplots(figsize=(14, 12))
    
    mask = np.triu(np.ones_like(matriz, dtype=bool))
    sns.heatmap(matriz, mask=mask, annot=True, fmt='d', cmap='YlOrRd', 
                square=True, linewidths=0.5, ax=ax,
                cbar_kws={'label': 'Frequência de Co-ocorrência'})
    
    ax.set_title(f'Matriz de Co-ocorrência (Top {top_n} Palavras)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Palavra', fontsize=12)
    ax.set_ylabel('Palavra', fontsize=12)
    
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig('04_matriz_coocorrencia.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("✓ Gráfico salvo: 04_matriz_coocorrencia.png")

matriz_coocorrencia(df, top_n=20)

# ============================================
# 6. ANÁLISE DE CENTRALIDADE
# ============================================

def analise_centralidade(G):
    """Calcula e visualiza métricas de centralidade"""
    # Calcular métricas
    degree_cent = dict(G.degree())
    betweenness_cent = nx.betweenness_centrality(G)
    closeness_cent = nx.closeness_centrality(G)
    eigenvector_cent = nx.eigenvector_centrality(G, max_iter=1000)
    
    # DataFrame com resultados
    cent_df = pd.DataFrame({
        'palavra': list(G.nodes()),
        'grau': [degree_cent[n] for n in G.nodes()],
        'betweenness': [betweenness_cent[n] for n in G.nodes()],
        'closeness': [closeness_cent[n] for n in G.nodes()],
        'eigenvector': [eigenvector_cent[n] for n in G.nodes()]
    }).sort_values('grau', ascending=False)
    
    # Gráfico
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Centralidade de Grau
    top_grau = cent_df.head(15)
    axes[0,0].barh(range(len(top_grau)), top_grau['grau'].values, color='steelblue')
    axes[0,0].set_yticks(range(len(top_grau)))
    axes[0,0].set_yticklabels(top_grau['palavra'])
    axes[0,0].set_xlabel('Centralidade de Grau')
    axes[0,0].set_title('Top 15 - Centralidade de Grau')
    axes[0,0].invert_yaxis()
    
    # Betweenness
    top_between = cent_df.nlargest(15, 'betweenness')
    axes[0,1].barh(range(len(top_between)), top_between['betweenness'].values, color='coral')
    axes[0,1].set_yticks(range(len(top_between)))
    axes[0,1].set_yticklabels(top_between['palavra'])
    axes[0,1].set_xlabel('Betweenness Centrality')
    axes[0,1].set_title('Top 15 - Betweenness Centrality')
    axes[0,1].invert_yaxis()
    
    # Closeness
    top_close = cent_df.nlargest(15, 'closeness')
    axes[1,0].barh(range(len(top_close)), top_close['closeness'].values, color='forestgreen')
    axes[1,0].set_yticks(range(len(top_close)))
    axes[1,0].set_yticklabels(top_close['palavra'])
    axes[1,0].set_xlabel('Closeness Centrality')
    axes[1,0].set_title('Top 15 - Closeness Centrality')
    axes[1,0].invert_yaxis()
    
    # Eigenvector
    top_eigen = cent_df.nlargest(15, 'eigenvector')
    axes[1,1].barh(range(len(top_eigen)), top_eigen['eigenvector'].values, color='purple')
    axes[1,1].set_yticks(range(len(top_eigen)))
    axes[1,1].set_yticklabels(top_eigen['palavra'])
    axes[1,1].set_xlabel('Eigenvector Centrality')
    axes[1,1].set_title('Top 15 - Eigenvector Centrality')
    axes[1,1].invert_yaxis()
    
    plt.tight_layout()
    plt.savefig('05_centralidade.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("\n📊 TOP 10 PALAVRAS POR CENTRALIDADE DE GRAU:")
    print(cent_df.head(10).to_string(index=False))
    
    return cent_df

cent_df = analise_centralidade(G)

# ============================================
# 7. GRÁFICO DE BURST (PALAVRAS EMERGENTES)
# ============================================

def grafico_burst(df, periodo='M'):
    """Identifica palavras com aumento súbito de frequência"""
    # Agrupar por período
    if periodo == 'D':
        df['periodo'] = df['timestamp'].dt.date
    elif periodo == 'W':
        df['periodo'] = df['timestamp'].dt.to_period('W')
    else:
        df['periodo'] = df['timestamp'].dt.to_period('M')
    
    # Calcular frequência por período
    freq_periodo = df.groupby(['periodo', 'keyword']).size().reset_index(name='count')
    
    # Para cada palavra, calcular taxa de crescimento
    palavras_emergentes = []
    
    for palavra in df['keyword'].unique():
        dados_palavra = freq_periodo[freq_periodo['keyword'] == palavra].sort_values('periodo')
        if len(dados_palavra) >= 3:
            # Calcular crescimento percentual
            growth = dados_palavra['count'].pct_change().fillna(0)
            max_growth = growth.max()
            if max_growth > 1.0:  # Crescimento > 100%
                palavras_emergentes.append((palavra, max_growth))
    
    palavras_emergentes = sorted(palavras_emergentes, key=lambda x: x[1], reverse=True)[:15]
    
    if palavras_emergentes:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        palavras, crescimentos = zip(*palavras_emergentes)
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(palavras)))
        
        bars = ax.barh(range(len(palavras)), crescimentos, color=colors)
        ax.set_yticks(range(len(palavras)))
        ax.set_yticklabels(palavras)
        ax.set_xlabel('Taxa de Crescimento Máxima (%)')
        ax.set_title(f'Palavras com Maior Pico de Crescimento\n(Período: {periodo})')
        
        # Adicionar valores
        for i, (bar, val) in enumerate(zip(bars, crescimentos)):
            ax.text(val + 0.05, i, f'{val*100:.0f}%', va='center')
        
        plt.tight_layout()
        plt.savefig('06_palavras_emergentes.png', dpi=150, bbox_inches='tight')
        plt.show()
        print("✓ Gráfico salvo: 06_palavras_emergentes.png")
    else:
        print("Nenhuma palavra com crescimento significativo encontrada")

grafico_burst(df, periodo='W')

# ============================================
# 8. GRÁFICO DE PARALLEL COORDINATES
# ============================================

def parallel_coordinates(df):
    """Visualização multidimensional de palavras"""
    # Agrupar métricas por palavra
    metrics = df.groupby('keyword').agg({
        'keyword': 'count',
        'line': 'mean',
        'hora': 'mean'
    }).rename(columns={'keyword': 'frequencia'})
    
    metrics['freq_normalizada'] = (metrics['frequencia'] - metrics['frequencia'].min()) / (metrics['frequencia'].max() - metrics['frequencia'].min())
    metrics['linha_media'] = (metrics['line'] - metrics['line'].min()) / (metrics['line'].max() - metrics['line'].min())
    metrics['hora_media'] = (metrics['hora'] - metrics['hora'].min()) / (metrics['hora'].max() - metrics['hora'].min())
    
    metrics_top = metrics.nlargest(30, 'frequencia')
    
    from pandas.plotting import parallel_coordinates
    
    fig, ax = plt.subplots(figsize=(14, 8))
    parallel_coordinates(metrics_top.reset_index(), 'index', 
                        cols=['freq_normalizada', 'linha_media', 'hora_media'],
                        ax=ax, color=plt.cm.tab20(range(len(metrics_top))))
    
    ax.set_title('Parallel Coordinates - Perfil das Palavras Mais Frequentes')
    ax.set_xticklabels(['Frequência', 'Linha Média', 'Hora Média'])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('07_parallel_coordinates.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("✓ Gráfico salvo: 07_parallel_coordinates.png")

parallel_coordinates(df)

# ============================================
# 9. RELATÓRIO FINAL
# ============================================

def gerar_relatorio(df, G, cent_df):
    """Gera relatório completo em formato texto e HTML"""
    
    # Relatório em texto
    with open('relatorio_analise.txt', 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("RELATÓRIO DE ANÁLISE DE PALAVRAS RESERVADAS JAVASCRIPT\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Data da análise: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("RESUMO GERAL:\n")
        f.write("-"*40 + "\n")
        f.write(f"Total de logs analisados: {len(df)}\n")
        f.write(f"Palavras reservadas únicas: {df['keyword'].nunique()}\n")
        f.write(f"Arquivos analisados: {df['file'].nunique()}\n")
        f.write(f"Período: {df['timestamp'].min()} até {df['timestamp'].max()}\n\n")
        
        f.write("TOP 10 PALAVRAS:\n")
        f.write("-"*40 + "\n")
        for palavra, count in df['keyword'].value_counts().head(10).items():
            f.write(f"  {palavra}: {count}\n")
        
        f.write("\nMÉTRICAS DE REDE:\n")
        f.write("-"*40 + "\n")
        f.write(f"Nós (palavras): {G.number_of_nodes()}\n")
        f.write(f"Arestas (conexões): {G.number_of_edges()}\n")
        f.write(f"Densidade: {nx.density(G):.4f}\n")
        
        f.write("\nTOP 10 POR CENTRALIDADE:\n")
        f.write("-"*40 + "\n")
        for _, row in cent_df.head(10).iterrows():
            f.write(f"  {row['palavra']}: grau={row['grau']:.0f}, betweenness={row['betweenness']:.4f}\n")
    
    print("\n✅ Relatório salvo: relatorio_analise.txt")
    
    # Relatório HTML (se plotly estiver disponível)
    if PLOTLY_AVAILABLE:
        gerar_relatorio_html(df)
    
    # Salvar dados processados
    df.to_csv('dados_processados.csv', index=False)
    cent_df.to_csv('centralidade_palavras.csv', index=False)
    print("✅ Dados salvos: dados_processados.csv, centralidade_palavras.csv")

def gerar_relatorio_html(df):
    """Gera relatório HTML interativo"""
    top20 = df['keyword'].value_counts().head(20).reset_index()
    top20.columns = ['Palavra', 'Frequência']
    
    fig = make_subplots(rows=2, cols=2, subplot_titles=('Top 20 Palavras', 'Ocorrências por Hora', 'Distribuição por Arquivo', 'Heatmap Temporal'))
    
    # Top 20 palavras
    fig.add_trace(go.Bar(x=top20['Frequência'], y=top20['Palavra'], orientation='h', marker_color='steelblue'), row=1, col=1)
    
    # Ocorrências por hora
    hora_counts = df['hora'].value_counts().sort_index()
    fig.add_trace(go.Scatter(x=hora_counts.index, y=hora_counts.values, mode='lines+markers', line=dict(color='coral')), row=1, col=2)
    
    # Top arquivos
    top_files = df['file'].value_counts().head(10)
    fig.add_trace(go.Pie(labels=top_files.index, values=top_files.values), row=2, col=1)
    
    # Heatmap temporal
    pivot_hora = pd.crosstab(df['hora'], df['keyword'].apply(lambda x: x[:10]))
    fig.add_trace(go.Heatmap(z=pivot_hora.values.T, x=pivot_hora.index, y=pivot_hora.columns, colorscale='Viridis'), row=2, col=2)
    
    fig.update_layout(height=800, title_text="Dashboard Interativo - Análise de Palavras Reservadas")
    fig.write_html('dashboard_interativo.html')
    print("✅ Dashboard HTML salvo: dashboard_interativo.html")

# Gerar relatório final
gerar_relatorio(df, G, cent_df)

# ============================================
# 10. EXIBIR RESUMO NO CONSOLE
# ============================================

print("\n" + "="*60)
print("✅ ANÁLISE CONCLUÍDA!")
print("="*60)
print("\n📁 ARQUIVOS GERADOS:")
print("   - 01_analise_descritiva.png")
print("   - 02_analise_temporal.png")
print("   - 03_rede_coocorrencia.png")
print("   - 04_matriz_coocorrencia.png")
print("   - 05_centralidade.png")
print("   - 06_palavras_emergentes.png")
print("   - 07_parallel_coordinates.png")
print("   - relatorio_analise.txt")
print("   - dados_processados.csv")
print("   - centralidade_palavras.csv")
if PLOTLY_AVAILABLE:
    print("   - dashboard_interativo.html")

print("\n📊 RESUMO DOS DADOS:")
print(f"   Total de registros: {len(df)}")
print(f"   Palavras únicas: {df['keyword'].nunique()}")
print(f"   Arquivos: {df['file'].nunique()}")
print(f"   Período: {df['timestamp'].min().date()} a {df['timestamp'].max().date()}")

print("\n🏆 TOP 10 PALAVRAS RESERVADAS:")
for i, (palavra, count) in enumerate(df['keyword'].value_counts().head(10).items(), 1):
    bar = "█" * int(count / df['keyword'].value_counts().head(10).max() * 30)
    print(f"   {i:2d}. {palavra:12s} {bar} {count}")
