# ============================================
# ANÁLISE DE REDES DE PALAVRAS RESERVADAS EM R
# ============================================

# 1. CARREGAR PACOTES
# ============================================
pacotes <- c(
  "tidyverse",      # Manipulação de dados
  "jsonlite",       # Leitura de JSON
  "igraph",         # Análise de redes
  "ggraph",         # Visualização de redes
  "tidygraph",      # Manipulação de redes
  "widyr",          # Co-ocorrência
  "factoextra",     # Visualização de clusters
  "cluster",        # Algoritmos de clustering
  "plotly",         # Gráficos interativos
  "heatmaply",      # Heatmaps interativos
  "circlize",       # Diagramas circulares
  "networkD3"       # Redes interativas
)

# Instalar pacotes que não tiver
for (p in pacotes) {
  if (!require(p, character.only = TRUE)) {
    install.packages(p)
    library(p, character.only = TRUE)
  }
}

2. CARREGAR DADOS
# ============================================
cat("========================================\n")
cat("CARREGANDO DADOS\n")
cat("========================================\n\n")

caminho_base <- "/home/gilmar/Documents/algoritmos/logado-utfpr-ifam/logado-students"

# Função para ler todos os JSONs
ler_logs <- function(caminho) {
  arquivos <- list.files(caminho, pattern = "\\.json$", 
                         recursive = TRUE, full.names = TRUE)
  
  todos_logs <- list()
  
  for (arq in arquivos) {
    dados <- fromJSON(arq)
    if (is.list(dados) && length(dados) > 0) {
      if (is.data.frame(dados)) {
        todos_logs <- append(todos_logs, split(dados, 1:nrow(dados)))
      } else if (!is.null(dados[[1]]$keyword)) {
        for (log in dados) {
          todos_logs[[length(todos_logs) + 1]] <- log
        }
      } else if (!is.null(dados$keyword)) {
        todos_logs[[length(todos_logs) + 1]] <- dados
      }
    }
  }
  
  df <- bind_rows(todos_logs)
  return(df)
}

# Carregar dados
df <- ler_logs(caminho_base)
cat("Total de registros:", nrow(df), "\n")
cat("Palavras únicas:", length(unique(df$keyword)), "\n")
cat("Arquivos analisados:", length(unique(df$file)), "\n")
cat("Período:", min(df$timestamp), "até", max(df$timestamp), "\n")

# 3. ANÁLISE DESCRITIVA BÁSICA
# ============================================
cat("\n========================================\n")
cat("ANÁLISE DESCRITIVA\n")
cat("========================================\n")

# Top palavras
top_palavras <- df %>%
  count(keyword, sort = TRUE) %>%
  head(20)

cat("\nTOP 20 PALAVRAS RESERVADAS:\n")
print(top_palavras)

