# -*- coding: utf-8 -*-
import os, sys
import time
import linecache
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from instance.config import Config

def printException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    
    
def erroDispositivo(dispositivo, comando):
    dataSave = "{} {} {} \n".format(time.strftime("%d/%m/%Y-%H:%M:%S"), dispositivo, comando)
    try:
        data = ''
        with open('../instance/LOG/logMqtt.txt', "r") as f:
            data = f.read()

        with open('../instance/LOG/logMqtt.txt', "w") as f:
            f.write(dataSave+data)

    except FileNotFoundError:
         if os.path.exists('../instance/LOG') == False:
              os.makedirs('../instance/LOG')

         with open('../instance/LOG/logMqtt.txt', "w") as f:
             f.write(dataSave)
             
def writeArquivo(dados, pasta, arquivo):
    print(dados, pasta, arquivo)
    dataSave = dados
    try:
        with open('./'+str(pasta)+'/'+str(arquivo), "w") as f:
            f.write(dataSave)

    except FileNotFoundError:
        if os.path.exists('./'+str(pasta)) == False:
            os.makedirs('./'+str(pasta))

        with open('./'+str(pasta)+'/'+str(arquivo), "w") as f:
            f.write(dataSave)

def readArquivo(pasta, arquivo):
    try:
        print(pasta, arquivo)
        with open('./'+str(pasta)+'/'+str(arquivo), "r") as f:
            return f.readlines()

    except FileNotFoundError:
            print("erro saveFile.readArquivo")

        
def nivelColetoras(dados):
    dataSave = dados
    try: 
        data = ""
        with open('../instance/LOG/nivel_coletoras.txt', "w") as f:
            f.write(dataSave)

    except FileNotFoundError:
        if os.path.exists('../instance/LOG') == False:
            os.makedirs('../instance/LOG')

        with open('../instance/LOG/nivel_coletoras.txt', "w") as f:
            f.write(dataSave)
            
def falhaTroca(dados):
    dataSave = dados
    try: 
        data = ""
        with open('../instance/LOG/falhas_troca_gasosa.txt', "r") as f:
            data = f.read()
            
        with open('../instance/LOG/falhas_troca_gasosa.txt', "w") as f:
            f.write("{} {}\n".format(time.strftime("%d/%m/%Y-%H:%M:%S"), dataSave)+data)

    except FileNotFoundError:
        if os.path.exists('../instance/LOG') == False:
            os.makedirs('../instance/LOG')

        with open('../instance/LOG/falhas_troca_gasosa.txt', "w") as f:
            f.write("{} {}\n".format(time.strftime("%d/%m/%Y-%H:%M:%S"), dataSave))
               
def falhaTeste(dados):
    dataSave = dados
    try: 
        data = ""
        with open('../instance/LOG/falhas_teste_estanqueidade.txt', "r") as f:
            data = f.read()
            
        with open('../instance/LOG/falhas_teste_estanqueidade.txt', "w") as f:
            f.write("{} {}\n".format(time.strftime("%d/%m/%Y-%H:%M:%S"), dataSave)+data)

    except FileNotFoundError:
        if os.path.exists('../instance/LOG') == False:
            os.makedirs('../instance/LOG')

        with open('../instance/LOG/falhas_teste_estanqueidade.txt', "w") as f:
            f.write("{} {}\n".format(time.strftime("%d/%m/%Y-%H:%M:%S"), dataSave))
                              
def resultadoTeste(dados):
    dataSave = dados
    try: 
        data = ""
        with open('../instance/LOG/teste_estanqueidade.txt', "r") as f:
            data = f.read()
        with open('../instance/LOG/teste_estanqueidade.txt', "w") as f:
            f.write(dataSave+data)

    except FileNotFoundError:
        if os.path.exists('../instance/LOG') == False:
            os.makedirs('../instance/LOG')

        with open('../instance/LOG/teste_estanqueidade.txt', "w") as f:
            f.write(dataSave)

def falhasColetoras(str):
    dataSave = str
    try:
        data = ""
        with open('../instance/LOG/coletoras/falhas_coletoras.txt', "r") as f:
            data = f.read()
        with open('../instance/LOG/coletoras/falhas_coletoras.txt', "w") as f:
            f.write(dataSave+data)

    except FileNotFoundError:
        if os.path.exists('../instance/LOG/coletoras') == False:
            os.makedirs('../instance/LOG/coletoras')

        with open('../instance/LOG/coletoras/falhas_coletoras.txt', "w") as f:
            f.write(dataSave)
            
