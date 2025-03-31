rm(list=ls(all.names = T))

library(stargazer)
library(plm)
library(AER)

data("Fatalities", package = "AER")

Fatalities <- Fatalities

str(Fatalities)

# Definición del ratio de la fatalidad
Fatalities$fatal_rate <- Fatalities$fatal/Fatalities$pop*10000
# summary(Fatalities$fatal_rate)

unique(Fatalities$state)

Fatalities$drinkage <- as.numeric(Fatalities$drinkage)

Fatalities <- Fatalities %>% 
    select(drinkage,
           everything())

# Discretizar la edad mínima para beber:
Fatalities$drinkagec <- cut(Fatalities$drinkage,
                           breaks = 18:22,
                           include.lowest = T,
                           right = F)

Fatalities <- Fatalities %>% 
    select(drinkage,
           drinkagec,
           everything())

# Panel equilibrado: Se dispone de todas las observaciones
#  Panel no equilibarado: No se dispone de todas las observaciones
# Establecer la edad mínima para ingerir alcohol [21,22] como nivel de referencia
Fatalities$drinkagec <- relevel(Fatalities$drinkagec,"[21:22]")

# Cárcelo o servicio comunitario obligatorio:

Fatalities$punish <- with(Fatalities,
                          factor(jail=="yes" | service =="yes",
                                 labels = c("no", "yes")))

str(Fatalities)


# Crear un objeto de datos de panel
panel_data <- pdata.frame(Fatalities, 
                          index = c("state", 
                                    "year"))

# Modelo de MCO
modelo_1 <- plm(fatal_rate ~ 
                  beertax,
                  data = Fatalities,
                  model = "pooling")

# Modelo de efectos fijos
# model_ef <- plm(fatal_rate ~ 
#                   spirits +
#                   unemp + 
#                   income + 
#                   emppop + 
#                   beertax + 
#                   baptist + 
#                   mormon + 
#                   drinkage + 
#                   dry + 
#                   youngdrivers +
#                   miles + 
#                   breath + 
#                   jail + 
#                   service + 
#                   nfatal + 
#                   sfatal + 
#                   fatal1517 + 
#                   nfatal1517 + 
#                   fatal1820 + 
#                   nfatal1820 + 
#                   fatal2124 + 
#                   nfatal2124 + 
#                   afatal + 
#                   pop + 
#                   pop1517 + 
#                   pop1820 + 
#                   pop2124 + 
#                   milestot + 
#                   unempus + 
#                   emppopus + 
#                   gsp,
#                 data = Fatalities,
#                 model = "within")

modelo_2 <- plm(fatal_rate ~ 
                beertax + 
                state +
                gsp,
                data = Fatalities,
                model = "within")

modelo_3 <- plm(fatal_rate ~ 
                beertax +
                state +
                year,
                data = Fatalities,
                index = c("state","year"),
                efect="twoways",
                model = "within")


# Modelo de efectos aleatorios
modelo_4 <- plm(fatal_rate ~ 
                beertax +
                state +
                year +
                drinkagec +
                punish +
                miles +
                unemp +
                log(income),
                model = "within",
                index = c("state","year"),
                efect="twoways",
                data = Fatalities)

modelo_4

modelo_5 <- plm(fatal_rate ~ 
                beertax +
                state +
                year +
                drinkagec +
                punish +
                miles,
                data = Fatalities,
                model = "within",
                index = c("state","year"),
                efect="twoways")

modelo_6 <- plm(fatal_rate ~ 
                beertax +
                state +
                year +
                drinkage +
                punish +
                miles +
                unemp +
                log(income),
                data = Fatalities,
                model = "within",
                index = c("state","year"),
                efect="twoways")

# Periodos

Fatal_1982_1988 <- Fatalities[with(Fatalities, year==1982 | year==1988),]

modelo_7 <- plm(fatal_rate ~ 
                beertax +
                year +
                drinkagec +
                punish +
                miles +
                unemp +
                log(income),
                data = Fatal_1982_1988,
                model = "within",
                index = c("state","year"),
                efect="twoways")

modelo_7

library(sandwich)

modelos <- list(modelo_1,
                modelo_2,
                modelo_3,
                modelo_4,
                modelo_5,
                modelo_6,
                modelo_7)

cluster <- lapply(modelos, function(x) {
  sqrt(diag(vcovHC(x, type="HC1")))
  
})

stargazer(modelo_1,
          modelo_2,
          modelo_3,
          modelo_4,
          modelo_5,
          modelo_6,
          modelo_6,
          modelo_7,
          digits = 3,
          header= F,
          df = F,
          align = T,
          type="text",
          column.labels = c("Modelo_1",
                            "Modelo_2",
                            "Modelo_3",
                            "Modelo_4",
                            "Modelo_5",
                            "Modelo_6",
                            "Modelo_7"),
          title = "Comparación de modelos",
          model.names = F)


# Generar la tabla:

stargazer(modelos, 
          type="text",
          title="Análisis de regresión del efecto de las leyes sobre conducción en estado de embriaguez sobre las muertes en accidentes de tráfico",
          df=F,
          dep.var.labels = "Tasa de mortalidad por accidentes de tráfico (muertes por cada 10.000 hab)",
          se=cluster,
          digits = 3)


summary(Fatalities$fatal_rate)
library(car)

linearHypothesis(modelo_4,
                 test="F",
                 c("drinkagec[18,19)=0",
                   "drinkagec[19,20)=0",
                   "drinkagec[20,21)=0"),
                 vcov.=vcovHC, 
                 type="HC1")

linearHypothesis(modelo_5,
                 test="F",
                 c("drinkagec[18,19)=0",
                   "drinkagec[19,20)=0",
                   "drinkagec[20,21)=0"),
                 vcov.=vcovHC, 
                 type="HC1")



