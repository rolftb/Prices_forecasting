# =============================================================================
# Importar paquetes y abrir Data
# =============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from geopandas import *
from plotnine import *

#para ajustar las fechas
import datetime

#para calcular el skew de un array() o list()
from scipy.stats import skew 

#%%
Filname='(column)Facturac_2017_2020.csv'

#Filname ='C:/Users/rolft/Documents/Tesis/Codigo/Trutro/Clustering Clientes/Data'
Fillocal=(
'C:/Users/rolft/Documents/Tesis/Codigo/Trutro/Clustering Clientes/Data/')

Fil=Fillocal+Filname
print(Fil)
col_names=pd.read_csv(Fil,
                    encoding="utf-8",sep=";",nrows=0).columns
types_dict = {col: str for col in col_names}

Data = pd.read_csv(Fil,
                   encoding="utf-8",sep=";",dtype=types_dict)

del Filname,Fillocal,Fil,types_dict
#%%
# =============================================================================
# Ajustar la data
# =============================================================================
def Ajuste_data(data):
    df=data.copy()
    # Funciones para eliminar los putos y cambiar las , por .
    def change_num_point(x):
        x=str(x)
        return x.replace('.', '')
    def change_num_coma(x):
        x=str(x)
        return x.replace(',', '.')
    for i in ['Kilos Venta KG','Venta Neta CLP','Precio Promedio CLP']:
        df[i]=df[i].apply(change_num_point)
        df[i]=df[i].apply(change_num_coma)
        df[i]=df[i].astype('int64')

        #Separacion fecha
    df['Semana']=df['Año natural/Semana'].str.split('.', expand=True)[[0]]
    df['Año']=df['Año natural/Semana'].str.split('.', expand=True)[[1]]

    df['Semana']=df['Semana'].astype('int64')
    df['Año']=df['Año'].astype('int64')
    
    #
    df["Día natural"] = df["Día natural"].apply(lambda x: 
                                                datetime.datetime.strptime(x,
                                                                           '%d.%m.%Y').date())
    return df
#%%

data=Ajuste_data(Data)
data=data[data['Año']>2018]
col_client='Cliente - Local.1'
# Creamos la Data clientes para almacenar las caracteristicas de los clientes
D_Clientes=pd.DataFrame({col_client:data[col_client].unique()
                        })
D_Clientes[col_client]=D_Clientes[col_client].astype('category')
D_Clientes.shape

#%%
# =============================================================================
# Función
# =============================================================================

def Proc_caida(data,id_client):
    
    #71225
    #id_client=D_Clientes['Cliente - Local.1'].iloc[i]    
    #id_client='71225'   
    df_i=data[data[col_client]==id_client].copy()
    
    
    #se ordenan los dias de forma creciente
    #para tener los Delta bien configurados
    df_i=df_i.sort_values(by=['Día natural'])
    
    #########################################
    #
    #########################################
    dias=list(df_i['Día natural'])
    
    #inicio con valores cero
    delta=list()
    delta_mean=0
    ratio_mean=0
    # recorre todos los dias menos el ultimo
    
    #para generar los delta
    for i in range(len(dias)-1):
        delta.append((dias[i+1] - dias[i]).days)
        delta_mean+=((dias[i+1] - dias[i]).days)
        if(i==len(dias)-1):
            delta.append((datetime.date(2021, 2, 11)- dias[i]).days)

    #delta promedio
    if(len(delta)>0):
        dfdelta=pd.DataFrame({'delta':delta})
        delta_mean=delta_mean/(len(delta))
        Proc=dfdelta[dfdelta['delta']>=(2*delta_mean)].shape[0]
        Proc=Proc/len(delta)
    else:
        delta_mean=delta_mean
        Proc=0
    return(delta_mean,Proc*100)

#%%
# =============================================================================
# Prueba
# =============================================================================
y='71225'
print(Proc_caida(data,y))
#%%
# =============================================================================
# Prueba
# =============================================================================
delta_mean=list()
Proc=list()

for i in range(len(D_Clientes)):
    delta_mean.append(Proc_caida(D_Clientes,i)[0])
    Proc.append(Proc_caida(D_Clientes,i)[1])