def operacoesColetoras(str):
    dataSave = str
    try:
        data = ""
        with open('../instance/LOG/coletoras/operacoes_coletoras.txt', "r") as f:
            data = f.read()
        with open('../instance/LOG/coletoras/operacoes_coletoras.txt', "w") as f:
            f.write(dataSave+data)

    except FileNotFoundError:
        if os.path.exists('../instance/LOGcoletoras/') == False:
            os.makedirs('../instance/LOGcoletoras/')

        with open('../instance/LOG/coletoras/operacoes_coletoras.txt', "w") as f:
            f.write(dataSave)

def falhasEvaporadoras(str):
    dataSave = str
    try:
        data = ""
        with open('../instance/LOG/evaporadoras/falhas_evaporadoras.txt', "r") as f:
            data = f.read()
        with open('../instance/LOG/evaporadoras/falhas_evaporadoras.txt', "w") as f:
            f.write(dataSave+data)

    except FileNotFoundError:
        if os.path.exists('../instance/LOG/evaporadoras') == False:
            os.makedirs('../instance/LOG/evaporadoras')

        with open('../instance/LOG/evaporadoras/falhas_evaporadoras.txt', "w") as f:
            f.write(dataSave)

def operacoesEvaporadoras(str):
    dataSave = str
    try:
        data = ""
        with open('../instance/LOG/evaporadoras/operacoes_evaporadoras.txt', "r") as f:
            data = f.read()
        with open('../instance/LOG/evaporadoras/operacoes_evaporadoras.txt', "w") as f:
            f.write(dataSave+data)

    except FileNotFoundError:
        if os.path.exists('../instance/LOG/evaporadoras') == False:
            os.makedirs('../instance/LOG/evaporadoras')

        with open('../instance/LOG/evaporadoras/operacoes_evaporadoras.txt', "w") as f:
            f.write(dataSave)
            
def resultadoTroca(str):
    dataSave = str
    try:
        data = ""
        with open('../instance/LOG/troca_gasosa.txt', "r") as f:
            data = f.read()
        with open('../instance/LOG/troca_gasosa.txt', "w") as f:
            f.write(dataSave+data)

    except FileNotFoundError:
        if os.path.exists('../instance/LOG') == False:
            os.makedirs('../instance/LOG')

        with open('../instance/LOG/troca_gasosa.txt', "w") as f:
            f.write(dataSave)

def historico_pressao(bloco, pressao):
    before = ""
    data=""
    try:
        try:
            with open("../instance/LOG/historico_pressao.txt","r") as e:
                data = e.readlines()
            existe = False
            new_data = ""
            for line in data:
                if len(line.split("=")) > 1:
                    if "NICO" in line:
                        existe = True
                        _bloco, press = line.rstrip().split("=")
                        pressoes = press.split(",")                        
                        new_data += "{}= {}, {}, {}, {}, {}\n".format(bloco, pressoes[1][1:],pressoes[2][1:],pressoes[3][1:],pressoes[4][1:],pressao)
                    else:
                        bloco_in_line = line.rstrip().split("=")[0].split(" ")
                        if bloco.split(" ")[2] == bloco_in_line[2]:
                            existe = True
                            _bloco, press = line.rstrip().split("=")
                            pressoes = press.split(",")
                            new_data += "{}= {}, {}, {}, {}, {}\n".format(bloco, pressoes[1][1:],pressoes[2][1:],pressoes[3][1:],pressoes[4][1:],pressao)
                        else:
                             new_data += line                        
                else:
                    new_data += line    
            if not existe:
                new_data += "{} {}=0 ,0 , 0, 0, {}\n".format(bloco, Config.PRESSAO_IDEAL, pressao)
            with open("../instance/LOG/historico_pressao.txt","w") as e:
                e.write(new_data)
        except FileNotFoundError:
            if os.path.exists('../instance/LOG') == False:
                os.makedirs('../instance/LOG')
            
            with open('../instance/LOG/historico_pressao.txt', "w") as f:
                new_data ="   **HISTORICO DOS TESTES**\n{} {}=0 ,0 , 0, 0, {}\n".format(bloco, Config.PRESSAO_IDEAL, pressao)
                f.write(new_data)    
    except:
        printException()
    
