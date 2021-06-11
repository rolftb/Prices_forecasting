import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from geopandas import *
from plotnine import *


from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

#%%
##################################
# Activación de los DF
###################################

#Activar DF clientes 2019 al 2020
Clientes_df = pd.read_csv("Data/Resultantes/Clientes_precios_19_20.csv",
                          encoding="utf-8",sep=";",dtype={'Cliente - Local.1': 'str'})
print('Clientes 2019 al 2020',Clientes_df.shape)

#Atributos categoricos desde 2017 al 2020

Categ_Atrib = pd.read_csv("Data/Resultantes/Atrinbutos_categoricos_clientes.csv",
                          encoding="utf-8",sep=";",dtype={'Cliente - Local.1': 'str'})
## esta data lo unico que se debe cambiar es la fecha del primer año

print('Atributos de los clientes del 2017 al 2020',Categ_Atrib.shape)
print(list(Categ_Atrib.columns) )

Atrb_client = pd.read_csv("Data/Resultantes/Python_Atrib_cleinte_2017_20202.csv",
                          encoding="utf-8",sep=";",dtype={'Cliente - Local.1': 'str'})

#Atrb_client = Atrb_client.rename(columns={'Cliente - Local.1': 'Dest. Mercancía'})

print('Atributos Facturación clientes del 2017 al 2020',Atrb_client.shape)

#%%
D_Clientes=pd.merge(Atrb_client , Clientes_df  
     , how='right')
D_Clientes=pd.merge(Categ_Atrib , D_Clientes  
     , how='right')
D_Clientes.shape
#%%
def Grafico_Nan(S):
    #S='Oficina de Ventas Unifica'
    Col=list(D_Clientes.columns)
    Col=Col[Col.index('Covarianza del lote'):]

    #PorcNaN=[ (D_Clientes[i].isnull().sum()/D_Clientes.shape[0])*100 for i in Col]
    Atributo=list()
    PorcNaN=list()
    S_Val=list()
    for c in Col:
        for s in D_Clientes[S].unique():
            Atributo.append(c)
            PorcNaN.append((D_Clientes[
                D_Clientes[S]==s][c].isnull().sum()/D_Clientes.shape[0])*100)
            S_Val.append(s)
    G=(
        ggplot(pd.DataFrame({'Atributo':Atributo,
                             'Procentaje de NaN':PorcNaN
                             ,S:S_Val
                            })
               , aes(x='Atributo',
                     y='Procentaje de NaN',fill=S))\
    + geom_col()\
    +theme(axis_text_x = element_text(angle=90, hjust=1)))#
    return(G)
Graf=list()
for i in list(Categ_Atrib.columns)[1:]:
    Graf.append(Grafico_Nan(i))
Graf
#%%
# =============================================================================
# DF con los clientes que si poseen Cov
# =============================================================================
#Los NaN en Cov implica que solo realizaron una compra



D_Clientes_Frec=(D_Clientes[~D_Clientes['Covarianza del lote'].isnull()]).copy()
print(D_Clientes_Frec.shape)
D_Clientes_Frec.hist()
D_Clientes_Frec.fillna(-1).hist()
#%%
Col=list(D_Clientes.columns)#=D_Clientes.fillna(0)
Col=Col[Col.index('Frecuencia mes promedio'):]
Col

X=D_Clientes_Frec.fillna(-1)
X_std=X[Col].copy()

from sklearn.preprocessing import StandardScaler

X_std = pd.DataFrame(StandardScaler().fit_transform(X_std),columns=X_std.columns)

from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=6)

import matplotlib.pyplot as plt

#la suma del error cuadrático para diferentes valores de k
SSE = []
for i in range(1, 21):
  km = KMeans(n_clusters=i)
  km.fit(X_std)
  SSE.append(km.inertia_)

# plot

plt.plot(range(1, 21), SSE,'-o', color='black')
plt.xlabel('Número of clusters')
plt.ylabel('SSE')
plt.show()
#%%
from sklearn.decomposition import PCA
print('Cantidad de columnas',len(list(X_std.columns)))

# Crear una instancia PCA: pca
pca = PCA()
principalComponents = pca.fit_transform(X_std)

# Graficar el porcetanje de la varianza que es explicada por cada componente
features = range(pca.n_components_)
plt.bar(features, pca.explained_variance_ratio_, color='black')
plt.xlabel('PCA features')
plt.ylabel('variance %')
plt.xticks(features)

# Guardar las componentes en un dataframe
PCA_components = pd.DataFrame(principalComponents)





#%%

Col=list(D_Clientes.columns)#=D_Clientes.fillna(0)
Col=Col[Col.index('Frecuencia mes promedio'):]
Col

X=D_Clientes_Frec.fillna(-1).copy()
X_std=X[Col].copy()

from sklearn.preprocessing import StandardScaler

X_std = pd.DataFrame(StandardScaler().fit_transform(X_std),columns=X_std.columns)





# =============================================================================
# # Modelo Kmenas
# =============================================================================

from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=5)
kfit = kmeans.fit(X_std)
identified_clusters = kfit.predict(X_std)
X['identified_clusters']=identified_clusters
X['identified_clusters']=X['identified_clusters'].astype('category')



#%%
# =============================================================================
# GRafico de Disposición a Pagar
# =============================================================================
a=X.groupby('identified_clusters').mean()#['Frecuencia mes promedio']

S_Clust=list(Clientes_df.columns)[1:]
Value=list()
ClusterDis=list()
Indent_cluster=list()
for i in list(a.index):
    for j in range(5):
        Value.append(a.iloc[i][5+j])
        ClusterDis.append(S_Clust[j])
        Indent_cluster.append(i)
P=pd.DataFrame(
{
'Value':Value,
'Disp a pagar Cluster':ClusterDis,
'identified_clusters':Indent_cluster,
})
P.identified_clusters=P.identified_clusters.astype('category')

#%%
GRaph_Disp_cluster=(
    ggplot(P, aes(x='Disp a pagar Cluster',y='Value'
                     ))\
                + labs(y='Disposición a pagar')\
                + geom_point(aes(color='identified_clusters'))\
                +geom_smooth()\
                +ggtitle(('Dispersión Clusters Clientes'+' \n Disposición a pagar v/s '+
                         'Tipo de Semana'))\
                +theme(axis_text_x = element_text(angle=90, hjust=1)
                       )#,figure_size=(15,8)

    )
GRaph_Disp_cluster
#%
a['identified_clusters']=list(a.index)
Gplot=list()
for c in a.columns[:5]:
    if(c=='Delta dia promedio'):
        Gplot.append(
        ggplot(a, aes(x='identified_clusters',y=c, color='Skew Delta dia'
                         ))\
                    + geom_point()\
                    +ggtitle(('Dispersión Clusters Clientes'+' \n'+
                             c))\
                   +theme(axis_text_x = element_text(angle=90, hjust=1))\
        )
    elif(c!='Skew Delta dia'):
        Gplot.append(
            ggplot(a, aes(x='identified_clusters',y=c
                             ))\
                        + geom_point()\
                        +ggtitle(('Dispersión Clusters Clientes'+' \n'+
                                 c))\
                       +theme(axis_text_x = element_text(angle=90, hjust=1))\
            )
#%%
Gplot