# Exemplo de análise complementar antes do VOSviewer
def analyze_patterns(analyzer):
    df = analyzer.get_dataframe()
    
    # Padrões sequenciais comuns
    print("Padrões de sequência comuns:")
    for file_name in df['file_origem'].unique()[:5]:
        file_logs = df[df['file_origem'] == file_name].sort_values('timestamp')
        sequence = ' → '.join(file_logs['keyword'].head(10))
        print(f"{file_name}: {sequence}")
    
    # Correlações temporais
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    hourly_patterns = df.groupby(['hour', 'keyword']).size().unstack()
    print("\nPadrões horários:")
    print(hourly_patterns[['if', 'else', 'while']].head(10))
