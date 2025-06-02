#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import tkinter.simpledialog
from datetime import *
import serial
import time
import random
import _thread
from smtplib import SMTP_SSL as SMTP
import logging, logging.handlers, sys
from email.mime.text import MIMEText

import gspread
from oauth2client.service_account import ServiceAccountCredentials

TITLE_FONT = ("Helvetica", 18, "bold")
LABEL_FONT = ("Verdana", 18, "bold")
serial_speed = 9600
arquivo ='lista_sepultados.csv'
serial_port = '/dev/ttyUSB0'
#serial_port = '/dev/rfcomm0'
#serial_port = 'COM9'
ser = serial.Serial(serial_port, serial_speed, timeout=1)


class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        #tk.Tk.iconbitmap(self, default="ICO.ico")
        #tk.Tk.geometry(self,"800x480+0+0")
        tk.Tk.attributes(self,'-fullscreen', True)
        tk.Tk.wm_title(self, "MCC - MÓDULO DE CONTROLE E COMANDO")
        #'''Declaração das variáveis'''
        self.var_temp = tk.StringVar()
        self.var_hum = tk.StringVar()
        self.var_freq = tk.StringVar()
        self.var_press = tk.StringVar()
        self.var_data = tk.StringVar()
        self.var_hora = tk.StringVar()
        self.var_status = tk.StringVar()
        self.var_efic = tk.StringVar()
        self.var_ocup = tk.StringVar()
        #self.var_status = tk.StringVar()
        #self.Porta()
        #self.Menu()       
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)        
        self.receber_dados()  
        self.font5 = "-family {Segoe UI} -size 14 -weight bold -slant "  \
            "roman -underline 0 -overstrike 0"
        self.frames = {}
        '''
        for F in (StartPage, PageOne,
                  PageTwo
                  ):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)
        '''
        frame = StartPage(container, self)
        frame_ = PageOne(container, self)

        self.frames[StartPage] = frame
        self.frames[PageOne] = frame_

        frame.grid(row=0, column=0, sticky="nsew")
        frame_.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def get_page(self, page_class):
        return self.frames[page_class]

    
    def show_frame(self, c):
        frame = self.frames[c]
        frame.tkraise()


    def receber_dados(self):
                '''
                    #VARIÁVEIS
                    #self.var_temp = tk.StringVar()
                    #self.var_hum = tk.StringVar()
                    #self.var_freq = tk.StringVar()
                    #self.var_press = tk.StringVar()
                    #self.var_temp = tk.StringVar()
                    #self.var_data = tk.StringVar()
                    #self.var_hora = tk.StringVar()
                    #self.var_status = tk.StringVar()
                '''
                    #if hasattr (self, 'ser'): # checa se o objeto self tem o atributo "ser" (ou seja, se a porta foi definida)
                      
                try:
##                    arq = open(arquivo, 'r')
##                    lido = arq.readlines()                      
##                    arq.close()
                    self.ser_read = ser.readline().decode("utf-8")
                    self.ser_read = self.ser_read[:-1] # retira o \n (newline) 
                    self.ser_read = self.ser_read[:-1] # retira o \o (endline)

