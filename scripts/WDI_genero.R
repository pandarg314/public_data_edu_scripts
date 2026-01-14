# Script R: participación laboral por género (Banco Mundial)
# Descarga WDI, limpia y guarda CSV en /datos (ruta relativa al repo)

library(rstudioapi)
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
setwd("..")

library(WDI)
library(dplyr)

# Indicadores (World Bank)
# SL.TLF.CACT.FE.ZS = Female labor force participation (% of female population ages 15+)
# SL.TLF.CACT.MA.ZS = Male labor force participation (% of male population ages 15+)

dir.create("datos", showWarnings = FALSE, recursive = TRUE)

datos <- WDI(
  indicator = c("SL.TLF.CACT.FE.ZS", "SL.TLF.CACT.MA.ZS"),
  country   = c("ES", "FR", "DE", "IT", "PT", "EUU"),
  start     = 2000,
  end       = 2023,
  extra     = FALSE
)

datos_limpios <- datos %>%
  rename(
    pais = country,
    año  = year,
    participacion_mujeres = SL.TLF.CACT.FE.ZS,
    participacion_hombres = SL.TLF.CACT.MA.ZS
  ) %>%
  select(pais, año, participacion_mujeres, participacion_hombres) %>%
  filter(!is.na(participacion_mujeres) | !is.na(participacion_hombres))

out <- "datos/participacion_laboral_genero.csv"
write.csv(datos_limpios, out, row.names = FALSE)
cat("✅ CSV guardado en:", out, "\n")
