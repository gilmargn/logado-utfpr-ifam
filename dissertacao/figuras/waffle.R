library(ggplot2)
library(dplyr)

# Dados fornecidos
dados <- data.frame(
  instituicao = c("PUCPR", "UTFPR", "IFTO", "IFAM", "IFTO", "IFTO", "IFAM", 
                  "IFAM", "IFAM", "UEA", "TJTO", "IFPA", "UTFPR", "PUCPR"),
  pergunta1 = c("Indiferente", "Concordo parcialmente", "Indiferente", "Concordo totalmente",
                "Concordo totalmente", "Concordo totalmente", "Discordo totalmente",
                "Discordo parcialmente", "Discordo parcialmente", "Concordo parcialmente", 
                "Concordo totalmente", "Concordo parcialmente", "Concordo totalmente", 
                "Concordo totalmente"),
  pergunta2 = c("Indiferente", "Discordo parcialmente", "Concordo parcialmente", "Concordo totalmente",
                "Concordo totalmente", "Concordo totalmente", "Concordo parcialmente",
                "Concordo parcialmente", "Indiferente", "Concordo parcialmente", 
                "Concordo totalmente", "Concordo parcialmente", "Concordo totalmente", 
                "Concordo totalmente")
)

# 1. WAFFLE CHART PARA PERGUNTA 1
# Contar as respostas para a pergunta 1
contagem_p1 <- table(dados$pergunta1)
print(contagem_p1)

# Expandir para 100 quadrados (proporcionalmente)
vals_p1 <- c(
  "Concordo totalmente" = 7,
  "Concordo parcialmente" = 4,
  "Indiferente" = 2,
  "Discordo parcialmente" = 2,
  "Discordo totalmente" = 1
)

# Criar dataframe expandido
df_p1 <- data.frame(
  val = rep(names(vals_p1), times = vals_p1),
  id = seq_len(sum(vals_p1))
)

# Calcular colunas e linhas (5x5 grid)
df_p1$col <- ((df_p1$id-1) %% 5) + 1
df_p1$row <- floor((df_p1$id-1)/5) + 1

# Definir ordem das respostas e cores
ordem_respostas <- c("Discordo totalmente", "Discordo parcialmente", "Indiferente", 
                     "Concordo parcialmente", "Concordo totalmente")
cores <- c("Discordo totalmente" = "#d73027", 
           "Discordo parcialmente" = "#fc8d59", 
           "Indiferente" = "#fee090", 
           "Concordo parcialmente" = "#91bfdb", 
           "Concordo totalmente" = "#4575b4")

df_p1$val <- factor(df_p1$val, levels = ordem_respostas)

# Plotar waffle chart para pergunta 1
ggplot(df_p1, aes(x = col, y = -row, fill = val)) +
  geom_tile(color = "white", size = 1) + 
  coord_equal() + 
  scale_fill_manual(values = cores, name = "Resposta:") +
  labs(title = "O uso de ferramentas de logs pode ajudar a tomar decisões\npara melhorar o rendimento e evitar a desistência?",
       subtitle = "Cada quadrado representa uma resposta (Total: 16 respostas)") +
  theme_void() +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 14),
    plot.subtitle = element_text(hjust = 0.5, size = 12),
    legend.position = "bottom"
  )

# 2. WAFFLE CHART PARA PERGUNTA 2
# Contar as respostas para a pergunta 2
contagem_p2 <- table(dados$pergunta2)
print(contagem_p2)

# Expandir para 100 quadrados (proporcionalmente)
vals_p2 <- c(
  "Concordo totalmente" = 9,
  "Concordo parcialmente" = 4,
  "Indiferente" = 2,
  "Discordo parcialmente" = 1
)

# Criar dataframe expandido
df_p2 <- data.frame(
  val = rep(names(vals_p2), times = vals_p2),
  id = seq_len(sum(vals_p2))
)

# Calcular colunas e linhas (4x4 grid)
df_p2$col <- ((df_p2$id-1) %% 4) + 1
df_p2$row <- floor((df_p2$id-1)/4) + 1

df_p2$val <- factor(df_p2$val, levels = ordem_respostas)

# Plotar waffle chart para pergunta 2
ggplot(df_p2, aes(x = col, y = -row, fill = val)) +
  geom_tile(color = "white", size = 1) + 
  coord_equal() + 
  scale_fill_manual(values = cores, name = "Resposta:") +
  labs(title = "O uso de ferramentas de logs pode auxiliar no ensino de programação?",
       subtitle = "Cada quadrado representa uma resposta (Total: 16 respostas)") +
  theme_void() +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 14),
    plot.subtitle = element_text(hjust = 0.5, size = 12),
    legend.position = "bottom"
  )

# 3. WAFFLE CHART COMBINADO (DUAS PERGUNTAS)
# Juntar os dados das duas perguntas
df_combined <- bind_rows(
  df_p1 %>% mutate(pergunta = "Tomada de decisões"),
  df_p2 %>% mutate(pergunta = "Auxílio no ensino")
)

# Ajustar coordenadas para visualização combinada
df_combined <- df_combined %>%
  group_by(pergunta) %>%
  mutate(
    new_id = row_number(),
    new_col = ((new_id-1) %% 8) + 1,
    new_row = floor((new_id-1)/8) + 1
  ) %>%
  ungroup()

# Plotar waffle chart combinado
ggplot(df_combined, aes(x = new_col, y = -new_row, fill = val)) +
  geom_tile(color = "white", size = 0.8) + 
  coord_equal() + 
  facet_wrap(~pergunta, ncol = 2) +
  scale_fill_manual(values = cores, name = "Resposta:") +
  labs(title = "Comparação das Opiniões sobre Uso de Ferramentas de Log",
       subtitle = "Cada quadrado representa uma resposta") +
  theme_void() +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 16),
    plot.subtitle = element_text(hjust = 0.5, size = 12),
    strip.text = element_text(face = "bold", size = 11),
    legend.position = "bottom"
  )

# 4. WAFFLE CHART PROPORCIONAL (100 QUADRADOS = 100%)
# Calcular proporções para a pergunta 1
proporcoes_p1 <- round(vals_p1 / sum(vals_p1) * 100)
df_prop_p1 <- data.frame(
  val = rep(names(proporcoes_p1), times = proporcoes_p1),
  id = seq_len(sum(proporcoes_p1))
)

# Calcular colunas e linhas (10x10 grid)
df_prop_p1$col <- ((df_prop_p1$id-1) %% 10) + 1
df_prop_p1$row <- floor((df_prop_p1$id-1)/10) + 1
df_prop_p1$val <- factor(df_prop_p1$val, levels = ordem_respostas)

# Plotar waffle chart proporcional
ggplot(df_prop_p1, aes(x = col, y = -row, fill = val)) +
  geom_tile(color = "white", size = 0.5) + 
  coord_equal() + 
  scale_fill_manual(values = cores, name = "Resposta:") +
  labs(title = "Distribuição Proporcional das Respostas",
       subtitle = "Tomada de decisões com ferramentas de logs (100 quadrados = 100%)",
       caption = "Cada quadrado representa 1% do total de respostas") +
  theme_void() +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 16),
    plot.subtitle = element_text(hjust = 0.5, size = 12),
    legend.position = "bottom"
  )