##                    print(self.ser_read)
                    if self.ser_read.startswith('<') and self.ser_read.endswith('>'):
                        #print(self.ser_read)
                        
                        self.ser_read = str(self.ser_read)
                        self.ser_read = self.ser_read.split(",")
                        self.var_temp.set(self.ser_read[0][1:]) #retira o primeiro caracter da string
                        self.var_hum.set(self.ser_read[1])
                        self.var_press.set(self.ser_read[2])
                        self.var_freq.set(self.ser_read[3])                    
                        self.var_data.set(self.ser_read[6])
                        self.var_hora.set(self.ser_read[7][:-1])#retira o ultimo caracter da string
                        

                    if self.ser_read.startswith('(') and self.ser_read.endswith(')'):
                        self.ser_read = self.ser_read[1:] # retira o ( (abre parentese)
                        self.ser_read = self.ser_read[:-1] # retira o ) (fecha parentese)            
                                           
                        self.var_status.set(self.ser_read)
                        if 'PROBLEMA' in self.ser_read:
                            time.sleep(3)
                            self._var_status.set(" ")
                        #print(self.ser_read)

                    if self.ser_read.startswith('[') and self.ser_read.endswith(']'):
                        self.ser_read = self.ser_read[1:] # retira o '[' (abre colchete)
                        self.ser_read = self.ser_read[:-1] # retira o ']' (fecha colchete)
          

                        if "marca" in self.ser_read: #armazena o início da troca gasosa
                                
                                global dia
                                global data
                                global hora
                                hoje = datetime.now()
                                dias = ('Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom')
                                dia = dias[hoje.weekday()]
                                data = hoje.strftime('%d/%m/%Y')
                                hora = hoje.strftime('%T')
                               

                        #if "sucesso" in self.ser_read:
                        #    now = datetime.datetime.now()
                        #    self.envia_Email("MCC - ZÉ DO CAIXÃO: Troca gasosa realizada com sucesso  "+str(now))

                        if "media" in self.ser_read: # início da troca gasosa
                       
                            dados = self.ser_read                                                         
                                           
                            self.registra_planilha("MCC_SANTA_BARBARA",dados)


                except:
                        pass            
                self.after(100,self.receber_dados)

    def envia_Email(self,texto):
        
        
        try:
            logger = logging.getLogger("__main__")
            logger.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            to=["vremapedro@gmail.com","pedrosilva@vilatec.com.br"]    #Recipient's email address
            frm="vremapedro@gmail.com"                      #Sender's email address
            pswd="nbr5410!"                     #Sender's password
            sub="MCC - ZÉ DO CAIXÃO"                      #Subject of email
            text=texto                  #Message to send
            msg = MIMEText(text, 'plain')
            msg['Subject'] = sub
            msg['To'] =  ", ".join(to)
        except Exception as err:
            pass

        try:
            conn = SMTP("smtp.gmail.com")
            conn.set_debuglevel(True)
            conn.login(frm, pswd)
            try: conn.sendmail(frm, to, msg.as_string())
            finally: conn.close()
        except Exception as exc:
            print(exc)
            logger.error("ERROR!!!")
            logger.critical(exc)
            sys.exit("Mail failed: {}".format(exc))
    
    def registra_planilha(self,texto,dados):
        global dia
        global data
        global hora
        dados = dados.split(",")
        media = dados[2]
        if dados[1] == "troca":
            altera = "troca.txt"
            coluna = 1
        if dados[1] == "teste":
            altera = "teste.txt"
            coluna = 7
        arq = open(altera, 'r')
        file_lines = arq.readlines()
        arq.close()
        if len(file_lines) > 0:
            last_line = file_lines [ len ( file_lines ) -1]        
            last_line = last_line.split("\t")
            last_line = int(last_line[0])            
        else:
            last_line = 3            
        mais_uma_linha = int(last_line)+1
        hoje = datetime.now()        
        arq = open(altera, 'a')        
        arq.writelines("\n"+str(mais_uma_linha)+"\t" + dia + "\t" + data + "\t" + hora + "\t" + hoje.strftime('%X'))
        arq.close()
                
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        sheet = client.open(texto).sheet1
        
        sheet.update_cell(mais_uma_linha, coluna, dia) #ATUALIZA CÉLULA ESPECÍFICA
        sheet.update_cell(mais_uma_linha, coluna+1, data) #ATUALIZA CÉLULA ESPECÍFICA
        sheet.update_cell(mais_uma_linha, coluna+2, hora) #ATUALIZA CÉLULA ESPECÍFICA       
        sheet.update_cell(mais_uma_linha, coluna+3, hoje.strftime('%T')) #ATUALIZA CÉLULA ESPECÍFICA
        sheet.update_cell(mais_uma_linha, coluna+4, media) #ATUALIZA CÉLULA ESPECÍFICA
        
        
        
          
