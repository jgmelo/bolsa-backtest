# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 09:57:12 2018

@author: usuario
"""

from bkt import BackTest
from visual import Visualiza

DATA_ANALISE = '2018.11.01'
# Cria objeto.
hilo04 = BackTest()

# Carrega dados no objeto criado.
hilo04.carrega_csv()

#Calcula medias moveis para HiLo.
hilo04.media()

# Cria objeto para plotagem do gráfico
hilo04_vis = Visualiza()
separado = hilo04_vis.categoriza_por_data(hilo04.get_lista_fonte())

# Cria dicionario de annotations
#dic_ann = hilo04.estr_hilo(separado[DATA_ANALISE])
dic_ann = hilo04.single_bar(separado[DATA_ANALISE])
hilo04_vis.plota(separado[DATA_ANALISE], dic_ann, indic01 = True, indic02 = True)