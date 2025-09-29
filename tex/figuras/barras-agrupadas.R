library(ggplot2)
library(dplyr)
library(tidyr)

# Dados fornecidos
dados <- data.frame(
  instituicao = c("PUCPR", "UTFPR", "IFTO", "IFAM", "IFTO", "IFTO", "IFAM", 
                  "IFAM", "IFAM", "UEA", "TJTO", "IFPA", "UTFPR", "PUCPR"),
  pergunta1 = c("Concordo totalmente", "Concordo parcialmente", "Concordo parcialmente", 
                "Concordo totalmente", "Concordo totalmente", "Concordo totalmente", 
                "Concordo totalmente", "Concordo parcialmente", "Indiferente", 
                "Indiferente", "Concordo parcialmente", "Concordo parcialmente", 
                "Concordo totalmente", "Concordo totalmente"),
  pergunta2 = c("Discordo parcialmente", "Concordo parcialmente", "Concordo parcialmente", 
                "Concordo parcialmente", "Concordo parcialmente", "Concordo totalmente", 
                "Concordo totalmente", "Concordo parcialmente", "Concordo totalmente", 
                "Concordo parcialmente", "Concordo parcialmente", "Indiferente", 
                "Concordo parcialmente", "Discordo totalmente")
)

# Transformar para formato longo
dados_long <- dados %>%
  pivot_longer(cols = c(pergunta1, pergunta2), 
               names_to = "pergunta", 
               values_to = "resposta")

# Definir ordem das respostas
ordem_respostas <- c("Discordo totalmente", "Discordo parcialmente", "Indiferente", 
                     "Concordo parcialmente", "Concordo totalmente")

dados_long$resposta <- factor(dados_long$resposta, levels = ordem_respostas)

# Gráfico de barras agrupadas
ggplot(dados_long, aes(x = instituicao, fill = resposta)) +
  geom_bar(position = "fill") +
  facet_wrap(~pergunta, ncol = 1, 
             labeller = labeller(pergunta = c(
               "pergunta1" = "Dataset a partir de logs",
               "pergunta2" = "Correção automatizada de código"
             ))) +
  scale_fill_manual(values = c("Discordo totalmente" = "#d73027", 
                               "Discordo parcialmente" = "#fc8d59", 
                               "Indiferente" = "#fee090", 
                               "Concordo parcialmente" = "#91bfdb", 
                               "Concordo totalmente" = "#4575b4")) +
  scale_y_continuous(labels = scales::percent) +
  labs(title = "Opiniões sobre Dataset de Logs e Correção Automatizada",
       x = "Instituição", 
       y = "Proporção de Respostas",
       fill = "Resposta") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
