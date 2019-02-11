# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 13:45:30 2018

@author: usuario
"""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.finance as fin
import matplotlib.dates as dts
import datetime as dtm
import numpy as np

TAMANHO_FIG_X = 15
TAMANHO_FIG_Y = 8

#TAMANHO_FIG_X = 30
#TAMANHO_FIG_Y = 16

INDICE_K = 0
INDICE_O = 1
INDICE_H = 2
INDICE_L = 3
INDICE_C = 4
INDICE_V = 6
INDICE_D = 7
INDICE_TH = 8
INDICE_MH = 9
INDICE_ML = 10
INDICE_MO = 11
INDICE_MC = 12
    
class Visualiza(object):
    
    # Padrão de uso da classe:
    # 1. Inicializa-se um objeto Visualiza;
    # 2. Chama-se o método categoriza_por_data (Toma valores D-OHLC como
    #    argumento). Motivo: plotagem de mais de
    #    um dia não fica boa no gráfico ainda (gaps grandes entre os dias).
    # 3. Chama-se o método plota para plotar os dados cateogorizados no passo
    #    anterior.
    
    def categoriza_por_data(self,lista_fonte):
        
        # Retorna dicionário com chaves == datas (dias) e valores == lista
        # de listas para entrada de candlestick_ohlc.
        self.d_categoria_diaria = dict()
        
        # Cada valor do dicionário self.d_categoria_diaria
        # é uma lista de listas. As listas do
        # nível herárquico mais baixo são os elementos de lista_fonte.
        # Portanto, agora, esses elementos estão separados por data.
        for elem in lista_fonte:
        
            # Toma o elemento correspondente a data, que é uma string,
            # e mantém somente YYYY.MM.DD ([:10]).
            self.chave_data = elem[INDICE_K][:10]
            
            try:
                # Se a chave existe, inclui o elemento corrente no fim da
                # lista que corresponde ao valor associado.
                self.d_categoria_diaria[self.chave_data].append(elem)
            except KeyError:
                # Se a chave não existir, cria-a e seta o valor como uma lista
                # contendo somente o elemento corrente.
                self.d_categoria_diaria[self.chave_data] = [elem]
                
        return self.d_categoria_diaria
    
    def plota(self, dados, dados_annot, 
              plota_MH = False, 
              plota_ML = False,
              plota_MO = False,
              plota_MC = False):
        
        self.fig = plt.figure(figsize=(TAMANHO_FIG_X,TAMANHO_FIG_Y))
        self.ax = self.fig.add_subplot(111)
        
        # Cria lista somente com os dados da data data_string
        self.dados = dados
        
        # Converte datas de string para datetime e depois para float.
        self.coluna_data_string = [x[INDICE_K] for x in self.dados]
        self.coluna_data_float = self.converte_data_em_float(self.coluna_data_string)
        
        # Cria lista argumento de entrada para a função candlestick_ohlc.
        self.entrada_ohlc = []
        for elem_data, elem_dados in zip(self.coluna_data_float, self.dados):
            self.aux = [elem_data]
            self.aux.extend(elem_dados[1:5])
            self.entrada_ohlc.append(self.aux)
#        self.entrada_ohlc = list(map(lambda y,z: [y].append(z), self.coluna_data_float, self.dados))
        
        # Cria lista argumento de entrada para a plotagem do volume.
        self.entrada_volume = []
        for elem_data, elem_dados in zip(self.coluna_data_float, self.dados):
            self.aux = [elem_data]
            self.aux.append(elem_dados[INDICE_O])
            self.aux.append(elem_dados[INDICE_C])
            self.aux.append(elem_dados[INDICE_V])
            self.entrada_volume.append(self.aux)
        
        # *************************************
        # ***** Plotagem do candlestick *******
        # *************************************
        
        fin.candlestick_ohlc(self.ax, self.entrada_ohlc, width=0.002, colorup=(0,1,0.2))
        
        # Instrui Matplotlib a definir automaticamente os xticks e
        # define a formatação desses xticks.
        self.ax.xaxis.set_major_locator(dts.AutoDateLocator())
        self.ax.xaxis.set_major_formatter(dts.DateFormatter('%H:%M'))
        
        # *************************************
        # ***** Plotagem das MMs **************
        # *************************************

        if plota_MH == True:
            self.coluna_medias_aux = list(map(lambda x: x[INDICE_MH], self.dados))
            self.ax.plot(self.coluna_data_float, self.coluna_medias_aux, color='b')
            
        if plota_ML == True:
            self.coluna_medias_aux = list(map(lambda x: x[INDICE_ML], self.dados))
            self.ax.plot(self.coluna_data_float, self.coluna_medias_aux, color='b')
        
        if plota_MO == True:
            self.coluna_medias_aux = list(map(lambda x: x[INDICE_MO], self.dados))
            self.ax.plot(self.coluna_data_float, self.coluna_medias_aux, color='b')
            
        if plota_MC == True:
            self.coluna_medias_aux = list(map(lambda x: x[INDICE_MC], self.dados))
            self.ax.plot(self.coluna_data_float, self.coluna_medias_aux, color='k')

        # *************************************
        # ***** Plotagem do volume. ***********
        # *************************************
        
        # Cria eixo secundário.
        self.ax_secundario = self.ax.twinx()
        
        self.vol_verde = list(filter(lambda s: s[2] >= s[1], self.entrada_volume))
        self.vol_verde_x = list(map(lambda x: x[0], self.vol_verde))
        self.vol_verde_y = list(map(lambda x: x[3], self.vol_verde))
        
        self.vol_vermelho = list(filter(lambda s: s[2] < s[1], self.entrada_volume))
        self.vol_vermelho_x = list(map(lambda x: x[0], self.vol_vermelho))
        self.vol_vermelho_y = list(map(lambda x: x[3], self.vol_vermelho))
        
        self.ax_secundario.bar(self.vol_verde_x, self.vol_verde_y, width=0.0025, color='g')
        self.ax_secundario.bar(self.vol_vermelho_x, self.vol_vermelho_y, width=0.0025, color='r')
        self.ax_secundario.set_position(matplotlib.transforms.Bbox([[0.125,-0.2],[0.9,0.09]]))
        
        # *************************************
        # ***** Inclusão das annotations. *****
        # *************************************
        
        self.y_max = self.ax.get_ybound()[1]
        self.y_min = self.ax.get_ybound()[0]
        # Calcula y médio do gráfico.
        self.y_medio = self.y_min + (self.y_max - self.y_min) / 2
        
        # A posição do texto de annotation é definida de forma crescente,
        # para melhor visualização. Por isso, faz-se um linspace abaixo, 
        # para que os textos sigam a diagonal do gráfico.
        for texto, data_hora, y_annotation, y_texto in \
        zip(dados_annot['texto'],\
            self.converte_data_em_float(dados_annot['datahora']),\
            dados_annot['y_annot'],\
            np.linspace(self.y_min, self.y_max, len(dados_annot['texto']))):
            
            self.ax.annotate(texto,\
                             xy = (data_hora, y_annotation),\
                             xytext = (data_hora, y_texto),\
                             arrowprops = dict(arrowstyle="->", connectionstyle="arc3"))

        plt.show()
        
    def converte_data_em_float(self, l_data_string):
        
        # Método para fazer a conversão de data para float, de forma a ser
        # aceita por candlestick_ohlc.
        
        self.l_data_float = \
        [dts.date2num(dtm.datetime(\
                                   int(x[:4]),\
                                   int(x[5:7]),\
                                   int(x[8:10]),\
                                   int(x[11:13]),\
                                   int(x[14:16]))) for x in l_data_string]            

        return self.l_data_float
        