library(ggplot2)
library(dplyr)
library(tidyr)

# Dados fornecidos
dados <- data.frame(
  instituicao = c("PUCPR", "UTFPR", "IFTO", "IFAM", "IFTO", "IFTO", "IFAM", 
                  "IFAM", "IFAM", "UEA", "TJTO", "IFPA", "UTFPR", "PUCPR"),
  ferramenta = c("Não", "Não", "Não", "Não", "Não", "Não", "Não", "Não", 
                 "Não", "Não", "Sim", "Não", "Não", "Sim"),
  opiniao = c("Indiferente", "Concordo parcialmente", "Indiferente", "Concordo totalmente",
              "Concordo totalmente", "Concordo parcialmente", "Concordo parcialmente",
              "Concordo parcialmente", "Indiferente", "Concordo parcialmente", 
              "Concordo totalmente", "Concordo parcialmente", "Concordo totalmente", 
              "Concordo totalmente")
)

# Criar tabela de frequência
tabela <- dados %>%
  count(instituicao, ferramenta, opiniao) %>%
  complete(instituicao, ferramenta, opiniao, fill = list(n = 0))

# Definir ordem para as opiniões (Likert)
ordem_opiniao <- c("Discordo", "Indiferente", "Concordo parcialmente", "Concordo totalmente")
tabela$opiniao <- factor(tabela$opiniao, levels = ordem_opiniao)

# Criar o heatmap
ggplot(tabela, aes(x = ferramenta, y = opiniao, fill = n)) +
  geom_tile(color = "white", size = 0.8) +
  geom_text(aes(label = ifelse(n > 0, n, "")), color = "white", size = 4, fontface = "bold") +
  facet_wrap(~instituicao, ncol = 3) +
  scale_fill_gradient(low = "#6baed6", high = "#084594", name = "Número de\nrespostas") +
  labs(title = "Uso de Ferramentas de Log no Apoio ao Ensino de Programação",
       subtitle = "Análise por instituição e tipo de resposta",
       x = "Usa ferramenta de log?",
       y = "Opinião sobre o uso de ferramentas",
       caption = "Fonte: Dados coletados da pesquisa") +
  theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 16),
    plot.subtitle = element_text(hjust = 0.5, size = 12),
    axis.text.x = element_text(angle = 0, vjust = 0.5),
    strip.text = element_text(face = "bold"),
    panel.grid = element_blank(),
    legend.position = "right"
  )

