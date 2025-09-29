library(ggplot2)
library(dplyr)
library(tidyr)

# Dados fornecidos
dados <- data.frame(
  instituicao = c("PUCPR", "UTFPR", "IFTO", "IFAM", "IFTO", "IFTO", "IFAM", 
                  "IFAM", "IFAM", "UEA", "TJTO", "IFPA", "UTFPR", "PUCPR"),
  opiniao_plugins = c("Concordo parcialmente", "Discordo parcialmente", "Concordo parcialmente", 
                      "Concordo parcialmente", "Concordo totalmente", "Indiferente", 
                      "Concordo parcialmente", "Concordo totalmente", "Discordo parcialmente", 
                      "Concordo parcialmente", "Concordo parcialmente", "Concordo parcialmente", 
                      "Concordo parcialmente", "Indiferente"),
  usaria_plugin = c("Sim", "Sim", "Não", "Sim", "Sim", "Sim", "Sim", 
                    "Sim", "Não", "Sim", "Sim", "Sim", "", "Sim")
)

# Limpar dados (remover resposta vazia)
dados <- dados[dados$usaria_plugin != "", ]

# Definir ordem para as opiniões
ordem_opiniao <- c("Discordo totalmente", "Discordo parcialmente", "Indiferente", 
                   "Concordo parcialmente", "Concordo totalmente")

dados$opiniao_plugins <- factor(dados$opiniao_plugins, levels = ordem_opiniao)

# Criar tabela de frequência
tabela <- dados %>%
  count(instituicao, opiniao_plugins, usaria_plugin) %>%
  group_by(instituicao, opiniao_plugins) %>%
  mutate(total_instituicao = sum(n)) %>%
  ungroup()

# Gráfico de pontos com tamanho proporcional
ggplot(tabela, aes(x = instituicao, y = opiniao_plugins, size = n, color = usaria_plugin)) +
  geom_point(alpha = 0.8) +
  scale_size_continuous(range = c(4, 12), name = "Número de\nrespostas") +
  scale_color_manual(values = c("Não" = "#e41a1c", "Sim" = "#377eb8"), 
                     name = "Usaria plugin?") +
  labs(title = "Opinião sobre Plugins e Intenção de Uso por Instituição",
       subtitle = "Tamanho do ponto representa o número de respostas",
       x = "Instituição", 
       y = "Opinião sobre plugins no ensino de algoritmos",
       caption = "Fonte: Dados coletados da pesquisa") +
  theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 16),
    plot.subtitle = element_text(hjust = 0.5, size = 12, margin = margin(b = 15)),
    axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1),
    axis.text.y = element_text(),
    panel.grid.major = element_line(color = "grey90", linewidth = 0.2),
    legend.position = "right",
    plot.margin = margin(15, 15, 15, 15)
  ) +
  guides(color = guide_legend(override.aes = list(size = 6)))
