import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import gumbel_r, kstest
from pandas import DataFrame

path = "/content/drive/MyDrive/TOPOGRAFIA_SANTO_DOMINGO/precipitacion maxima 24.xlsx"
data = pd.read_excel(path)

#########################DATOS

#Tiempo de retorno de 1000 años
tiempo_retorno = [100]

#Duracion de tormenta en minutos cuando el numero de intervalos es par
duracion = [15,45,75,105,135,165,195,225,255,285,305,335,365,395]

#Duracion de tormenta en horas
TIEMPO = [i/60 for i in (duracion)]

#########################Determinacion del ajuste estadistico bajo la prueba de kolmogorov

#Segun la prueba de kolmogorov-smirnov se acepta la distribucion de gumbel con una
#probabilidad del 30% mucho mayor a nivel de significancia de 5%
datos = np.flip(data["Pp"].sort_values(ascending =False).reset_index(drop =True))
parametros = gumbel_r.fit(datos)
D, p_value = kstest(datos , "gumbel_r", args = parametros)


######################## Calculo las curvas IDF para un periodo de retorno de 1000 años
intensidad_list = list()
for tr in tiempo_retorno:
  kt1 = -0.45004099
  kt2 = -0.7796968
  kt3 = np.log(tr/(tr-1))
  kt4 = np.log(kt3)
  kt = kt1+kt2*kt4
  for d, y in zip((range(len(duracion))),(range(len(TIEMPO)))):
    def pmax1(x):
      p1=x*((duracion[d]/1440)**0.25)/TIEMPO[y]
      return p1
    pd =data['Pp'].apply(pmax1)
    d = pd.to_numpy()
    promedio =d.mean()
    desv = d.std()
    intensidad = promedio + desv*kt
    intensidad_list.append(intensidad)
    intensidad_array = np.array(intensidad_list).tolist()


## Calculo de las intesidades segun el metodo de factores de frecuencia mediante el
## Rejuste matricial de la lista array , para darle la longitud de lista de "duracion",
## y el numero de listas equivalente al numero de periodos de retorno
intensidades_maximas = np.array(intensidad_array).reshape(len(tiempo_retorno),len(duracion))


## Logaritmos de la lista de las duraciones y las intensidades maximas
X = np.log(TIEMPO)
Y = np.log(intensidades_maximas[0])

#Calculo de Objeto que contiene la pendiente y el termino independiente de la ecuacion de regresion lineal
X = np.log(TIEMPO)
Y = np.log(intensidades_maximas[0])
lreg = stats.linregress(X,Y)
#Duracion de la tormenta
duracion_= TIEMPO

#Intensidad instantanea calculada(mm/hr) a partir de la duracion en horas
Intensida_d = round(2.71828**(lreg.intercept.tolist()),2)*(duracion_)**round(lreg.slope,2)

#Calculo precipitacion acumulada(mm)
p_cum = Intensida_d*duracion_

########################Calculo de hietograma de tormenta segun el metodo de bloques alternos para numero de datos par

#Calculo de la precipitacion incremental
#p_acum = pd.DataFrame(data = p_cum[1:len(p_cum)], columns=["X"])
p_acum = DataFrame({"X": p_cum[1:len(p_cum)]})
#p_acum["X_reducido"] = pd.DataFrame(data = p_cum[0:len(p_cum)-1], columns=["X_"])["X_"]
p_acum["X_reducido"]= DataFrame({"X_":p_cum[0:len(p_cum)-1]})["X_"]
p_acum["diferencia"] = p_acum["X"] - p_acum["X_reducido"]
p_acum.sort_values(["diferencia"], ascending =False , inplace =True)
p_final = np.insert(p_acum["diferencia"].tolist(), [0], p_cum[0])

#objeto Dataframe creado a partir del la precipitacion incremental
df = DataFrame({"Pp" :p_final})


##Reordenamiento del la precipitacion incremental (el maximo valor se encontrara en la posicion de la mediana) y creacion de la lista
# de indices con el orden adecuado para el hietograma

lista_index = np.concatenate([np.flip([(i*2)+1 for i in range(len(p_final))][0:int(len(p_final)/2)]),[i*2 for i in range(len(p_final))][0:int((len(p_final)/2))]])

#Hietograma final con la indexacion correcta
#hietograma_final = DataFrame(data = [df["Pp"].loc[[i]].values for i in lista_index], columns = ['intensidad'])
hietograma_final = DataFrame({"intensidad": [df["Pp"].loc[[i]].values[0] for i in lista_index]})


#################################Visualizacion del ajuste estadistico, curvas IDF y el Hietograma de tormenta

fig ,(ax1,ax2,ax3) =plt.subplots(1,3,figsize =(10,6))

ax1.plot(np.flip(data["Pp"].sort_values(ascending =False).reset_index(drop =True)),[i/(i+1) for i in range(1,len(data)+1)])
ax1.plot(np.flip(data["Pp"].sort_values(ascending =False).reset_index(drop =True)),gumbel_r.cdf(np.flip(data["Pp"].sort_values(ascending =False).reset_index(drop =True))))
ax1.set_title("Weibull vs gumbel"+","+"P_value ="+str(round(p_value,2)), fontsize = 10)

plt.style.use('ggplot')
ax2.plot(TIEMPO, intensidades_maximas[0])
ax2.set_title("CURVA IDF T = "+str(tiempo_retorno[0])+" "+"años", fontsize =10)
ax2.set_xlabel("Tiempo(hrs)")
ax2.set_ylabel("Intensidad(mm/h)")

ax1.set_xlabel("Precip(mm)")
ax3.bar(TIEMPO , hietograma_final["intensidad"])
ax3.set_title("Hietograma T ="+str(tiempo_retorno[0])+" "+"años", fontsize = 10)
ax3.set_ylabel("Duracion(Hrs)")