class StartPage(tk.Frame):
    def __init__(self, parent, controller):

        self.font5 = "-family {Segoe UI} -size 14 -weight bold -slant "  \
            "roman -underline 0 -overstrike 0"
        self.font6 = "-family {Segoe UI} -size 12 -weight normal "  \
            "-slant roman -underline 0 -overstrike 0"
        self.font7 = "-family {Segoe UI} -size 12 -weight bold -slant "  \
            "roman -underline 0 -overstrike 0"
        self.font9 = "-family {Segoe UI} -size 10 -weight normal "  \
            "-slant roman -underline 0 -overstrike 0"
        self.controller=controller        
        tk.Frame.__init__(self, parent)
        tk.Frame.configure(self,background="#d9d9d9")
        tk.Frame.configure(self,highlightbackground="#d9d9d9")
        tk.Frame.configure(self,highlightcolor="black")
        
        self.label = tk.Label(self, text="MCC-MÓDULO DE CONTROLE E COMANDO", font=TITLE_FONT)
        self.label.configure(relief='groove')
        self.label.configure(fg='green')
        self.label.configure(height=None,width=60) #não aumentar a quantidade de linhas
        self.label.configure(background="#d9d9d9")
        self.label.configure(highlightbackground="#d9d9d9")
        self.label.configure(highlightcolor="black")
        self.label.place(relx=0.1, rely=0.0, height=34, width=600)

        

        self.Button1 = tk.Button(self)
        self.Button1.place(relx=0.02, rely=0.8, height=34, width=150)
        self.Button1.configure(activebackground="#d9d9d9")
        self.Button1.configure(activeforeground="#000000")
        self.Button1.configure(background="#d9d9d9")
        self.Button1.configure(command=self.teste_de_pressao)
        self.Button1.configure(disabledforeground="#a3a3a3")
        self.Button1.configure(font=self.font6)
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="black")
        self.Button1.configure(pady="0")
        self.Button1.configure(takefocus="0")
        self.Button1.configure(text='''Teste de pressão''')

        self.btn_abrevalvula = tk.Button(self)
        #self.btn_abrevalvula.place(relx=0.22, rely=0.8, height=34, width=150)
        self.btn_abrevalvula.configure(activebackground="#d9d9d9")
        self.btn_abrevalvula.configure(activeforeground="#000000")
        self.btn_abrevalvula.configure(background="#d9d9d9")
        self.btn_abrevalvula.configure(command=self.abre_valvula)
        self.btn_abrevalvula.configure(disabledforeground="#a3a3a3")
        self.btn_abrevalvula.configure(font=self.font6)
        self.btn_abrevalvula.configure(foreground="#000000")
        self.btn_abrevalvula.configure(highlightbackground="#d9d9d9")
        self.btn_abrevalvula.configure(highlightcolor="black")
        self.btn_abrevalvula.configure(pady="0")
        self.btn_abrevalvula.configure(takefocus="0")
        self.btn_abrevalvula.configure(text='''Abre valvula''')

        self.btn_fechavalvula = tk.Button(self)
        #self.btn_fechavalvula.place(relx=0.22, rely=0.9, height=34, width=150)
        self.btn_fechavalvula.configure(activebackground="#d9d9d9")
        self.btn_fechavalvula.configure(activeforeground="#000000")
        self.btn_fechavalvula.configure(background="#d9d9d9")
        self.btn_fechavalvula.configure(command=self.fecha_valvula)
        self.btn_fechavalvula.configure(disabledforeground="#a3a3a3")
        self.btn_fechavalvula.configure(font=self.font6)
        self.btn_fechavalvula.configure(foreground="#000000")
        self.btn_fechavalvula.configure(highlightbackground="#d9d9d9")
        self.btn_fechavalvula.configure(highlightcolor="black")
        self.btn_fechavalvula.configure(pady="0")
        self.btn_fechavalvula.configure(takefocus="0")
        self.btn_fechavalvula.configure(text='''Fecha valvula''')

        self.Label2 = tk.Label(self)
        self.Label2.place(relx=0.03, rely=0.10, height=41, width=194)
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(activeforeground="black")
        self.Label2.configure(background="#d9d9d9")
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(font=self.font5)
        self.Label2.configure(foreground="#0000ff")
        self.Label2.configure(highlightbackground="#d9d9d9")
        self.Label2.configure(highlightcolor="black")
        self.Label2.configure(relief="groove")
        self.Label2.configure(text='''TEMPERATURA''')

        self.Label3 = tk.Label(self)
        self.Label3.place(relx=0.03, rely=0.20, height=41, width=194)
        self.Label3.configure(activebackground="#f9f9f9")
        self.Label3.configure(activeforeground="black")
        self.Label3.configure(background="#d9d9d9")
        self.Label3.configure(disabledforeground="#a3a3a3")
        self.Label3.configure(font=self.font5)
        self.Label3.configure(foreground="#0000ff")
        self.Label3.configure(highlightbackground="#d9d9d9")
        self.Label3.configure(highlightcolor="black")
        self.Label3.configure(relief="groove")
        self.Label3.configure(text='''PRESSÃO''')

        self.Label4 = tk.Label(self)
        self.Label4.place(relx=0.03, rely=0.30, height=41, width=194)
        self.Label4.configure(activebackground="#f9f9f9")
        self.Label4.configure(activeforeground="black")
        self.Label4.configure(background="#d9d9d9")
        self.Label4.configure(disabledforeground="#a3a3a3")
        self.Label4.configure(font=self.font5)
        self.Label4.configure(foreground="#0000ff")
        self.Label4.configure(highlightbackground="#d9d9d9")
        self.Label4.configure(highlightcolor="black")
        self.Label4.configure(relief='groove')
        self.Label4.configure(text='''FREQUÊNCIA''')

        self.Label5 = tk.Label(self)
        self.Label5.place(relx=0.03, rely=0.40, height=41, width=194)
        self.Label5.configure(activebackground="#f9f9f9")
        self.Label5.configure(activeforeground="black")
        self.Label5.configure(background="#d9d9d9")
        self.Label5.configure(disabledforeground="#a3a3a3")
        self.Label5.configure(font=self.font5)
        self.Label5.configure(foreground="#0000ff")
        self.Label5.configure(highlightbackground="#d9d9d9")
        self.Label5.configure(highlightcolor="black")
        self.Label5.configure(relief='groove')
        self.Label5.configure(text='''UMIDADE''')
        '''
        self.Label_eficiencia = tk.Label(self)
        self.Label_eficiencia.place(relx=0.03, rely=0.50, height=41, width=194)
        self.Label_eficiencia.configure(activebackground="#f9f9f9")
        self.Label_eficiencia.configure(activeforeground="black")
        self.Label_eficiencia.configure(background="#d9d9d9")
        self.Label_eficiencia.configure(disabledforeground="#a3a3a3")
        self.Label_eficiencia.configure(font=self.font5)
        self.Label_eficiencia.configure(foreground="#0000ff")
        self.Label_eficiencia.configure(highlightbackground="#d9d9d9")
        self.Label_eficiencia.configure(highlightcolor="black")
        self.Label_eficiencia.configure(relief='groove')
        '''#self.Label_eficiencia.configure(text='''EFICIÊNCIA''')
        

        self.Label_total_sepultados = tk.Label(self)
        self.Label_total_sepultados.place(relx=0.03, rely=0.60, height=41, width=194)
        self.Label_total_sepultados.configure(activebackground="#f9f9f9")
        self.Label_total_sepultados.configure(activeforeground="black")
        self.Label_total_sepultados.configure(background="#d9d9d9")
        self.Label_total_sepultados.configure(disabledforeground="#a3a3a3")
        self.Label_total_sepultados.configure(font=self.font5)
        self.Label_total_sepultados.configure(foreground="#0000ff")
        self.Label_total_sepultados.configure(highlightbackground="#d9d9d9")
        self.Label_total_sepultados.configure(highlightcolor="black")
        self.Label_total_sepultados.configure(relief='groove')
        self.Label_total_sepultados.configure(text='''OCUPAÇÃO''')


        #VAR_TEMPERATURA
        self.Label6 = tk.Label(self)
        self.Label6.place(relx=0.31, rely=0.10, height=41, width=104)
        self.Label6.configure(activebackground="#f9f9f9")
        self.Label6.configure(activeforeground="black")
        self.Label6.configure(background="#ffffff")
        self.Label6.configure(disabledforeground="#a3a3a3")
        self.Label6.configure(font=self.font5)
        self.Label6.configure(foreground="#b43fc0")
        self.Label6.configure(highlightbackground="#d9d9d9")
        self.Label6.configure(highlightcolor="black")
        self.Label6.configure(relief='groove')
        self.Label6.configure(textvariable=self.controller.var_temp)

        #VAR_PRESSAO
        self.Label7 = tk.Label(self)
        self.Label7.place(relx=0.31, rely=0.20, height=41, width=104)
        self.Label7.configure(activebackground="#f9f9f9")
        self.Label7.configure(activeforeground="black")
        self.Label7.configure(background="#ffffff")
        self.Label7.configure(disabledforeground="#a3a3a3")
        self.Label7.configure(font=self.font5)
        self.Label7.configure(foreground="#b43fc0")
        self.Label7.configure(highlightbackground="#d9d9d9")
        self.Label7.configure(highlightcolor="black")
        self.Label7.configure(relief='groove')
        self.Label7.configure(textvariable=self.controller.var_press)

        #VAR_FREQUENCIA
        self.Label8 = tk.Label(self)
        self.Label8.place(relx=0.31, rely=0.30, height=41, width=104)
        self.Label8.configure(activebackground="#f9f9f9")
        self.Label8.configure(activeforeground="black")
        self.Label8.configure(background="#ffffff")
        self.Label8.configure(disabledforeground="#a3a3a3")
        self.Label8.configure(font=self.font5)
        self.Label8.configure(foreground="#b43fc0")
        self.Label8.configure(highlightbackground="#d9d9d9")
        self.Label8.configure(highlightcolor="black")
        self.Label8.configure(relief='groove')
        self.Label8.configure(textvariable=self.controller.var_freq)

        #VAR_HUM
        self.Label9 = tk.Label(self)
        self.Label9.place(relx=0.31, rely=0.40, height=41, width=104)
        self.Label9.configure(activebackground="#f9f9f9")
        self.Label9.configure(activeforeground="black")
        self.Label9.configure(background="#ffffff")
        self.Label9.configure(disabledforeground="#a3a3a3")
        self.Label9.configure(font=self.font5)
        self.Label9.configure(foreground="#b43fc0")
        self.Label9.configure(highlightbackground="#d9d9d9")
        self.Label9.configure(highlightcolor="black")
        self.Label9.configure(relief='groove')
        self.Label9.configure(textvariable=self.controller.var_hum)

        #VAR_EFICIENCIA
        self.Label_var_efic = tk.Label(self)
        #self.Label_var_efic.place(relx=0.31, rely=0.50, height=41, width=104)
        self.Label_var_efic.configure(activebackground="#f9f9f9")
        self.Label_var_efic.configure(activeforeground="black")
        self.Label_var_efic.configure(background="#ffffff")
        self.Label_var_efic.configure(disabledforeground="#a3a3a3")
        self.Label_var_efic.configure(font=self.font5)
        self.Label_var_efic.configure(foreground="#b43fc0")
        self.Label_var_efic.configure(highlightbackground="#d9d9d9")
        self.Label_var_efic.configure(highlightcolor="black")
        self.Label_var_efic.configure(relief='groove')
        self.Label_var_efic.configure(textvariable=self.controller.var_efic)

        #VAR_OCUPAÇÃO
        self.Label_var_ocup = tk.Label(self)
        self.Label_var_ocup.place(relx=0.31, rely=0.60, height=41, width=104)
        self.Label_var_ocup.configure(activebackground="#f9f9f9")
        self.Label_var_ocup.configure(activeforeground="black")
        self.Label_var_ocup.configure(background="#ffffff")
        self.Label_var_ocup.configure(disabledforeground="#a3a3a3")
        self.Label_var_ocup.configure(font=self.font5)
        self.Label_var_ocup.configure(foreground="#b43fc0")
        self.Label_var_ocup.configure(highlightbackground="#d9d9d9")
        self.Label_var_ocup.configure(highlightcolor="black")
        self.Label_var_ocup.configure(relief='groove')
        self.Label_var_ocup.configure(textvariable=self.controller.var_ocup)


        self.Label10 = tk.Label(self)
        self.Label10.place(relx=0.44, rely=0.12, height=27, width=22)
        self.Label10.configure(activebackground="#f9f9f9")
        self.Label10.configure(activeforeground="black")
        self.Label10.configure(background="#d9d9d9")
        self.Label10.configure(disabledforeground="#a3a3a3")
        self.Label10.configure(font=self.font7)
        self.Label10.configure(foreground="#000000")
        self.Label10.configure(highlightbackground="#d9d9d9")
        self.Label10.configure(highlightcolor="black")
        self.Label10.configure(text='''°C''')

        self.Label11 = tk.Label(self)
        self.Label11.place(relx=0.45, rely=0.42, height=27, width=35)
        self.Label11.configure(activebackground="#f9f9f9")
        self.Label11.configure(activeforeground="black")
        self.Label11.configure(background="#d9d9d9")
        self.Label11.configure(disabledforeground="#a3a3a3")
        self.Label11.configure(font=self.font7)
        self.Label11.configure(foreground="#000000")
        self.Label11.configure(highlightbackground="#d9d9d9")
        self.Label11.configure(highlightcolor="black")
        self.Label11.configure(text='''RH%''')

        self.Label12 = tk.Label(self)
        self.Label12.place(relx=0.44, rely=0.32, height=27, width=32)
        self.Label12.configure(activebackground="#f9f9f9")
        self.Label12.configure(activeforeground="black")
        self.Label12.configure(background="#d9d9d9")
        self.Label12.configure(disabledforeground="#a3a3a3")
        self.Label12.configure(font=self.font7)
        self.Label12.configure(foreground="#000000")
        self.Label12.configure(highlightbackground="#d9d9d9")
        self.Label12.configure(highlightcolor="black")
        self.Label12.configure(text='''Hz''')

        self.Label13 = tk.Label(self)
        self.Label13.place(relx=0.45, rely=0.22, height=27, width=70)
        self.Label13.configure(activebackground="#f9f9f9")
        self.Label13.configure(activeforeground="black")
        self.Label13.configure(background="#d9d9d9")
        self.Label13.configure(disabledforeground="#a3a3a3")
        self.Label13.configure(font=self.font7)
        self.Label13.configure(foreground="#000000")
        self.Label13.configure(highlightbackground="#d9d9d9")
        self.Label13.configure(highlightcolor="black")
        self.Label13.configure(text='''mmH2O''')

        '''
        self.Label13 = tk.Label(self)
        self.Label13.place(relx=0.45, rely=0.52, height=27, width=24)
        self.Label13.configure(activebackground="#f9f9f9")
        self.Label13.configure(activeforeground="black")
        self.Label13.configure(background="#d9d9d9")
        self.Label13.configure(disabledforeground="#a3a3a3")
        self.Label13.configure(font=self.font7)
        self.Label13.configure(foreground="#000000")
        self.Label13.configure(highlightbackground="#d9d9d9")
        self.Label13.configure(highlightcolor="black")
        '''#self.Label13.configure(text='''%''')        


        self.Label13 = tk.Label(self)
        self.Label13.place(relx=0.45, rely=0.62, height=27, width=65)
        self.Label13.configure(activebackground="#f9f9f9")
        self.Label13.configure(activeforeground="black")
        self.Label13.configure(background="#d9d9d9")
        self.Label13.configure(disabledforeground="#a3a3a3")
        self.Label13.configure(font=self.font7)
        self.Label13.configure(foreground="#000000")
        self.Label13.configure(highlightbackground="#d9d9d9")
        self.Label13.configure(highlightcolor="black")
        self.Label13.configure(text='''Lóculos''')        
        
        self.Label14 = tk.Label(self)
        self.Label14.place(relx=0.62, rely=0.17, height=211, width=244)
        self.Label14.configure(activebackground="#f9f9f9")
        self.Label14.configure(activeforeground="black")
        self.Label14.configure(background="#d9d9d9")
        self.Label14.configure(disabledforeground="#a3a3a3")
        self.Label14.configure(foreground="#000000")
        self.Label14.configure(highlightbackground="#d9d9d9")
        self.Label14.configure(highlightcolor="black")
        self._img1 = tk.PhotoImage(file="LOGO_CEM.png")
        self.Label14.configure(image=self._img1)        
        self.Label14.configure(text='''Label''')

        self.Label15 = tk.Label(self)
        self.Label15.place(relx=0.41, rely=0.91, height=31, width=134)
        self.Label15.configure(activebackground="#f9f9f9")
        self.Label15.configure(activeforeground="black")
        self.Label15.configure(background="#d9d9d9")
        self.Label15.configure(disabledforeground="#a3a3a3")
        self.Label15.configure(foreground="#000000")
        self.Label15.configure(highlightbackground="#d9d9d9")
        self.Label15.configure(highlightcolor="black")
        self._img2 = PhotoImage(file="LOGO_VILATEC.png")
        self.Label15.configure(image=self._img2)
        self.Label15.configure(text='''Label''')

        self.Label16 = tk.Label(self)
        self.Label16.place(relx=0.85, rely=0.92, height=21, width=100)
        self.Label16.configure(activebackground="#f9f9f9")
        self.Label16.configure(activeforeground="black")
        self.Label16.configure(background="#d9d9d9")
        self.Label16.configure(disabledforeground="#a3a3a3")
        self.Label16.configure(font=self.font6)
        self.Label16.configure(foreground="#000000")
        self.Label16.configure(highlightbackground="#d9d9d9")
        self.Label16.configure(highlightcolor="black")
        #self.Label16.configure(text='''29/06/1982''')
        self.Label16.configure(textvariable=self.controller.var_data)

        self.Label17 = tk.Label(self)
        self.Label17.place(relx=0.85, rely=0.88, height=21, width=100)
        self.Label17.configure(activebackground="#f9f9f9")
        self.Label17.configure(activeforeground="black")
        self.Label17.configure(background="#d9d9d9")
        self.Label17.configure(disabledforeground="#a3a3a3")
        self.Label17.configure(font=self.font6)
        self.Label17.configure(foreground="#000000")
        self.Label17.configure(highlightbackground="#d9d9d9")
        self.Label17.configure(highlightcolor="black")
        #self.Label17.configure(text='''10:47''')
        self.Label17.configure(textvariable=self.controller.var_hora)
