# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 12:04:10 2018

@author: usuario
"""
import datetime as dtm

HILO_PERIODOS = 12

INDICE_K = 0
INDICE_O = 1
INDICE_H = 2
INDICE_L = 3
INDICE_C = 4
INDICE_D = 7
INDICE_TH = 8
INDICE_MH = 9
INDICE_ML = 10

# Fator que multiplicará o stop loss para definir o take profit.
#> Implementar o fornecimento desse fator como argumento.
FATOR_LUCRO = 2

# Número de barras a ser tolerado antes de cancelar o setup Single Bar.
TOLERANCIA_POS_SBAR = 2
# Sequência de lista_fonte: [K O H L C TV V D TH MH ML ]
#                           [0 1 2 3 4 5  6 7 8 9 10 ]

# Padrão de uso da classe:
# 1. Inicializa objeto BackTest();
# 3. chama objeto.carrega_csv() para trazer os dados do ativo;


class BackTest(object):

    def carrega_csv(self):
        
        self.lista_fonte = []
        
        # Abre o arquivo csv e...
        # >Trocar futuramente por um arquivo a ser informada pelo usuário,
        # >com tratamento de exceção para o caso do arquivo não existir.
        with open('base.csv', mode='r') as self.infile:
            
            for self.linha in self.infile:
                # O arquivo .csv exportado do MT5 vem com caracteres que devem ser
                # substituídos. Possivelmente pode ser resolvido com escolha de codi-
                # ficação, mas resolvi assim mais rápido.
                self.linha = self.linha.replace('\x00','').replace('\n','')
                self.sep=self.linha.split(',')
                
                if len(self.sep) > 1:# Linhas vazias aparecem intercaladas e não interessam.
                    
                    # Converte as strings para float. 
                    # >Fazer de um jeito mais elgante, utilizando exceções.
                    for self.indice in range(1,len(self.sep)):
                        self.sep[self.indice] = float(self.sep[self.indice])
                    
                    self.sep.append(self.sep[0].split(' ')[0])
                    self.sep.append(self.sep[0].split(' ')[1])
                    
                    self.lista_fonte.append(self.sep)
        
        # Remove o primeiro elemento, que vem com um primeiro caractere (do 
        # arquivo inteiro) impertinente da importação do csv.
        self.lista_fonte = self.lista_fonte[1:]
            
        return self.lista_fonte
        # Problema de se usar dicionario aqui: dicionario não é ordenado.
        # Por isso não está sendo usado.
        
    def media(self):
        
        self.lista_H_hilo = []
        self.lista_L_hilo = []
        
        # Monta duas listas (inicializadas acima), 
        # uma com máximas e outra com mínimas. Data/hora estão mantidas como
        # chave de cada valor.
        for self.elem in self.lista_fonte:
            self.lista_H_hilo.append([self.elem[INDICE_H], self.elem[INDICE_K]])
            self.lista_L_hilo.append([self.elem[INDICE_L], self.elem[INDICE_K]])
            
        self.lista_medias_H_hilo = []
        self.lista_medias_L_hilo = []
        
        # Inicia a criação das listas das médias móveis das máximas e mínimas
        # (inicializadas acima). Até HILO_PERIODOS-1, não dá pra calcular a MM.
        while len(self.lista_medias_H_hilo) < HILO_PERIODOS:
            self.lista_medias_H_hilo.append(3610.0)    
        while len(self.lista_medias_L_hilo) < HILO_PERIODOS:
            self.lista_medias_L_hilo.append(3605.0)
        
        # Ao invés de incrementar o índice (precisaria de um for baseado em
        # índice), as listas auxiliares têm seu primeiro elemento removido a
        # cada iteração, o que permite que sempre se pegue uma janela de tamanho
        # HILO_PERIODOS o primeiro elemento dessas listas em cada iteração, 
        # mantendo assim o efeito de incremento de posição.
        
        # Unica diferença das listas auxiliares é que não tem a chave.
        # São listas de números puros (H/L).
        self.lista_H_hilo_aux = list(map(lambda ls: ls[0], self.lista_H_hilo))
        self.lista_L_hilo_aux = list(map(lambda ls: ls[0], self.lista_L_hilo))
    
        while len(self.lista_H_hilo_aux) > HILO_PERIODOS:
            self.lista_medias_H_hilo.append(sum(self.lista_H_hilo_aux[:HILO_PERIODOS]) / HILO_PERIODOS)
            self.lista_H_hilo_aux = self.lista_H_hilo_aux[1:]
        while len(self.lista_L_hilo_aux) > HILO_PERIODOS:
            self.lista_medias_L_hilo.append(sum(self.lista_L_hilo_aux[:HILO_PERIODOS]) / HILO_PERIODOS)
            self.lista_L_hilo_aux = self.lista_L_hilo_aux[1:]
            
        # Neste ponto, temos médias móveis de H e L nas posições
        # correspondentes a cada elemtno (lista de dados) de self.lista_fonte.
        # Basta, então, fazer append de cada elemento de lista_medias_X_hilo no
        # elemento correspondente de self.lista_fonte.
        list(map(lambda l_orig, l_medias: l_orig.append(l_medias),self.lista_fonte, self.lista_medias_H_hilo))
        list(map(lambda l_orig, l_medias: l_orig.append(l_medias),self.lista_fonte, self.lista_medias_L_hilo))
        
        return self.lista_fonte

    def get_lista_fonte(self):
        
        # Getter para self.lista_fonte.
        
        return self.lista_fonte
            
#    def get_entrada_candlestick_ohlc(self):
#        
#        # Retorna [data em float ([x]) e OHLC (i[INDICE_O:INDICE_C+1])] como uma tupla de 
#        # listas, para ser usada como entrada em candlestick_ohlc. 
#        return tuple(list(map(lambda x,i: [x] + i[INDICE_O:INDICE_C+1], self.l_datahora_float, self.lista_fonte)))
        
    def estr_hilo(self, lista_fonte_periodo):
        # Argumento lista_fonte_periodo é uma lista de listas.
        # Cada lista folha é a sequência de dados de um candle.
        
        # Inicialização das variáveis e das flags.
        self.saldo = 100.0
        self.aporte = 0.0
        self.take_profit = 0.0
        self.stop_loss = 0.0
        self.ohlc_aux = []
        self.flag_entrou = False
        self.flag_compra = False
        self.flag_venda = False
        self.d_params_annotation = {'texto':[], 'y_annot':[], 'ytext_annot':[], 'datahora':[]}

        for vela in lista_fonte_periodo:
            
            #***********************************************
            #***** Código para pular as horas iniciais *****
            #***********************************************
            
            self.hora_offset = dtm.datetime(int(vela[INDICE_D][:4]),
                                            int(vela[INDICE_D][5:7]),
                                            int(vela[INDICE_D][8:10]),
                                            10,
                                            0)
            
            if self.conv_str_datetime(vela[INDICE_K]) < self.hora_offset:
                continue
            
            #***********************************************
            #***** Fim do código para pular horas iniciais *
            #***********************************************
            
            
            # Se o saldo do dia for negativo, sai da função.
            #if self.saldo < 0: return self.saldo
            
            #******************************************
            #***** Código para entrar na operação *****
            #******************************************
            
            # Testa valor de fechamento contra média. Se condição for
            # satisfeita, entra na lógica para realizar o aporte.
            if (vela[INDICE_C] > vela[INDICE_MH]) and self.flag_entrou == False: 
                
                # Seta flag para indicar que entrou no trade.
                self.flag_entrou = True
                # Seta flag para indicar que entrou comprando.
                self.flag_compra = True
                # Salva dados do candle da operação de entrada.
                self.ohlc_aux = vela
                
                if self.saldo >= 100:
                    self.aporte = 100
                    self.saldo -= 100
                else:
                    # Variável auxiliar para diminuir a expressão.
                    self.aporte_aux = vela[INDICE_C] - vela[INDICE_ML]
                    # Resultado é em pontos, e cada ponto vale R$10 (ativo WDOL).
                    # Se for tal que o aporte seja maior que R$100, o mesmo fica
                    # limitado a R$100.
                    self.aporte = 10*self.aporte_aux if self.aporte_aux < 10 else 100
                    self.saldo -= 10*self.aporte_aux if self.aporte_aux < 10 else 100
                    
                self.aux_take_profit = vela[INDICE_C] - vela[INDICE_ML]
                self.take_profit = vela[INDICE_C] + FATOR_LUCRO * self.aux_take_profit
                
                # Inclui na lista referente ao texto para as annotations a
                # descrição da entrada na operação.
#                self.d_params_annotation['texto'].append(\
#                                        'Entrada, compra.\nHora da entrada: '\
#                                        + vela[INDICE_TH]\
#                                        + '\nPreço de entrada: '\
#                                        + str(vela[INDICE_C])\
#                                        + '\nPreço de take profit: '\
#                                        + str(self.take_profit)\
#                                        + '\nPreço de stop loss: '\
#                                        + str(vela[INDICE_ML])\
#                                        + '\nAporte: '\
#                                        + str(self.aporte)\
#                                        + '\nSaldo após aporte: '\
#                                        + str(self.saldo))
                self.d_params_annotation['texto'].append(\
                                         'E C')
#                                        'E C às '\
#                                        + vela[INDICE_TH]\
#                                        + ', a '\
#                                        + str(vela[INDICE_C])\
#                                        + ' Sd: '\
#                                        + str(self.saldo))
                # Inclui na lista referente à coordenada y para as annotations
                # o preço de entrada em float.
                self.d_params_annotation['y_annot'].append(vela[INDICE_C])
                # Inclui na lista referente à coordenada y para o texto
                # da annotation o preço de entrada
                # em float, com um offset para evitar sobreposição no gráfico.
                self.d_params_annotation['ytext_annot'].append(vela[INDICE_C]-10)
                # Inclui data/hora em string na lista de datas.
                self.d_params_annotation['datahora'].append(vela[INDICE_K])
                
                #-----------------------
                #----- Debug print -----
                #-----------------------
                print('Entrada, compra.')
                print('Hora da entrada: ' + vela[INDICE_TH])
                print('Preço de entrada: ' + str(vela[INDICE_C]))
                print('Preço de take profit: ' + str(self.take_profit))
                print('Preço de stop loss: ' + str(vela[INDICE_ML]))
                print('Aporte: ' + str(self.aporte))
                print('Saldo após aporte: ' + str(self.saldo))
                print('===========================================')
                    
            if (vela[INDICE_C] < vela[INDICE_ML]) and self.flag_entrou == False:
                
                self.flag_entrou = True
                self.flag_venda = True
                self.ohlc_aux = vela
                    
                if self.saldo >= 100:
                    self.aporte = 100
                    self.saldo -= 100
                else:
                    self.aporte_aux = vela[INDICE_MH] - vela[INDICE_C]
                    self.aporte = 10*self.aporte_aux if self.aporte_aux < 10 else 100
                    self.saldo -= 10*self.aporte_aux if self.aporte_aux < 10 else 100
                    
                self.aux_take_profit = vela[INDICE_MH] - vela[INDICE_C]
                self.take_profit = vela[INDICE_C] - FATOR_LUCRO * self.aux_take_profit
                
#                self.d_params_annotation['texto'].append(\
#                        'Entrada, compra.\nHora da entrada: '\
#                        + vela[INDICE_TH]\
#                        + '\nPreço de entrada: '\
#                        + str(vela[INDICE_C])\
#                        + '\nPreço de take profit: '\
#                        + str(self.take_profit)\
#                        + '\nPreço de stop loss: '\
#                        + str(vela[INDICE_MH])\
#                        + '\nAporte: '\
#                        + str(self.aporte)\
#                        + '\nSaldo após aporte: '\
#                        + str(self.saldo))
                self.d_params_annotation['texto'].append(\
                                         'E V')
#                                        'E V às '\
#                                        + vela[INDICE_TH]\
#                                        + ', a '\
#                                        + str(vela[INDICE_C])\
#                                        + ' Sd: '\
#                                        + str(self.saldo))
                self.d_params_annotation['y_annot'].append(vela[INDICE_C])
                self.d_params_annotation['ytext_annot'].append(vela[INDICE_C]-10)
                self.d_params_annotation['datahora'].append(vela[INDICE_K]) 
                
                #-----------------------
                #----- Debug print -----
                #-----------------------
                print('Entrada, venda.')
                print('Hora da entrada: ' + vela[INDICE_TH])
                print('Preço de entrada: ' + str(vela[INDICE_C]))
                print('Preço de take profit: ' + str(self.take_profit))
                print('Preço de stop loss: ' + str(vela[INDICE_MH]))
                print('Aporte: ' + str(self.aporte))
                print('Saldo após aporte: ' + str(self.saldo))
                print('===========================================')
                
        #**************************************************
        #***** Fim do código para entrar na operação. *****
        #**************************************************
        
        #*****************************************
        #***** Código para sair da operação. *****
        #*****************************************
            if self.flag_entrou == True:
                
                # Verifica se o candle corrente saiu da operação, seja com
                # gain ou loss. Por isso, a lista vela é iterada.
                # Para sair da operação, basta O, H, L ou C satisfazerem
                # os requisitos de saída.
                # self.ohlc_aux e vela são o mesmo tipo de lista.
                for elem in vela[INDICE_O : INDICE_C+1]:
                    if (self.flag_compra == True) and (elem > self.take_profit):
                        # Sai da operação com lucro (take profit).
                        # Lucro é preço corrente (elem) menos o preço de
                        # fechamento do candle que disparou a entrada na
                        # operação.
                        self.saldo += self.aporte + elem - self.ohlc_aux[INDICE_C]
                        
                        # Reseta variáveis e flags
                        self.ohlc_aux = []
                        self.flag_entrou = False # Indica saída do trade.
                        self.flag_compra = False

                        # Inclui na lista referente ao texto para as annotations a
                        # descrição da saída da operação.                        
#                        self.d_params_annotation['texto'].append(\
#                                                'Saída de compra, take profit.'\
#                                                + '\nHora da saída: '\
#                                                + vela[INDICE_TH]\
#                                                + '\nSaldo após saída: '\
#                                                + str(self.saldo))
                        self.d_params_annotation['texto'].append(\
                                                 'S C, TP')
#                                                'S C, TP às '\
#                                                + vela[INDICE_TH]\
#                                                + 'Sd: '\
#                                                + str(self.saldo))
                        # Inclui na lista referente à coordenada y para as annotations
                        # o preço de saída em float.
                        self.d_params_annotation['y_annot'].append(elem)
                        # Inclui na lista referente à coordenada y para o texto
                        # da annotation o preço de entrada
                        # em float, com um offset para evitar sobreposição no gráfico.
                        self.d_params_annotation['ytext_annot'].append(elem-15)
                        # Inclui data em string na lista de datas.
                        self.d_params_annotation['datahora'].append(vela[INDICE_K])
                        
                        #-----------------------
                        #----- Debug print -----
                        #-----------------------
                        print('Saída de compra, take profit.')
                        print('Hora da saída: ' + vela[INDICE_TH])
                        print('Saldo após saída: ' + str(self.saldo))
                        print('===========================================')
                        
                        break
                
                    if (self.flag_compra == True) and (elem < vela[INDICE_ML]):
                        # Sai da operação com perda (stop loss).
                        # O aporte já fui subtraído do saldo, mais acima no código.
                        # Portanto, nada a fazer no saldo.
                        
                        # Reseta variáveis e flags
                        self.ohlc_aux = []
                        self.flag_entrou = False # Indica saída do trade.
                        self.flag_compra = False
                        
                        # Inclui na lista referente ao texto para as annotations a
                        # descrição da saída da operação.                        
#                        self.d_params_annotation['texto'].append(\
#                                                'Saída de compra, take profit.'\
#                                                + '\nHora da saída: '\
#                                                + vela[INDICE_TH]\
#                                                + '\nSaldo após saída: '\
#                                                + str(self.saldo))
                        self.d_params_annotation['texto'].append(\
                                                 'S C, SL')
#                                                'S C, SL às '\
#                                                + vela[INDICE_TH]\
#                                                + ' Sd: '\
#                                                + str(self.saldo))
                        # Inclui na lista referente à coordenada y para as annotations
                        # o preço de saída em float.
                        self.d_params_annotation['y_annot'].append(elem)
                        # Inclui na lista referente à coordenada y para o texto
                        # da annotation o preço de entrada
                        # em float, com um offset para evitar sobreposição no gráfico.
                        self.d_params_annotation['ytext_annot'].append(elem-15)
                        # Inclui data em string na lista de datas.
                        self.d_params_annotation['datahora'].append(vela[INDICE_K])
                        
                        #-----------------------
                        #----- Debug print -----
                        #-----------------------
                        print('Saída de compra, stop loss.')
                        print('Hora da saída: ' + vela[INDICE_TH])
                        print('Saldo após saída: ' + str(self.saldo))
                        print('===========================================')
                        
                        break
                        
                    if (self.flag_venda == True) and (elem < self.take_profit):
                        # Sai da oepração com lucro (take profit).
                        # Lucro é o preço de fechamento do candle que disparou
                        # a entrada na operação menos o preço corrente (elem).
                        self.saldo += self.aporte + self.ohlc_aux[INDICE_C] - elem
                    
                        # Reseta variáveis e flags
                        self.ohlc_aux = []
                        self.flag_entrou = False # Indica saída do trade.
                        self.flag_venda = False
                        
                        # Inclui na lista referente ao texto para as annotations a
                        # descrição da saída da operação.                        
#                        self.d_params_annotation['texto'].append(\
#                                                'Saída de compra, take profit.'\
#                                                + '\nHora da saída: '\
#                                                + vela[INDICE_TH]\
#                                                + '\nSaldo após saída: '\
#                                                + str(self.saldo))
                        self.d_params_annotation['texto'].append(\
                                                 'S V, TP')
#                                                'S V, TP às '\
#                                                + vela[INDICE_TH]\
#                                                + 'Sd: '\
#                                                + str(self.saldo))
                        # Inclui na lista referente à coordenada y para as annotations
                        # o preço de saída em float.
                        self.d_params_annotation['y_annot'].append(elem)
                        # Inclui na lista referente à coordenada y para o texto
                        # da annotation o preço de entrada
                        # em float, com um offset para evitar sobreposição no gráfico.
                        self.d_params_annotation['ytext_annot'].append(elem-15)
                        # Inclui data em string na lista de datas.
                        self.d_params_annotation['datahora'].append(vela[INDICE_K])
                        
                        #-----------------------
                        #----- Debug print -----
                        #-----------------------
                        print('Saída de venda, take profit.')
                        print('Hora da saída: ' + vela[INDICE_TH])
                        print('Saldo após saída: ' + str(self.saldo))
                        print('===========================================')
                        
                        break
                    
                    if (self.flag_venda == True) and (elem > vela[INDICE_MH]):
                        # Sai da operação com perda (stop loss).
                        # O aporte já fui subtraído do saldo, mais acima no código.
                        # O aporte já fui subtraído do saldo, mais acima no código.
                        # Portanto, nada a fazer no saldo.
                        
                        # Reseta variáveis e flags
                        self.ohlc_aux = []
                        self.flag_entrou = False # Indica saída do trade.
                        self.flag_venda = False
                        
                        # Inclui na lista referente ao texto para as annotations a
                        # descrição da saída da operação.                        
#                        self.d_params_annotation['texto'].append(\
#                                                'Saída de compra, take profit.'\
#                                                + '\nHora da saída: '\
#                                                + vela[INDICE_TH]\
#                                                + '\nSaldo após saída: '\
#                                                + str(self.saldo))
                        self.d_params_annotation['texto'].append(\
                                                 'S V, SL')
#                                                'S V, SL às '\
#                                                + vela[INDICE_TH]\
#                                                + 'Sd: '\
#                                                + str(self.saldo))
                        # Inclui na lista referente à coordenada y para as annotations
                        # o preço de saída em float.
                        self.d_params_annotation['y_annot'].append(elem)
                        # Inclui na lista referente à coordenada y para o texto
                        # da annotation o preço de entrada
                        # em float, com um offset para evitar sobreposição no gráfico.
                        self.d_params_annotation['ytext_annot'].append(elem-15)
                        # Inclui data em string na lista de datas.
                        self.d_params_annotation['datahora'].append(vela[INDICE_K])
                        
                        #-----------------------
                        #----- Debug print -----
                        #-----------------------
                        print('Saída de venda, stop loss.')
                        print('Hora da saída: ' + vela[INDICE_TH])
                        print('Saldo após saída: ' + str(self.saldo))
                        print('===========================================')
                        
                        break
        #************************************************
        #***** Fim do código para sair da operação. *****
        #************************************************
        return self.d_params_annotation
    
    def conv_str_datetime(self,datahora):
        # Converte data/hora em string para objeto datetime.
        return dtm.datetime(int(datahora[:4]),
                            int(datahora[5:7]),
                            int(datahora[8:10]),
                            int(datahora[11:13]),
                            int(datahora[14:16]))
    
    def single_bar(self, lista_fonte_periodo):
        
        # Inicializa variáveis e flags.
        self.saldo = 100.0
        self.aporte = 0.0
        self.take_profit = 0.0
        self.stop_loss = 0.0
        self.cont_verdes = 0
        self.cont_vermelhas = 0
        self.tol_pos_sbar = 0
        self.gatilho_entrada = 0.0
        self.C_ultima_vela = 0.0
        self.ohlc_aux = []
        self.fifo_velas = []
        self.flag_entrou = False
        self.flag_sbar_compra = False
        self.flag_sbar_venda = False
        self.d_params_annotation = {'texto':[], 'y_annot':[], 'ytext_annot':[], 'datahora':[]}

        for vela in lista_fonte_periodo:
            
        #***********************************************
        #***** Código para atualizar fifo de velas *****
        #***********************************************
        
            if vela[INDICE_C] > vela[INDICE_O]:
                
                 self.fifo_velas.append('g')
                 # Passa as 3 primeiras velas sem operar.
                 if len(self.fifo_velas) <= 4:
                     continue
                 else:
                     # Volta a fifo para 4 velas de tamanho.
                     self.fifo_velas = self.fifo_velas[1:]
            
            elif vela[INDICE_C] < vela[INDICE_O]:
            
                self.fifo_velas.append('r')
                # Passa as 3 primeiras velas sem operar.
                if len(self.fifo_velas) <= 4:
                     continue
                else:
                     # Volta a fifo para 4 velas de tamanho.
                     self.fifo_velas = self.fifo_velas[1:]
            
            # Se o preço de entrada e de fechamento forem iguais,
            # considera-se o mesmo tipo da vela anterior.
            else:
                self.fifo_velas.append(self.fifo_velas[-1])
                # Passa as 3 primeiras velas sem operar.
                if len(self.fifo_velas) <= 4:
                     continue
                else:
                    # Volta a fifo para 4 velas de tamanho.
                    self.fifo_velas = self.fifo_velas[1:]
                
        #******************************************************
        #***** Fim do código para atualizar fifo de velas *****
        #******************************************************
            
        #*******************************************
        #***** Código para detectar single bar *****
        #*******************************************
            
            if (vela[INDICE_C] < vela[INDICE_O]) and not(self.flag_sbar_compra or self.flag_sbar_venda):
                
                # Checa se as 3 primeiras velas da fifo são verdes e se a
                # quarta vela é vermelha.
                self.cont_verdes = len(list(filter(lambda x: x=='g', self.fifo_velas[:-1])))
                if self.cont_verdes == 3 and self.fifo_velas[-1] == 'r':
                    
                    # Gatilho de entrada é C da última vela de tendência.
                    # Vai para a próxima vela.
                    self.gatilho_entrada = self.C_ultima_vela
                    self.flag_sbar_compra = True
                    continue
                    
            elif vela[INDICE_C] > vela[INDICE_O] and not(self.flag_sbar_compra or self.flag_sbar_venda):

                # Checa se as 3 primeiras velas da fifo são vermelhas e se a
                # quarta vela é verde.
                self.cont_vermelhas = len(list(filter(lambda x: x=='r', self.fifo_velas[:-1])))
                if self.cont_vermelhas == 3 and self.fifo_velas[-1] == 'g':
                    
                    # Gatilho de entrada é C da última vela de tendência.
                    # Vai para a próxima vela.
                    self.gatilho_entrada = self.C_ultima_vela
                    self.flag_sbar_venda = True
                    continue
                    
                # Se nenhuma das condições ocorrer, pelo próprio fluxo do programa
                # segue para a próxima vela.
                    
            #**************************************************
            #***** Fim do código para detectar single bar *****
            #**************************************************
            
            #*******************************************
            #***** Código para entrar na operação *****
            #*******************************************
            
            for elem in vela[INDICE_O : INDICE_C+1]:
                
                if (elem >= self.gatilho_entrada) and self.flag_sbar_compra and not(self.flag_entrou):
                    
                    self.flag_entrou = True
                    
                    # Utilizando MML como stop loss.
                    self.stop_loss = vela[INDICE_ML] 
                    
                    if self.saldo >= 100:
                        self.aporte = 100
                        self.saldo -= 100
                    else:
                        # Variável auxiliar para diminuir a expressão.
                        self.aporte_aux = elem - self.stop_loss
                        # Resultado é em pontos, e cada ponto vale R$10 (ativo WDOL).
                        # Se for tal que o aporte seja maior que R$100, o mesmo fica
                        # limitado a R$100.
                        self.aporte = 10*self.aporte_aux if self.aporte_aux < 10 else 100
                        self.saldo -= 10*self.aporte_aux if self.aporte_aux < 10 else 100
                        
                    self.aux_take_profit = vela[INDICE_C] - self.stop_loss
                    self.take_profit = vela[INDICE_C] + FATOR_LUCRO * self.aux_take_profit
                    
                    self.d_params_annotation['texto'].append('E C')
                    self.d_params_annotation['y_annot'].append(elem)
                    self.d_params_annotation['ytext_annot'].append(elem-10)
                    self.d_params_annotation['datahora'].append(vela[INDICE_K])
                    
                    #-----------------------
                    #----- Debug print -----
                    #-----------------------
                    print('Entrada, compra.')
                    print('Hora da entrada: ' + vela[INDICE_TH])
                    print('Preço de entrada: ' + str(vela[INDICE_C]))
                    print('Preço de take profit: ' + str(self.take_profit))
                    print('Preço de stop loss: ' + str(self.stop_loss))
                    print('Aporte: ' + str(self.aporte))
                    print('Saldo após aporte: ' + str(self.saldo))
                    print('===========================================')
                    
                    break
                        
                elif (elem <= self.gatilho_entrada) and self.flag_sbar_venda and not(self.flag_entrou):
                    
                    self.flag_entrou = True
                    
                    # Utilizando MMH como stop loss.
                    self.stop_loss = vela[INDICE_MH]
                    
                    if self.saldo >= 100:
                        self.aporte = 100
                        self.saldo -= 100
                    else:
                        # Variável auxiliar para diminuir a expressão.
                        self.aporte_aux = self.stop_loss - elem
                        # Resultado é em pontos, e cada ponto vale R$10 (ativo WDOL).
                        # Se for tal que o aporte seja maior que R$100, o mesmo fica
                        # limitado a R$100.
                        self.aporte = 10*self.aporte_aux if self.aporte_aux < 10 else 100
                        self.saldo -= 10*self.aporte_aux if self.aporte_aux < 10 else 100
                         
                    self.aux_take_profit = self.stop_loss - elem
                    self.take_profit = elem - FATOR_LUCRO * self.aux_take_profit
                    
                    self.d_params_annotation['texto'].append('E V')
                    self.d_params_annotation['y_annot'].append(elem)
                    self.d_params_annotation['ytext_annot'].append(elem-10)
                    self.d_params_annotation['datahora'].append(vela[INDICE_K])
                    
                    #-----------------------
                    #----- Debug print -----
                    #-----------------------
                    print('Entrada, venda.')
                    print('Hora da entrada: ' + vela[INDICE_TH])
                    print('Preço de entrada: ' + str(vela[INDICE_C]))
                    print('Preço de take profit: ' + str(self.take_profit))
                    print('Preço de stop loss: ' + str(self.stop_loss))
                    print('Aporte: ' + str(self.aporte))
                    print('Saldo após aporte: ' + str(self.saldo))
                    print('===========================================')
                    
                    break                
                
            #*************************************************
            #***** Fim do código para entrar na operação *****
            #*************************************************
            
            #******************************************
            #***** Código para canclear o setup *******
            #******************************************
            
            if not(self.flag_entrou) and (self.flag_sbar_compra or self.flag_sbar_venda):
                
                self.tol_pos_sbar += 1
                
                if self.tol_pos_sbar == TOLERANCIA_POS_SBAR:
                    self.tol_pos_sbar = 0
                    self.flag_sbar_compra = False
                    self.flag_sbar_venda = False
                    continue
                
            #**************************************************
            #*****  Fim do código para canclear o setup *******
            #**************************************************
                
            #******************************************
            #***** Código para sair da operação *******
            #******************************************
            
            if self.flag_entrou:
                
                # Atualiza o stop loss.
                if self.flag_sbar_compra:
                    self.stop_loss = vela[INDICE_ML] 
                else:
                    self.stop_loss = vela[INDICE_MH]
                
                for elem in vela[INDICE_O : INDICE_C+1]:
                    
                    if self.flag_sbar_compra and (elem > self.take_profit):

                        self.saldo += self.aporte + elem - self.gatilho_entrada
                        self.ohlc_aux = []
                        self.flag_entrou = False
                        self.flag_sbar_compra = False
                        self.cont_verdes = 0
                        self.cont_vermelhas = 0
                        
                        self.d_params_annotation['texto'].append('S C, TP')
                        self.d_params_annotation['y_annot'].append(vela[INDICE_C])
                        self.d_params_annotation['ytext_annot'].append(vela[INDICE_C]-10)
                        self.d_params_annotation['datahora'].append(vela[INDICE_K])
                
                        #-----------------------
                        #----- Debug print -----
                        #-----------------------
                        print('Saída de compra, take profit.')
                        print('Hora da saída: ' + vela[INDICE_TH])
                        print('Saldo após saída: ' + str(self.saldo))
                        print('===========================================')
                        
                        break
                    
                    elif self.flag_sbar_compra and (elem < self.stop_loss):

                        self.ohlc_aux = []
                        self.flag_entrou = False
                        self.flag_sbar_compra = False
                        self.cont_verdes = 0
                        self.cont_vermelhas = 0
                        
                        self.d_params_annotation['texto'].append('S C, SL')
                        self.d_params_annotation['y_annot'].append(elem)
                        self.d_params_annotation['ytext_annot'].append(elem-15)
                        self.d_params_annotation['datahora'].append(vela[INDICE_K])
                        
                        #-----------------------
                        #----- Debug print -----
                        #-----------------------
                        print('Saída de compra, stop loss.')
                        print('Hora da saída: ' + vela[INDICE_TH])
                        print('Saldo após saída: ' + str(self.saldo))
                        print('===========================================')
                        
                        break
                    
                    elif self.flag_sbar_venda and (elem < self.take_profit):

                        self.saldo += self.aporte + self.gatilho_entrada - elem
                        self.ohlc_aux = []
                        self.flag_entrou = False # Indica saída do trade.
                        self.flag_sbar_venda = False
                        self.cont_verdes = 0
                        self.cont_vermelhas = 0
                        
                        self.d_params_annotation['texto'].append('S V, TP')
                        self.d_params_annotation['y_annot'].append(elem)
                        self.d_params_annotation['ytext_annot'].append(elem-15)
                        self.d_params_annotation['datahora'].append(vela[INDICE_K])
                        
                        #-----------------------
                        #----- Debug print -----
                        #-----------------------
                        print('Saída de venda, take profit.')
                        print('Hora da saída: ' + vela[INDICE_TH])
                        print('Saldo após saída: ' + str(self.saldo))
                        print('===========================================')
                        
                        break
                    
                    elif self.flag_sbar_venda and (elem > self.stop_loss):

                        self.ohlc_aux = []
                        self.flag_entrou = False
                        self.flag_sbar_venda = False
                        self.cont_verdes = 0
                        self.cont_vermelhas = 0
                        
                        self.d_params_annotation['texto'].append('S V, SL')
                        self.d_params_annotation['y_annot'].append(elem)
                        self.d_params_annotation['ytext_annot'].append(elem-15)
                        self.d_params_annotation['datahora'].append(vela[INDICE_K])
                        
                        #-----------------------
                        #----- Debug print -----
                        #-----------------------
                        print('Saída de venda, stop loss.')
                        print('Hora da saída: ' + vela[INDICE_TH])
                        print('Saldo após saída: ' + str(self.saldo))
                        print('===========================================')
                        
                        break
                    
        #************************************************
        #***** Fim do código para sair da operação. *****
        #************************************************
            
            self.C_ultima_vela = vela[INDICE_C]
            
        return self.d_params_annotation