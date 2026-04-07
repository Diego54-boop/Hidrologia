##Script para calcular estadisticas basicas (promedio, maximo , minimo) de los registros 
# de caudales diarios de la base de datos Andrea

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Direccion local de la serie hidrologica obtenida desde la plataforma andrea
dfd = pd.read_excel("/content/DatosSerie (7).xlsx")

##Reordenamiento de columnas para tener la serie diaria en una dimension
lista_df = []
for j in dfd.groupby(by ='Año', as_index =True).count().index:
    df_1 = dfd[dfd["Año"]== j][np.delete(dfd.columns, [0,1])]
    for i in df_1.columns:
        lista_df.append(df_1[i])

DF_ = pd.concat(lista_df, axis = 0, ignore_index =True)

#Lista de años del registro total de caudales diarios
años = dfd["Año"].unique()

##Creacion de objecto dataframe a partir de la serie pandas obtenida del reordenamiento 
#anterior
g = pd.DataFrame(DF_)
g["fecha"] = pd.date_range(start = '01-01-'+str(años[0]), periods = len(g))
g.rename(columns = {0:"Caudal diario"}, inplace =True)


##Calculo de estadisticas (maximo , minimo , promedio, desviacion standart),
# en el ejemplo se calcula el caudal diario maximo

g["fecha"]= g["fecha"].apply(lambda x:str(x))
año = g["fecha"].str.split("-", expand =True)[0]
g["Año"] = año
lista_caudal_max =list()
for i in [j for j in set(g["Año"])]:
  caudal_max = g[g["Año"]== i]["Caudal diario"].max()
  lista_caudal_max.append(caudal_max)

#Creacion del objeto dataframe a partir de caudales maximos y sus años correspondientes
df_caudal_max = pd.DataFrame({"año":[j for j in set(g["Año"])],"Caudal_max":lista_caudal_max }).sort_values(["año"], ascending =True)

##Visualizacion final en grafico de barras
fig , ax = plt.subplots(figsize =(20,10))
df_caudal_max.plot(ax=ax,kind ='bar', x ='año', y = 'Caudal_max')