#LABEL STATUS RETORNADO DO ARDUINO
        self.Label18 = tk.Label(self)
        self.Label18.place(relx=0.4, rely=0.8, height=25, width=430)
        self.Label18.configure(activebackground="#f9f9f9")
        self.Label18.configure(activeforeground="black")
        self.Label18.configure(background="#d9d9d9")
        self.Label18.configure(disabledforeground="#a3a3a3")
        self.Label18.configure(font=self.font5)
        
        self.Label18.configure(foreground="#000000")
        self.Label18.configure(highlightbackground="#d9d9d9")
        self.Label18.configure(highlightcolor="black")
        self.Label18.configure(text='''10:47''')
        self.Label18.configure(textvariable=self.controller.var_status)        
        

        self.button1 = tk.Button(self)        
        self.button1.place(relx=0.02, rely=0.9, height=34, width=150)
        self.button1.configure(activebackground="#d9d9d9")
        self.button1.configure(activeforeground="#000000")
        self.button1.configure(background="#d9d9d9")
        self.button1.configure(command=lambda: controller.show_frame(PageOne))
        self.button1.configure(disabledforeground="#a3a3a3")
        self.button1.configure(font=self.font6)
        self.button1.configure(foreground="#000000")
        self.button1.configure(highlightbackground="#d9d9d9")
        self.button1.configure(highlightcolor="black")
        self.button1.configure(pady="0")
        self.button1.configure(takefocus="0")
        self.button1.configure(text='''Cadastro''')
        
    def teste_de_pressao(self):
