# =============================================================================
# Importar paquetes y abrir Data
# =============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from geopandas import *
from plotnine import *

#para ajustar las fechas
import datetime

#para calcular el skew de un array() o list()
from scipy.stats import skew 

#%%
Filname='(column)Facturac_2017_2020.csv'

#Filname ='C:/Users/rolft/Documents/Tesis/Codigo/Trutro/Clustering Clientes/Data'
Fillocal=(
'C:/Users/user/Documents/Codigo/Codigo Cerdo/Clustering Clientes/Data/')

Fil=Fillocal+Filname
print(Fil)
col_names=pd.read_csv(Fil,
                    encoding="utf-8",sep=";",nrows=0).columns
types_dict = {col: str for col in col_names}

Data = pd.read_csv(Fil,
                   encoding="utf-8",sep=";",dtype=types_dict)

del Filname,Fillocal,Fil,types_dict




Data=Data[Data['Zona de ventas.1']=='Temuco']
print(Data.describe(include='all'))
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
    df["Día natural"] = \
    df["Día natural"].apply(lambda x: 
                                    datetime.datetime.strptime(x,
                                                           '%d.%m.%Y').date())
    return df

data=Ajuste_data(Data)

col_client='Cliente - Local.1'
# Creamos la Data clientes para almacenar las caracteristicas de los clientes
D_Clientes=pd.DataFrame({col_client:data[col_client].unique()
                        })
D_Clientes[col_client]=D_Clientes[col_client].astype('category')
print(D_Clientes.shape)



#%%
# =============================================================================
# Atributos Clientes
# =============================================================================
def Atributos_cliente(D_Clientes,i):
    id_client=D_Clientes.iloc[i,0]    
    df_i=data[data[col_client]==id_client].copy()
    
    
    #se ordenan los dias de forma creciente
    #para tener los Delta bien configurados
    df_i=df_i.sort_values(by=['Día natural'])
    
    Last_day=list(df_i['Día natural'])
    #print(Last_day)
    #print('Cant dias',len(Last_day))
    
    Last_day=Last_day[len(Last_day)-1]
    
    #print('Ultimo dia',Last_day)
    row=df_i[df_i['Día natural']==Last_day]

    
    
    return( list(row['Oficina de Ventas Unifica'])[0],
            list(row['Subtipo de cliente'])[0],
            list(row['Cluster'])[0],
           )
 

print(Atributos_cliente(D_Clientes,0))
    
    
    
    
    
    
    
#%%
Sucursal=list()
Subtipo=list()
Cluster_prev=list()

for i in range(len(D_Clientes)):
    X_a=Atributos_cliente(D_Clientes,i)
    Sucursal.append(X_a[0])
    Subtipo.append(X_a[1])
    Cluster_prev.append(X_a[2])
    
    
#%%
df_clientes=pd.DataFrame({col_client:D_Clientes[col_client],
                          'Oficina de Ventas Unifica':Sucursal,
                          'Subtipo de cliente':Subtipo,
                          'Cluster BW':Cluster_prev
                         })
#%%
file_name='Atrinbutos_categoricos_clientes.csv'
df_clientes.to_csv(file_name, sep=';', encoding='utf-8', index=False)