##Ejecutar esta linea en una celda aparte
import os
os.environ("OPENTOPOGRAPHY_API_KEY")= "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

##Instalacion de librerias para descarga de modelos digitales de elevacion
# y para obtener estadisticas zonales
!pip install bmi_topography
!pip install rasterstats

##Importacion de librerias
import ee
ee.Authenticate()
ee.Initialize(project = 'fit-authority-476815-f4')
import geopandas as gpd
import rasterio as rio
from rasterio.plot import show
from matplotlib import pyplot as plt
import geemap
import pandas as pd
import bmi_topography
from bmi_topography import Topography
from rasterstats import zonal_stats
from pathlib import Path
import numpy as np

##Consulta del nombre de las subcuencas
subcuencas = gpd.read_file("/content/drive/MyDrive/GOOGLE EARTH ENGINE/CURVA HIPSOMETRICA/UniHidroMen_ANA_geogpsperu.shp" )

Alto_madre_de_dios = subcuencas.sort_values(['AREA_KM2'], ascending =False)["Nombre_UH"].reset_index(drop =True)[1]
Alto_madre_de_dios


### NOTA IMPORTANTE :
  #EL CODIGO TIENE COMO ENTRADAS EL NUMERO DE CLASES, Y EL NOMBRE DE LA CUENCA

##Entradas del modelo
nombre_cuenca = 'Cuenca Alto Huallaga'
Numero_clases = 10

##Objetos del cliente
basins = ee.FeatureCollection("projects/fit-authority-476815-f4/assets/UniHidroMen_ANA_geogpsperu")
##Base de datos de modelos digitales de elevacion a nivel mundial
world_strm = ee.Image("NASA/ASTER_GED/AG100_003")

## Shapefile Cuenca Alto Madre de Dios
subbasin = basins.filterMetadata("Nombre_UH", "equals" , nombre_cuenca)
##Raster de la cuenca madre de dios
dem_basin = world_strm.select('elevation').clip(subbasin)


##Visualizacion de la capa raster con geemap
map = geemap.Map()
map.addLayer(dem_basin)
map.centerObject(dem_basin)
map

#Visualizacion de la capa vectorial con geemap
map = geemap.Map()
map.addLayer(subbasin)
map.centerObject(subbasin,10)
map

##Calculo de la altura minima en a partir del calculo de estadisticas
# zonales de la cuenca con el metodo reduceRegion
minimo_valor = dem_basin.select("elevation").reduceRegion(
                                       reducer = ee.Reducer.min(),
                                       geometry = subbasin,
                                       scale = 30,
                                       maxPixels = 1e12
                                       )
##Calculo de la altura maxima en a partir del calculo de estadisticas
# zonales de la cuenca con el metodo reduceRegion
maximo_valor = dem_basin.select("elevation").reduceRegion(
                                       reducer = ee.Reducer.max(),
                                       geometry = subbasin,
                                       scale = 30,
                                       maxPixels = 1e12
                                       )

#Atributos de los estadisticos anteriormente calculados
min = minimo_valor.getInfo()["elevation"]
max = maximo_valor.getInfo()["elevation"]



####################CLASIFICACION DEL RASTER EN FORMATO IMAGE DE GOOGLE EARTH ENGINE

##Calculo de los intervalos igualmente espaciados de la clasificacion
df = pd.DataFrame(data = np.linspace(min, max, Numero_clases), columns = ['A'])
df["B"] =  df.drop([0], axis = 0).reset_index(drop =True)
df.drop([len(df)-1], axis = 0, inplace =True)


##Clasificacion con los metodos gt() y lt(), sobre el objeto modelo digital de elevacion
# creado de la cuenca de interes
lista = list()
for i, j, z in zip(df["A"], df["B"] ,range(1,len(df)+1)):
  dem =  dem_basin.select("elevation")
  c1  = dem.gt(i).And(dem.lt(j)).multiply(z)
  lista.append(c1)

##Recursividad para unir todas las clases con el metodo add()
c_i = lista[0].add(lista[1])
for i in range(2,len(df)):
  c_i = c_i.add(lista[i])

##Vectorizacion o reduccion a vectores del raster clasificado con el metodo
# reduceToVectors
vectors = c_i.addBands(dem_basin).reduceToVectors(
    geometry= subbasin,
    crs= dem_basin.projection(),
    scale=90,
    geometryType='polygon',
    eightConnected=False,
    labelProperty='zone',
    reducer=ee.Reducer.mean(),
)


#Visualizacion del poligono obtenido a partir del raster
map = geemap.Map()
display_image = ee.Image(0).updateMask(0).paint(vectors, '000000', 3 )
map.addLayer(display_image, {"palette":'000000'})
map

##Visualizacion de del raster clasificado
mapa_ = geemap.Map()
mapa_.addLayer(c_i , {"min": 1  , "max":Numero_clases-1, "palette": ["blue","pink","green","orange", "red","black","brown", "yellow","grey"]})
mapa_.centerObject(c_i   )
mapa_


