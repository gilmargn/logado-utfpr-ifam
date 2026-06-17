import glob
import pandas as pd
import json
from pathlib import Path

# ============================================
# PASSO 1: Localizar todos os arquivos JSON
# ============================================

# Altere para o caminho dos seus arquivos JSON
caminho_json = '/home/gilmar/Documents/algoritmos/logado-utfpr-ifam/logado-students/repos_logado/**/*.json'

# Encontra todos os arquivos JSON recursivamente
arquivos_json = glob.glob(caminho_json, recursive=True)

print(f"Encontrados {len(arquivos_json)} arquivos JSON")
for arquivo in arquivos_json[:500]:  # Mostra os 5 primeiros
    print(f"  - {arquivo}")

# ============================================
# PASSO 2: Ler cada arquivo JSON e armazenar
# ============================================

frames = []  # Lista para guardar cada DataFrame

for arquivo in arquivos_json:
    try:
        # Lê o arquivo JSON
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        # Converte para DataFrame
        if isinstance(dados, list):  # Se for lista de logs
            df_temp = pd.DataFrame(dados)
        elif isinstance(dados, dict):  # Se for dicionário
            df_temp = pd.DataFrame([dados])
        else:
            print(f"Formato não reconhecido: {arquivo}")
            continue
        
        # Adiciona coluna com o nome do arquivo de origem
        df_temp['arquivo_origem'] = Path(arquivo).name
        df_temp['repositorio'] = Path(arquivo).parent.name
        
        frames.append(df_temp)
        print(f"✓ Lido: {Path(arquivo).name} - {len(df_temp)} registros")
        
    except Exception as e:
        print(f"✗ Erro ao ler {arquivo}: {e}")


# ============================================
# PASSO 3: Concatenar todos em um único DataFrame
# ============================================

if frames:
    df = pd.concat(frames, ignore_index=True)
    print(f"\n✅ Total de registros: {len(df)}")
    print(f"✅ Colunas: {df.columns.tolist()}")
else:
    print("Nenhum arquivo JSON foi carregado!")
    exit()

# ============================================
# PASSO 4: VISUALIZAR O AGRUPAMENTO
# ============================================

print("\n" + "="*60)
print("VISUALIZAÇÃO DO AGRUPAMENTO")
print("="*60)

# 1. VISÃO GERAL DOS DADOS
print("\n📊 PRIMEIRAS LINHAS:")
print(df.head(10))

print("\n📊 INFORMAÇÕES DO DATAFRAME:")
print(df.info())

print("\n📊 ESTATÍSTICAS BÁSICAS:")
print(df.describe())

# 2. AGRUPAMENTO POR PALAVRA RESERVADA
print("\n" + "="*60)
print("AGRUPAMENTO POR PALAVRA RESERVADA")
print("="*60)

# Verifica qual coluna tem as palavras (pode ser 'keyword' ou 'palavra_reservada')
coluna_palavra = None
for col in ['keyword', 'palavra_reservada', 'palavra', 'word']:
    if col in df.columns:
        coluna_palavra = col
        break

if coluna_palavra:
    agrupado_por_palavra = df.groupby(coluna_palavra).size().sort_values(ascending=False)
    print(f"\nAgrupado por {coluna_palavra}:")
    print(agrupado_por_palavra.head(20))
else:
    print(f"Coluna de palavras não encontrada. Colunas disponíveis: {df.columns.tolist()}")

# 3. AGRUPAMENTO POR ARQUIVO DE ORIGEM
print("\n" + "="*60)
print("AGRUPAMENTO POR ARQUIVO DE ORIGEM")
print("="*60)

if 'arquivo_origem' in df.columns:
    agrupado_por_arquivo = df.groupby('arquivo_origem').size().sort_values(ascending=False)
    print(agrupado_por_arquivo.head(10))

# 4. AGRUPAMENTO POR REPOSITÓRIO
print("\n" + "="*60)
print("AGRUPAMENTO POR REPOSITÓRIO")
print("="*60)

if 'repositorio' in df.columns:
    agrupado_por_repositorio = df.groupby('repositorio').size().sort_values(ascending=False)
    print(agrupado_por_repositorio)

# 5. AGRUPAMENTO POR LINHA (onde mais ocorre)
print("\n" + "="*60)
print("LINHAS COM MAIS OCORRÊNCIAS")
print("="*60)

if 'line' in df.columns:
    agrupado_por_linha = df.groupby('line').size().sort_values(ascending=False).head(10)
    print(agrupado_por_linha)

# 6. AGRUPAMENTO POR TIMESTAMP (se existir)
print("\n" + "="*60)
print("AGRUPAMENTO POR DATA/HORA")
print("="*60)