##       ser.write(b'TURBINA 255\n')
        ser.write(b'TESTE\n')
        

    def abre_valvula(self):
       ser.write(b'A_V\n')
       print("abre")
       
    def fecha_valvula(self):
       ser.write(b'F_V\n')
       print("fecha")
       

    #def setVarSpin1(self,v):
    
        

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.configure(self,background="#d9d9d9")
        tk.Frame.configure(self,highlightbackground="#d9d9d9")
        tk.Frame.configure(self,highlightcolor="black")
        
        self.entry_inclui_loculo = tk.StringVar()
        self.entry_inclui_sepultado = tk.StringVar()
        self.entry_inclui_data = tk.StringVar()
        self.listBox_sepultados = tk.StringVar()
        

        
        self.font4 = "-family {Courier New} -size 12 -weight bold "  \
            "-slant roman -underline 0 -overstrike 0"
        self.font5 = "-family {Segoe UI} -size 14 -weight bold -slant "  \
            "roman -underline 0 -overstrike 0"
        self.font6 = "-family {Segoe UI} -size 12 -weight normal "  \
            "-slant roman -underline 0 -overstrike 0"
        self.font7 = "-family {Segoe UI} -size 12 -weight bold -slant "  \
            "roman -underline 0 -overstrike 0"
        self.font9 = "-family {Segoe UI} -size 12 -weight bold "  \
            "-slant roman -underline 0 -overstrike 0"
        
        self.controller=controller
        
        self.Listbox1 = tk.Listbox(self)
        self.Listbox1.place(relx=0.03, rely=0.51, relheight=0.34, relwidth=0.95)
        self.scrollbar = tk.Scrollbar(self.Listbox1, orient=VERTICAL)
        #self.scrollbar.place(relx=0.1, rely=0.05, relheight=1.0,relwidth=0.02)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.scrollbar['command'] = self.Listbox1.yview
        self.Listbox1.config(yscrollcommand=self.scrollbar.set)
        self.Listbox1.configure(background="white")
        self.Listbox1.configure(disabledforeground="#a3a3a3")
        self.Listbox1.configure(font=self.font4)
        self.Listbox1.configure(foreground="#000000")
        self.Listbox1.configure(highlightbackground="#d9d9d9")
        self.Listbox1.configure(highlightcolor="black")
        self.Listbox1.configure(selectbackground="#c4c4c4")
        self.Listbox1.configure(selectforeground="black")
        self.Listbox1.configure(width=744)
        self.Listbox1.configure(listvariable=self.listBox_sepultados)
        self.Listbox1.bind('<Double-1>',self.onselect)

        arq = open(arquivo, 'r')
        lido = arq.readlines()
        self.controller.var_ocup.set(len(lido))
        for x in range(len(lido)):
            retira_nl = lido[x][:-1]
            self.Listbox1.insert(END, retira_nl)            
        #self.listBox_sepultados.set(tuple(lido))
        arq.close()
       

        self.Button2 = tk.Button(self)
        self.Button2.place(relx=0.03, rely=0.87, height=34, width=137)
        self.Button2.configure(activebackground="#d9d9d9")
        self.Button2.configure(activeforeground="#000000")
        self.Button2.configure(background="#d9d9d9")
        self.Button2.configure(command=lambda: controller.show_frame(StartPage))
        self.Button2.configure(disabledforeground="#a3a3a3")
        self.Button2.configure(foreground="#000000")
        self.Button2.configure(highlightbackground="#d9d9d9")
        self.Button2.configure(highlightcolor="black")
        self.Button2.configure(pady="0")
        self.Button2.configure(text='''Voltar''')
        self.Button2.configure(width=137)

        self.Frame1 = tk.Frame(self)
        self.Frame1.configure(background="#d9d9d9")
        self.Frame1.configure(highlightbackground="#d9d9d9")
        self.Frame1.configure(highlightcolor="black")
        self.Frame1.place(relx=0.06, rely=0.1, relheight=0.32, relwidth=0.81)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")        
        self.Frame1.configure(background="#d9d9d9")
        self.Frame1.configure(width=635)

        self.Label19 = tk.Label(self.Frame1)
        self.Label19.place(relx=0.01, rely=0.32, height=21, width=200)
        self.Label19.configure(background="#d9d9d9")
        self.Label19.configure(disabledforeground="#a3a3a3")
        self.Label19.configure(font=self.font9)
        self.Label19.configure(foreground="#000000")
        self.Label19.configure(text='''Data de Sepultamento''')
        self.Label19.configure(width=133)

        self.Label20 = tk.Label(self.Frame1)
        self.Label20.place(relx=0.01, rely=0.07, height=21, width=49)
        self.Label20.configure(activebackground="#f9f9f9")
        self.Label20.configure(activeforeground="black")
        self.Label20.configure(background="#d9d9d9")
        self.Label20.configure(disabledforeground="#a3a3a3")
        self.Label20.configure(font=self.font9)
        self.Label20.configure(foreground="#000000")
        self.Label20.configure(highlightbackground="#d9d9d9")
        self.Label20.configure(highlightcolor="black")
        self.Label20.configure(text='''Nome''')
        self.Label20.configure(width=49)

        self.Label21 = tk.Label(self.Frame1)
        self.Label21.place(relx=0.58, rely=0.32, height=21, width=55)
        self.Label21.configure(activebackground="#f9f9f9")
        self.Label21.configure(activeforeground="black")
        self.Label21.configure(background="#d9d9d9")
        self.Label21.configure(disabledforeground="#a3a3a3")
        self.Label21.configure(font=self.font9)
        self.Label21.configure(foreground="#000000")
        self.Label21.configure(highlightbackground="#d9d9d9")
        self.Label21.configure(highlightcolor="black")
        self.Label21.configure(text='''Lóculo''')

        self.Entry1 = tk.Entry(self.Frame1)
        self.Entry1.place(relx=0.09, rely=0.08, relheight=0.16, relwidth=0.86)
        self.Entry1.configure(background="white")
        self.Entry1.configure(disabledforeground="#a3a3a3")
        self.Entry1.configure(font=self.font4)
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(insertbackground="black")
        self.Entry1.configure(textvariable=self.entry_inclui_sepultado)
        self.Entry1.configure(width=544)

        self.Entry2 = tk.Entry(self.Frame1)
        self.Entry2.place(relx=0.35, rely=0.33, relheight=0.16, relwidth=0.20)
        self.Entry2.configure(background="white")
        self.Entry2.configure(disabledforeground="#a3a3a3")
        self.Entry2.configure(font=self.font4)
        self.Entry2.configure(foreground="#000000")
        self.Entry2.configure(insertbackground="black")
        self.Entry2.configure(textvariable=self.entry_inclui_data)

        self.Entry3 = tk.Entry(self.Frame1)
        self.Entry3.place(relx=0.69, rely=0.32, relheight=0.16, relwidth=0.26)
        self.Entry3.configure(background="white")
        self.Entry3.configure(disabledforeground="#a3a3a3")
        self.Entry3.configure(font=self.font4)
        self.Entry3.configure(foreground="#000000")
        self.Entry3.configure(insertbackground="black")
        self.Entry3.configure(textvariable=self.entry_inclui_loculo)
        self.Entry3.bind("<Return>",self.salva_sepultado)

        self.Button3 = tk.Button(self.Frame1)
        self.Button3.place(relx=0.3, rely=0.66, height=34, width=97)
        self.Button3.configure(activebackground="#d9d9d9")
        self.Button3.configure(activeforeground="#000000")
        self.Button3.configure(background="#d9d9d9")
        self.Button3.configure(command=self.salva_sepultado,event=None)
        self.Button3.configure(disabledforeground="#a3a3a3")
        self.Button3.configure(foreground="#000000")
        self.Button3.configure(highlightbackground="#d9d9d9")
        self.Button3.configure(highlightcolor="black")
        self.Button3.configure(pady="0")
        self.Button3.configure(text='''Salvar''')
        self.Button3.configure(width=97)

        self.Button4 = tk.Button(self.Frame1)
        self.Button4.place(relx=0.54, rely=0.66, height=34, width=97)
        self.Button4.configure(activebackground="#d9d9d9")
        self.Button4.configure(activeforeground="#000000")
        self.Button4.configure(background="#d9d9d9")
        self.Button4.configure(command=lambda: self.controller.show_frame(StartPage))
        
        self.Button4.configure(disabledforeground="#a3a3a3")
        self.Button4.configure(foreground="#000000")
        self.Button4.configure(highlightbackground="#d9d9d9")
        self.Button4.configure(highlightcolor="black")
        self.Button4.configure(pady="0")
        self.Button4.configure(text='''Cancelar''')

        self.Label18 = tk.Label(self)
        self.Label18.place(relx=0.32, rely=0.02, height=31, width=222)
        self.Label18.configure(background="#d9d9d9")
        self.Label18.configure(disabledforeground="#a3a3a3")
        self.Label18.configure(foreground="#000000")
        self.Label18.configure(text='''INFORMAÇÃO DE ABERTURA''')
        self.Label18.configure(width=222)
        
    def onselect(self,evt):
        # Note here that Tkinter passes an event object to onselect()
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        isYes = tkinter.messagebox.askyesno("EXCLUIR", "Confirma retirada de\n"+value)    
        if isYes == False:
            return
        arq = open(arquivo, 'r')    
        total = arq.readlines()      
        del total[index] # +1 DEVIDO AO "\n" da ultima lista
        total = sorted(total) 
        arq = open(arquivo, 'w')
        arq.writelines(total)
        arq.close()
        self.Listbox1.delete(0,END)
        arq = open(arquivo, 'r')
        lido = arq.readlines()
        self.controller.var_ocup.set(len(lido))
        for x in range(len(lido)):
            retira_nl = lido[x][:-1]
            self.Listbox1.insert(END, retira_nl)
            
        #self.listBox_sepultados.set(tuple(lido))
        
        arq.close()
        
        #self.listBox_sepultados.set(tuple(total))        
        #arq.close()
        
    def salva_sepultado(self,event=None):
        arq = open(arquivo, 'r')
        lista = arq.readlines()
        
        
        try:
            loculo = int(self.entry_inclui_loculo.get())
            if loculo > 1000:
                messagebox.showinfo("Informação","O Lóculo informado é maior\n \
    do que a capacidade total")
                arq.close()
                return
            
        except ValueError:
            messagebox.showerror("Erro", "Dados inválidos")
            arq.close()
            return
        
        loculo = str(loculo)
        loculo = loculo.zfill(4)
        for text in lista:
            if loculo in text:
                messagebox.showinfo("Informação","O Lóculo informado já está ocupado ")
                return
        nome_sepultado = self.entry_inclui_sepultado.get().upper()
        data = self.entry_inclui_data.get()
        try:
            newdate1 = time.strptime(data, "%d/%m/%y")
            
            
        except ValueError:
            messagebox.showinfo("Informação","Data inválida")
            return
        
        if loculo == "" or nome_sepultado =="" or data =="":
            messagebox.showerror("Dados incompletos", "Preencher todos os campos")
            return
        comprimento_string = len(nome_sepultado)
        comprimento_maximo = 50
        for x in range(comprimento_maximo - comprimento_string):
            nome_sepultado = nome_sepultado + " "
        sepultado = loculo + "     " + nome_sepultado + "     " + data + "\n"
        lista.append(sepultado)
        lista = sorted (lista)        
        arq = open(arquivo, 'w')    
        arq.writelines(lista)        
        self.controller.var_ocup.set(len(lista))
        self.listBox_sepultados.set(tuple(lista))
        arq.close()
        self.entry_inclui_loculo.set("")
        self.entry_inclui_sepultado.set("")
        self.entry_inclui_data.set("")
        messagebox.showinfo("Informação","Cadastro realizado")
        self.controller.show_frame(StartPage)

		
class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller=controller
        label = tk.Label(self, text="This is page 3", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame(StartPage))
        button.pack()

        




       
if __name__ == "__main__":
    
    app = SampleApp()    
    app.mainloop()
