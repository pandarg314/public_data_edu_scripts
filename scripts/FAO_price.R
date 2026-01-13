# FAO FFPI (XLSX) → descarga, chequeo rápido y gráficos en pantalla
u <- "https://www.fao.org/media/docs/worldfoodsituationlibraries/default-document-library/food_price_indices_data_jan3.xlsx?sfvrsn=63809b16_99"
dir.create("datos", showWarnings=FALSE, recursive=TRUE); f <- "datos/fao_ffpi.xlsx"
download.file(u, f, mode="wb", quiet=TRUE)

library(readxl)
d <- suppressMessages(read_excel(f, sheet="Indices_Monthly_Nominal", skip=3))[, 1:7]
names(d) <- c("date","ffpi","meat","dairy","cereals","oils","sugar");

d$date <- if (inherits(d$date, "Date")) d$date else as.Date(d$date, origin="1899-12-30")

# Resumen del dato (estructura, rango temporal, NAs)
cat("FAO Food Price Index (monthly nominal)\n",
    "Rows:", nrow(d), " Cols:", ncol(d), "\n",
    "Range:", min(d$date), "→", max(d$date), "\n",
    "Total NAs:", sum(is.na(d)), "\n", sep="")

# Aviso: ¿es el mismo tipo de dato que las capturas del README?
ok <- all(c("ffpi","meat","dairy","cereals","oils","sugar") %in% names(d)) && min(d$date, na.rm=TRUE) <= as.Date("1990-01-01")
message(if (ok) "OK: parece el FFPI mensual nominal (tipo de dato del README)." else
  "AVISO: el formato/hoja/columnas no coinciden con el FFPI mensual nominal esperado.")

# Gráfico 1: índice general
plot(d$date, d$ffpi, type="l",
     xlab="Date", ylab="Index (2014–2016=100)",
     main="FAO Food Price Index (FFPI)")

# Gráfico 2: índice + componentes
matplot(d$date, as.matrix(d[,-1]), type="l", lty=1,
        xlab="Date", ylab="Index",
        main="FFPI and components")
legend("topleft", names(d)[-1], lty=1, col=1:6, cex=.8, bg="white")