if 'timestamp' in df.columns:
    # Converte timestamp para datetime
    df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
    
    # Por data
    df['data'] = df['timestamp_dt'].dt.date
    agrupado_por_data = df.groupby('data').size()
    print(f"\nPor data: {len(agrupado_por_data)} dias diferentes")
    print(agrupado_por_data.head(10))
    
    # Por hora do dia
    df['hora'] = df['timestamp_dt'].dt.hour
    agrupado_por_hora = df.groupby('hora').size()
    print(f"\nPor hora do dia:")
    print(agrupado_por_hora)

try:
    import matplotlib.pyplot as plt
    
    print("\n" + "="*60)
    print("GERANDO GRÁFICOS...")
    print("="*60)
    
    # Configurar gráficos
    plt.rcParams['figure.figsize'] = (12, 6)
    
    # Gráfico 1: Top 15 palavras reservadas
    if coluna_palavra:
        plt.subplot(2, 2, 1)
        top_palavras = df[coluna_palavra].value_counts().head(15)
        top_palavras.plot(kind='bar')
        plt.title('Top 15 Palavras Reservadas')
        plt.xlabel('Palavra')
        plt.ylabel('Frequência')
        plt.xticks(rotation=45)
    
    # Gráfico 2: Distribuição por arquivo (top 10)
    if 'arquivo_origem' in df.columns:
        plt.subplot(2, 2, 2)
        top_arquivos = df['arquivo_origem'].value_counts().head(10)
        top_arquivos.plot(kind='bar', color='green')
        plt.title('Top 10 Arquivos com Mais Ocorrências')
        plt.xlabel('Arquivo')
        plt.ylabel('Frequência')
        plt.xticks(rotation=45)
    
    # Gráfico 3: Distribuição por repositório
    #if 'repositorio' in df.columns:
    #    plt.subplot(2, 2, 3)
    #    df['repositorio'].value_counts().plot(kind='pie', autopct='%1.1f%%')
    #    plt.title('Distribuição por Repositório')
    #    plt.ylabel('')
    
    # Gráfico 4: Ocorrências por hora (se tiver timestamp)
    if 'timestamp' in df.columns and 'hora' in df.columns:
        plt.subplot(2, 2, 4)
        ocorrencias_por_hora = df.groupby('hora').size()
        ocorrencias_por_hora.plot(kind='line', marker='o')
        plt.title('Ocorrências por Hora do Dia')
        plt.xlabel('Hora')
        plt.ylabel('Número de Ocorrências')
        plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('analise_agrupamento.png')
    plt.show()
    
    print("✓ Gráficos salvos em 'analise_agrupamento.png'")
    
except ImportError:
    print("⚠ Matplotlib não instalado. Instale com: pip install matplotlib")

# ============================================
# PASSO 6: EXPORTAR RESULTADOS AGRUPADOS
# ============================================

print("\n" + "="*60)
print("EXPORTANDO RESULTADOS")
print("="*60)

# Exporta o DataFrame completo
df.to_csv('todos_logs_agrupados.csv', index=False)
print("✓ Exportado: todos_logs_agrupados.csv")

# Exporta agrupamento por palavra
if coluna_palavra:
    agrupado_por_palavra.to_csv('agrupamento_por_palavra.csv')
    print("✓ Exportado: agrupamento_por_palavra.csv")

# Exporta agrupamento por arquivo
if 'arquivo_origem' in df.columns:
    agrupado_por_arquivo.to_csv('agrupamento_por_arquivo.csv')
    print("✓ Exportado: agrupamento_por_arquivo.csv")

# Exporta em JSON (formato aninhado para VOSviewer)
resultado_agrupado = {
    'total_registros': len(df),
    'palavras_unicas': int(df[coluna_palavra].nunique()) if coluna_palavra else 0,
    'arquivos_unicos': int(df['arquivo_origem'].nunique()) if 'arquivo_origem' in df.columns else 0,
    'repositorios_unicos': int(df['repositorio'].nunique()) if 'repositorio' in df.columns else 0,
    'agrupamento_por_palavra': agrupado_por_palavra.to_dict() if coluna_palavra else {},
    'agrupamento_por_arquivo': agrupado_por_arquivo.to_dict() if 'arquivo_origem' in df.columns else {}
}

with open('resumo_agrupamento.json', 'w', encoding='utf-8') as f:
    json.dump(resultado_agrupado, f, indent=2, ensure_ascii=False)

print("✓ Exportado: resumo_agrupamento.json")

print("\n✅ ANÁLISE CONCLUÍDA!")
print("📁 Arquivos gerados:")
print("   - todos_logs_agrupados.csv")
print("   - agrupamento_por_palavra.csv")
print("   - agrupamento_por_arquivo.csv")
print("   - resumo_agrupamento.json")
print("   - analise_agrupamento.png (se matplotlib instalado)")