# Gráfico de barras
ggplot(top_palavras, aes(x = reorder(keyword, n), y = n, fill = n)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  scale_fill_gradient(low = "lightblue", high = "darkblue") +
  labs(title = "Top 20 Palavras Reservadas JavaScript",
       x = "Palavra", y = "Frequência") +
  theme_minimal() +
  theme(legend.position = "none")

ggsave("top_palavras.png", width = 10, height = 6)

# 4. MATRIZ DE CO-OCORRÊNCIA
# ============================================
cat("\n========================================\n")
cat("CONSTRUINDO REDE DE CO-OCORRÊNCIA\n")
cat("========================================\n")

# Criar pares de palavras que aparecem juntas no mesmo arquivo
co_occ <- df %>%
  group_by(file) %>%
  summarise(palavras = list(keyword)) %>%
  unnest(cols = c(palavras)) %>%
  group_by(file) %>%
  summarise(pares = if(length(palavras) > 1) {
    combn(palavras, 2, simplify = FALSE)
  } else {
    list()
  }) %>%
  unnest(pares, keep_empty = FALSE) %>%
  mutate(p1 = map_chr(pares, 1),
         p2 = map_chr(pares, 2)) %>%
  count(p1, p2, sort = TRUE)

cat("Total de pares únicos:", nrow(co_occ), "\n")

# Matriz de co-ocorrência
matriz_cooc <- co_occ %>%
  pivot_wider(names_from = p2, values_from = n, values_fill = 0) %>%
  column_to_rownames("p1")

# Heatmap interativo
heatmaply(matriz_cooc[1:20, 1:20],
          main = "Matriz de Co-ocorrência (Top 20 palavras)",
          xlab = "Palavra", ylab = "Palavra",
          fontsize_row = 10, fontsize_col = 10)

# 5. CRIAÇÃO DO GRAFO
# ============================================
cat("\n========================================\n")
cat("CRIANDO GRAFO\n")
cat("========================================\n")

# Criar grafo a partir dos pares
grafo <- graph_from_data_frame(co_occ, directed = FALSE)

# Adicionar atributos
V(grafo)$frequencia <- degree(grafo, mode = "total")
V(grafo)$centralidade <- betweenness(grafo, directed = FALSE)
V(grafo)$closeness <- closeness(grafo)

cat("Nós (palavras):", vcount(grafo), "\n")
cat("Arestas (conexões):", ecount(grafo), "\n")
cat("Densidade:", edge_density(grafo), "\n")

# 6. ANÁLISE DE CLUSTERS
# ============================================
cat("\n========================================\n")
cat("ANÁLISE DE CLUSTERS\n")
cat("========================================\n")

# Detectar comunidades
comunidades <- cluster_louvain(grafo)
V(grafo)$cluster <- membership(comunidades)

cat("Número de clusters:", max(membership(comunidades)), "\n")
cat("Modularidade:", modularity(comunidades), "\n")

# Resumo dos clusters
cluster_summary <- data.frame(
  cluster = 1:max(membership(comunidades)),
  tamanho = sizes(comunidades),
  palavras = sapply(1:max(membership(comunidades)), function(x) {
    paste(names(membership(comunidades)[membership(comunidades) == x])[1:5], collapse = ", ")
  })
)

print(cluster_summary)

# 7. VISUALIZAÇÕES
# ============================================
cat("\n========================================\n")
cat("GERANDO VISUALIZAÇÕES\n")
cat("========================================\n")

# Visualização 1: Rede completa
set.seed(123)
layout_rede <- layout_with_fr(grafo)

png("rede_completa.png", width = 1200, height = 800)
plot(grafo,
     layout = layout_rede,
     vertex.size = log(V(grafo)$frequencia) * 3,
     vertex.color = rainbow(max(membership(comunidades)))[V(grafo)$cluster],
     vertex.label = V(grafo)$name,
     vertex.label.cex = 0.7,
     vertex.label.dist = 1,
     edge.width = E(grafo)$weight / max(E(grafo)$weight) * 3,
     edge.color = "gray70",
     main = "Rede de Co-ocorrência de Palavras Reservadas JavaScript")
legend("topleft", legend = 1:max(membership(comunidades)), 
       col = rainbow(max(membership(comunidades))), pch = 19, 
       title = "Clusters")
dev.off()

# Visualização 2: Rede interativa (html)
library(networkD3)

# Converter para formato D3
d3_network <- igraph_to_networkD3(grafo, group = V(grafo)$cluster)

# Criar mapa de cores
cores <- c("#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", 
           "#DDA0DD", "#98D8C8", "#F7B731", "#FF9999", "#66CCCC")

# Rede interativa
rede_interativa <- forceNetwork(
  Links = d3_network$links,
  Nodes = d3_network$nodes,
  Source = "source",
  Target = "target",
  Value = "value",
  NodeID = "name",
  Group = "group",
  opacity = 0.9,
  zoom = TRUE,
  legend = TRUE,
  colourScale = JS(paste0('d3.scaleOrdinal().range(["', paste(cores[1:max(membership(comunidades))], collapse = '", "'), '"])')),
  fontSize = 14,
  linkWidth = JS("function(d) { return Math.sqrt(d.value); }"),
  radiusCalculation = JS("Math.sqrt(d.nodesize) * 3")
)

saveNetwork(rede_interativa, "rede_interativa.html")

# Visualização 3: Diagrama circular
library(circlize)

# Selecionar top conexões
top_conexoes <- co_occ %>%
  arrange(desc(n)) %>%
  head(50)

# Criar diagrama circular
chordDiagram(top_conexoes[, 1:3], 
             transparency = 0.5,
             annotationTrack = "grid",
             preAllocateTracks = 1)
title("Diagrama Circular - Top 50 Co-ocorrências")

# Visualização 4: Rede com ggraph (ggplot2)
library(ggraph)

ggraph(grafo, layout = "fr") +
  geom_edge_link(aes(width = weight, alpha = weight), color = "gray70") +
  geom_node_point(aes(size = frequencia, color = factor(cluster))) +
  geom_node_text(aes(label = name), repel = TRUE, size = 3) +
  scale_edge_width(range = c(0.1, 2)) +
  scale_size(range = c(3, 15)) +
  theme_void() +
  labs(title = "Rede de Palavras Reservadas JavaScript",
       subtitle = paste(vcount(grafo), "palavras,", ecount(grafo), "conexões")) +
  theme(plot.title = element_text(hjust = 0.5, size = 16))

ggsave("rede_ggraph.png", width = 14, height = 10)

# 8. ANÁLISE DE CENTRALIDADE
# ============================================
cat("\n========================================\n")
cat("ANÁLISE DE CENTRALIDADE\n")
cat("========================================\n")

# Calcular métricas de centralidade
centralidade <- data.frame(
  palavra = V(grafo)$name,
  grau = degree(grafo, mode = "total"),
  betweenness = betweenness(grafo, directed = FALSE),
  closeness = closeness(grafo),
  eigen = eigen_centrality(grafo)$vector,
  cluster = V(grafo)$cluster
) %>%
  arrange(desc(grau))

cat("\nTOP 10 PALAVRAS POR CENTRALIDADE DE GRAU:\n")
print(head(centralidade, 10))

# Visualizar centralidade
centralidade %>%
  head(20) %>%
  ggplot(aes(x = reorder(palavra, grau), y = grau, fill = grau)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  scale_fill_gradient(low = "lightblue", high = "darkred") +
  labs(title = "Top 20 Palavras por Centralidade de Grau",
       x = "Palavra", y = "Centralidade") +
  theme_minimal()

ggsave("centralidade.png", width = 10, height = 6)

# 9. ANÁLISE TEMPORAL
# ============================================
cat("\n========================================\n")
cat("ANÁLISE TEMPORAL\n")
cat("========================================\n")

# Converter timestamp
df <- df %>%
  mutate(timestamp_dt = as.POSIXct(timestamp),
         data = as.Date(timestamp_dt),
         hora = hour(timestamp_dt),
         dia_semana = wday(timestamp_dt, label = TRUE),
         mes = month(timestamp_dt, label = TRUE))

# Evolução temporal
evolucao <- df %>%
  group_by(data, keyword) %>%
  summarise(n = n(), .groups = "drop") %>%
  group_by(data) %>%
  mutate(total_dia = sum(n)) %>%
  ungroup()

# Gráfico de evolução (top palavras)
top5 <- names(sort(table(df$keyword), decreasing = TRUE))[1:5]

evolucao %>%
  filter(keyword %in% top5) %>%
  ggplot(aes(x = data, y = n, color = keyword)) +
  geom_line(size = 1) +
  geom_point(size = 2) +
  labs(title = "Evolução Temporal das Palavras Mais Frequentes",
       x = "Data", y = "Número de Ocorrências") +
  theme_minimal() +
  theme(legend.position = "bottom")

ggsave("evolucao_temporal.png", width = 12, height = 6)

# 10. RELATÓRIO FINAL
# ============================================
cat("\n========================================\n")
cat("GERANDO RELATÓRIO\n")
cat("========================================\n")

# Criar arquivo de relatório
sink("relatorio_analise.txt")

cat("RELATÓRIO DE ANÁLISE DE PALAVRAS RESERVADAS JAVASCRIPT\n")
cat("========================================================\n\n")

cat("DATA DA ANÁLISE:", Sys.Date(), "\n\n")

cat("RESUMO GERAL:\n")
cat("-------------\n")
cat("Total de logs analisados:", nrow(df), "\n")
cat("Palavras reservadas únicas:", length(unique(df$keyword)), "\n")
cat("Arquivos analisados:", length(unique(df$file)), "\n")
cat("Repositórios:", length(unique(df$repositorio)), "\n")
cat("Período:", min(df$timestamp), "até", max(df$timestamp), "\n\n")

cat("TOP 10 PALAVRAS:\n")
cat("----------------\n")
print(top_palavras[1:10, ])

cat("\nMÉTRICAS DE REDE:\n")
cat("-----------------\n")
cat("Nós (palavras):", vcount(grafo), "\n")
cat("Arestas (conexões):", ecount(grafo), "\n")
cat("Densidade:", edge_density(grafo), "\n")
cat("Modularidade:", modularity(comunidades), "\n")
cat("Número de clusters:", max(membership(comunidades)), "\n\n")

cat("TOP 10 POR CENTRALIDADE:\n")
cat("------------------------\n")
print(centralidade[1:10, c("palavra", "grau", "betweenness", "cluster")])

cat("\nCLUSTERS ENCONTRADOS:\n")
cat("---------------------\n")
print(cluster_summary)

sink()

cat("\n✅ ANÁLISE CONCLUÍDA!\n")
cat("📁 Arquivos gerados:\n")
cat("   - top_palavras.png\n")
cat("   - rede_completa.png\n")
cat("   - rede_interativa.html\n")
cat("   - rede_ggraph.png\n")
cat("   - centralidade.png\n")
cat("   - evolucao_temporal.png\n")
cat("   - relatorio_analise.txt\n")

# 11. DASHBOARD INTERATIVO (opcional)
# ============================================
cat("\n========================================\n")
cat("CRIANDO DASHBOARD INTERATIVO\n")
cat("========================================\n")

library(shiny)
library(plotly)

# Salvar dados para o dashboard
saveRDS(df, "dados_logs.rds")
saveRDS(grafo, "grafo_logs.rds")
saveRDS(centralidade, "centralidade.rds")

# Criar dashboard
dashboard_code <- '
library(shiny)
library(plotly)
library(dplyr)
library(ggplot2)

# Carregar dados
df <- readRDS("dados_logs.rds")
centralidade <- readRDS("centralidade.rds")

ui <- fluidPage(
  titlePanel("Dashboard - Análise de Palavras Reservadas JavaScript"),
  
  sidebarLayout(
    sidebarPanel(
      selectInput("palavra", "Selecione uma palavra:",
                  choices = unique(df$keyword)),
      dateRangeInput("periodo", "Período:",
                     start = min(df$timestamp_dt),
                     end = max(df$timestamp_dt))
    ),
    
    mainPanel(
      tabsetPanel(
        tabPanel("Visão Geral", 
                 plotlyOutput("freq_plot"),
                 plotlyOutput("evolucao")),
        tabPanel("Centralidade", 
                 plotlyOutput("centralidade_plot")),
        tabPanel("Detalhes", 
                 tableOutput("detalhes"))
      )
    )
  )
)

server <- function(input, output) {
  output$freq_plot <- renderPlotly({
    df %>%
      count(keyword, sort = TRUE) %>%
      head(20) %>%
      plot_ly(x = ~reorder(keyword, n), y = ~n, type = "bar") %>%
      layout(title = "Frequência das Palavras",
             xaxis = list(title = ""),
             yaxis = list(title = "Frequência"))
  })
  
  output$evolucao <- renderPlotly({
    df %>%
      filter(keyword == input$palavra) %>%
      count(data = as.Date(timestamp_dt)) %>%
      plot_ly(x = ~data, y = ~n, type = "scatter", mode = "lines+markers") %>%
      layout(title = paste("Evolução de", input$palavra),
             xaxis = list(title = "Data"),
             yaxis = list(title = "Ocorrências"))
  })
  
  output$centralidade_plot <- renderPlotly({
    centralidade %>%
      head(20) %>%
      plot_ly(x = ~reorder(palavra, grau), y = ~grau, type = "bar") %>%
      layout(title = "Centralidade de Grau",
             xaxis = list(title = ""),
             yaxis = list(title = "Grau"))
  })
  
  output$detalhes <- renderTable({
    df %>%
      filter(keyword == input$palavra) %>%
      group_by(file, line, coluna) %>%
      summarise(n = n()) %>%
      head(10)
  })
}

shinyApp(ui = ui, server = server)
'

writeLines(dashboard_code, "dashboard.R")

cat("\n✅ Dashboard criado! Execute 'shiny::runApp(\"dashboard.R\")' para visualizar\n")