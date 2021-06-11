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
    df["Día natural"] = df["Día natural"].apply(lambda x: 
                                                datetime.datetime.strptime(x,
                                                                           '%d.%m.%Y').date())
    return df

data=Ajuste_data(Data)

col_client='Cliente - Local.1'
# Creamos la Data clientes para almacenar las caracteristicas de los clientes
D_Clientes=pd.DataFrame({col_client:data[col_client].unique()
                        })
D_Clientes[col_client]=D_Clientes[col_client].astype('category')
D_Clientes.shape

#%%
# =============================================================================
# Frecuencia Clientes
# =============================================================================

def frec_cliente(D_Clientes,i):
    id_client=D_Clientes.iloc[i,0]
    
    
    df_i=data[data[col_client]==id_client].copy()
    #-------------------------------------------
    #primer año
    #int((str(df_i['Día natural'].min()))[:4])
    ano_in=df_i['Día natural'].min().year
    
    #primer mes
    #int((str(df_i['Día natural'].min()))[5:7])
    mes_in=df_i['Día natural'].min().month
    
    
    #---------------------------------------------------------------------------
    # values
    date_v=list(df_i.groupby(['Mes','Año'],
                             sort=True).count()['Kilos Venta KG'])

    #index
    date_i=list((df_i.groupby(['Mes','Año'],
                              sort=True).count()['Kilos Venta KG']).index)
    date_i
    
    
    #------------------------------
    #
    #------------------------------
    fechas=list()
    for a in range(ano_in,2022):
        if a==ano_in:
            for m in range(mes_in,13):
                t=tuple((str(m),a))
                fechas.append(t)     
        elif(a==2021):
            for m in range(1,3):
                t=tuple((str(m),a))
                fechas.append(t)
        else:
            for m in range(1,13):
                t=tuple((str(m),a))
                fechas.append(t)

    return ((pd.merge(pd.DataFrame({'Date':fechas}),
                    pd.DataFrame({'Date':date_i,'Frecuencia':date_v})
                 , how='left'))['Frecuencia'].sum()/len(fechas))
#%%

print(frec_cliente(D_Clientes,0))



#%%
Client_frec=list()#[ i for i in range(len(D_Clientes))]
for i in range(len(D_Clientes)):
    Client_frec.append(frec_cliente(D_Clientes,i))

df_clientes=pd.DataFrame({col_client:D_Clientes[col_client],
                          'Frecuencia mes promedio':Client_frec})



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
    
    #########################################
    #
    #########################################
    lote=list(df_i['Kilos Venta KG'])
    dias=list(df_i['Día natural'])
    
    #inicio con valores cero
    delta=list()
    delta_mean=0
    ratio_mean=0
    # recorre todos los dias menos el ultimo
    #para generar los delta
    for i in range(len(dias)-1):
        delta.append((dias[i+1] - dias[i]).days)
        ratio_mean+=delta[i]/lote[i]
        delta_mean+=((dias[i+1] - dias[i]).days)
    #delta promedio
    if(len(delta)>0):
        delta_mean=delta_mean/(len(delta))
        ratio_mean=ratio_mean/(len(delta))
        skew_delta =skew(delta)
    else:
        delta_mean=delta_mean
        ratio_mean=ratio_mean
        skew_delta=0
    df_lote=pd.DataFrame({'lote':lote})
    
    return(delta_mean,skew_delta, sum(lote)/len(lote) ,
           (df_lote.std()['lote']/df_lote.mean()['lote']))
#%%
print(Atributos_cliente(D_Clientes,1))
id_client=D_Clientes.iloc[i,0]    
print(data[data[col_client]==id_client][data.columns[13:]].head())
    
    
    
    
    
    
#%%
delta_mean=list()
skew_delta=list()
Lote_mean=list()
Lote_cov=list()
for i in range(len(D_Clientes)):
    X_a=Atributos_cliente(D_Clientes,i)
    delta_mean.append(X_a[0])
    skew_delta.append(X_a[1])
    Lote_mean.append(X_a[2])
    Lote_cov.append(X_a[3])
    
    
#%%
df_clientes=pd.DataFrame({col_client:D_Clientes[col_client],
                          'Frecuencia mes promedio':Client_frec
                          ,'Delta dia promedio':delta_mean
                          ,'Skew Delta dia':skew_delta
                          ,'Kilos Venta promedio':Lote_mean
                          ,'Covarianza del lote':Lote_cov
                         })
#%%
file_name='Python_Atrib_cleinte_2017_20202.csv'
df_clientes.to_csv(file_name, sep=';', encoding='utf-8', index=False)