##Exportacion del poligono clasificado hacia una carpeta drive , de la cuenta asociada a google earth engine
export = ee.batch.Export.table.toDrive(
    collection = vectors,
    folder =  "POLS" ,
    description = 'POLIGONOS'+'_'+nombre_cuenca,
    fileFormat = 'SHP')
export.start()


##Poligono clasificado leido desde la carpeta drive que la contiene
poligono_clasificados = gpd.read_file('/content/drive/MyDrive/POLS/POLIGONOS'+'_'+nombre_cuenca+'.shp')


##Disolver el poligono de clasificacion a partir del campo de clasificacion
lista_pol = list()
for i in poligono_clasificados.groupby(by = "zone", as_index = True).count().index:
  geom = poligono_clasificados[poligono_clasificados["zone"]== i]
  lista_pol.append(geom.dissolve(by = 'zone', as_index = True))

multipoligono = pd.concat(lista_pol, axis = 0, ignore_index = False)


### Descarga de modelo digital de elevacion desde la STRM de la nasa
Alto_MDD = gpd.read_file("/content/drive/MyDrive/GOOGLE EARTH ENGINE/CURVA HIPSOMETRICA/UniHidroMen_ANA_geogpsperu.shp")

#Area de interes
region = Alto_MDD[Alto_MDD["Nombre_UH"]==nombre_cuenca]

#Objeto dataframe que representa contiene las coordenadas de extension del area de interes
coord = region.to_crs(4326).bounds.reset_index(drop =True).transpose()[0].sort_values(ascending =True).reset_index(drop =True).loc[[2,3,0,1]].to_numpy()

#Objeto de la clase Topography que contiene las coordendas de la entension , segun los puntos cardinales
params = Topography.DEFAULT.copy()
params["south"] = float(coord[0])
params["north"] = float(coord[1])
params["west"] = float(coord[2])
params["east"] = float(coord[3])

#Metodos para la extraccion del archivo dem
boulder = Topography(**params)
boulder.load()
boulder.da.spatial_ref
boulder.load()
boulder.fetch()


##Disolucion de poligono clasificado obtenido de la vectorizacion (conversion de poligono a multipoligono)
d = gpd.read_file('/content/drive/MyDrive/POLS/POLIGONOS'+'_'+nombre_cuenca+'.shp')
lista_pol = list()
for i in d.groupby(by = "zone", as_index = True).count().index:
  geom = d[d["zone"]== i]
  lista_pol.append(geom.dissolve(by = 'zone', as_index = True))

##Tratamiento, manejo y analisis exploratorio del archivo tipo multipoligono clasificado
multipoligono = pd.concat(lista_pol, axis = 0, ignore_index = False)
multipoligono.drop(multipoligono[multipoligono["mean"]< 0].index, axis = 0, inplace =True)
multipoligono["Area"] = multipoligono.area


##Debido a que el metodo zonal_stats requiere de la direccion del poligono delimitador, se usa
# el metodo Path para exportar el archivo a un directorio local en drive
pathfile = Path("/content/drive/MyDrive/POLS"+"/"+"multipol_"+nombre_cuenca+".shp")
pathfile.parent.mkdir(parents =True, exist_ok  =True)
multipoligono.to_file(pathfile)


##Estadisticas zonales en formato dataframe
estadisticas = pd.DataFrame(zonal_stats("/content/drive/MyDrive/POLS"+"/"+"multipol_"+nombre_cuenca+".shp",boulder.fetch(), stats = "count min mean max median" ))

##Tratamiento, manejo y analisis exploratorio del dataframe con las estadisticas zonales
estadisticas.drop(estadisticas[estadisticas["min"] == estadisticas["max"]].index, axis = 0, inplace =True)


##Conformacion de la forma final de los datos conteniendo las estadisticas zonales y los atributos geometricos
# necesarios
data = pd.concat([multipoligono, estadisticas], axis = 1 , ignore_index= False)


#Calculo de area acumulada
Area_array = data["Area"].to_numpy()
cum_Area = np.cumsum(Area_array)


#Calculo de altura media
Altura_media = (data['min'] + data['max'])/2
Altura_vect = Altura_media.to_numpy()


#Calculo de area acumulada porcentual
valores = list()
for i in range(len(cum_Area)):
  div = ((cum_Area[i])/(cum_Area[len(cum_Area)-1]))*100
  valores.append(div)


#ploteo de valores
fig, ax   = plt.subplots(figsize=(10,6))
ax.plot(valores, np.flip(Altura_vect),label = 'curva_hipsometrica', color = 'red')
ax.scatter(valores,np.flip(Altura_vect), color = 'red')
ax.grid(True)
ax.legend()
plt.xlabel('Area Acumulada(%)')
plt.ylabel('Altura Media(m)')
plt.title('CURVA HIPSOMETRICA')