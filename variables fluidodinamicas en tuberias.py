##Librerias necesarias
import math
import numpy as np
from matplotlib import pyplot as plt

## Calculo de la perdida de carga en tuberias de diferentes diametros , longitudes , y regimenes de flujo de distintos numeros
# de Reynolds segun la ecuacion de Darcy weischbach


##### DATOS
#Diametros comerciales en pulgadas
diametros_comerciales = [    "1/2\"",    "3/4\"",    "1\"",    "1 1/4\"",    "1 1/2\"",    "2\"",    "2 1/2\"",    "3\"",    "4\"",    "6\""]

#Diametros comerciales en metros
diametros_m = [    0.0127,    0.01905,    0.0254,    0.03175,    0.0381,    0.0508,    0.0635,    0.0762,    0.1016,    0.1524]

#Lista de longitudes
Longitud = np.linspace(100,1000,10)

#Lista de Numeros de Reynolds
RE_list = np.linspace(100,10000,10)


##### CALCULOS

##Calculo de los coeficiente de friccion para una superficie hidraulicamente lisa, segun
# el numero de reynolds haciendo uso del metodo de resolucion de ecuaciones no lineales newton Raphson
lista_fi = list()
for Re_i in RE_list:
  def newton_raphson(xo,tol,n):
    F = lambda f: 1/math.sqrt(f) - 2*math.log10(Re_i*math.sqrt(f))+ 0.8
    dF =  lambda f : -0.5 * f**(-1.5) - 1/(f * math.log(10))
    x = xo
    for k in range(n):
      x = x -(F(x)/dF(x))
      if abs(F(x))<tol:
        return x
    return x
  lista_fi.append(newton_raphson(0.03, 0.0005, 13))

##Calculo de la perdida de carga de la tuberia en funcion de la longitud de la tuberia
# y su diametro, segun la ecuacion de perdida de carga para un coeficiente de friccion
# variable en funcion del numero de reynolds

for k in Longitud:
  fig, (ax1,ax2) =plt.subplots(1,2, figsize =(15,5))
  #fig, ax = plt.subplots(figsize =(10,6))
  for i , j  in zip(diametros_m, diametros_comerciales):


    ##Visualizacion de la perdida de carga en funcion del numero de Reynolds
    RE_list = np.linspace(100,10000,10)
    hi= np.array(lista_fi)*(k/i)*((((RE_list*1e-6)/i)**2)/(2*9.81))
    ax1.plot(RE_list, hi, label = j)
    ax1.set_xlabel("Reynolds")
    ax1.set_ylabel("Perdida de carga")
    ax1.set_title("Perdida de carga vs Nro_Reynolds"+" "+"L ="+str(k)+"m")
    ax1.grid(True)
    ax1.legend()


    ##Visualizacion de la perdida de carga en funcion de caudal en m3/s
    Q_list = RE_list*diametros_m*math.pi*0.25*1e-6
    hi_1 = np.array(lista_fi)*(k/i)*(((RE_list*1e-6)/(i))**2)/(2*9.81)
    ax2.plot(Q_list, hi_1, label = j)
    ax2.set_xlabel("Caudal m3/s")
    ax2.set_ylabel("Perdida de carga")
    ax2.set_title("Perdida de carga vs Caudal"+" "+"L ="+str(k)+"m")
    ax2.grid(True)
    ax2.legend()