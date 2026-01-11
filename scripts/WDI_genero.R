# Script R: participación laboral por género (Banco Mundial)
# Requiere paquetes: install.packages(c("WDI", "dplyr"))

library(WDI)
library(dplyr)

# Códigos de indicadores del Banco Mundial
# SL.TLF.CACT.FE.ZS = Female labor force participation (% of female population ages 15+)
# SL.TLF.CACT.MA.ZS = Male labor force participation (% of male population ages 15+)

datos <- WDI(
  indicator = c("SL.TLF.CACT.FE.ZS", "SL.TLF.CACT.MA.ZS"),
  country = c("ES", "FR", "DE", "IT", "PT", "EUU"),  # España, Francia, Alemania, Italia, Portugal, EE.UU.
  start = 2000,
  end = 2023,
  extra = FALSE
)

# Renombrar columnas para claridad
datos_limpios <- datos %>%
  rename(
    pais = country,
    año = year,
    participacion_mujeres = SL.TLF.CACT.FE.ZS,
    participacion_hombres = SL.TLF.CACT.MA.ZS
  ) %>%
  select(pais, año, participacion_mujeres, participacion_hombres) %>%
  filter(!is.na(participacion_mujeres) | !is.na(participacion_hombres))

# Guardar en CSV
write.csv(datos_limpios, "/home/panda/Documents/udima/TFM/datos_csv_github/datos/participacion_laboral_genero.csv", row.names = FALSE)

cat("✅ CSV guardado: participacion_laboral_genero.csv\n")