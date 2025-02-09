
library(srvyr)
library(tidyverse)

dci_provincial <- f1_personas %>%
  group_by(prov) %>%  # Agrupar por provincia
  summarise(
    factor_expansion = sum(fexp[dcronica == 1], na.rm = TRUE),  # Total ponderado por fexp solo para dcronica == 1
    ninios_dci = sum(dcronica == 1 & f1_s1_3_1 < 5, na.rm = TRUE),  # Número total de niños con DCI menores de 5 años
    total_ninios = sum(f1_s1_3_1 < 5, na.rm = TRUE),  # Total de niños menores de 5 años
    dci_provincial = round((ninios_dci / total_ninios) * 100, 2),  # Proporción en porcentaje
    .groups = "drop"  # Eliminar agrupamiento posterior
  )

# Convertir los datos a un diseño de encuesta
f1_survey <- f1_personas %>%
  as_survey_design(ids = 1,  # Sin conglomerados
                   weights = fexp)  # Usar el factor de expansión

# Calcular la prevalencia de desnutrición crónica por provincia
prevalencia_dci_prov <- f1_survey %>%
  filter(f1_s1_3_1 < 5) %>%  # Filtrar niños menores de 5 años
  group_by(prov) %>%  # Agrupar por provincia
  summarise(
    dci = round(survey_mean(dcronica == 1, na.rm = TRUE) * 100, 2),  # Proporción ponderada redondeada
    total_dci = round(survey_total(dcronica == 1, na.rm = TRUE), 2),  # Total ponderado redondeado
    total_ninios = round(survey_total(na.rm = TRUE), 2)  # Total ponderado redondeado
  )


View(prevalencia_dci_prov)
