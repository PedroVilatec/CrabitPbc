#169.254.0.1
# -*- coding: utf-8 -*-
import time
import linecache
import urllib.parse
import subprocess
import httplib2
import pyperclip
import json
import requests
import os
import sys
def printException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    
DEVICE = ""
UID = ""

http = httplib2.Http()
url = "https://api.remot3.it/apv/v23.5/user/login"  
body = {"username" : "pedrosilva@vilatec.com.br", "password" : "nbr5410!remot3" }
data = urllib.parse.urlencode(body)
data = data.encode('ascii')
headers = {
    'developerkey': "MzUzREM3NEMtQkQ4Ri00QzRBLUEyNDYtNjkxMzI4RjEwMjk5",
    'content-type': "application/json",
    'cache-control': "no-cache"
    }
response, content = http.request(url, method="POST", headers=headers, body=json.dumps(body))
#print(content.decode())
pedro = json.loads(content.decode())
#print(pedro["developer_key"])

apiMethod="https://"
apiServer="api.remot3.it"
apiVersion= "/apv/v23.5"
developerkey=pedro["developer_key"]
# add the token here which you got from the /user/login API call
token =pedro["token"]
deviceListURL = apiMethod + apiServer + apiVersion + "/device/list/all"
content_type_header     = "application/json"

deviceListHeaders = {
                'Content-Type': content_type_header,
                'developerkey': developerkey,
                            # you need to get token from a call to /user/login
                'token': token,
            }

httplib2.debuglevel     = 0
http                    = httplib2.Http()

response, content = http.request( deviceListURL, 'GET', headers=deviceListHeaders)

#print(content.decode())
data_4 = json.loads(content.decode())
# ~ for k in data_4['devices']:
    # ~ for k2, v in k.items():
        # ~ print(k, v)                
        # ~ if v == 'inactive':
            # ~ print(k)
            # ~ print()

devices = {}
lista = []
counter = 0
chaves=["VNC","vnc","SSH","ssh", "WEB", "HTTP"]
for itens in data_4["devices"]:
    # ~ print(itens)
    # ~ print()
    #print (itens["devicealias"]," " * (35 - len(itens["devicealias"])), itens["devicestate"])
    # ~ for procurado in chaves:
    if not "EVO" in itens:
        elementos=[]
        elementos.append(counter)
        elementos.append(itens["devicealias"])
        elementos.append(itens["deviceaddress"])
        elementos.append(itens["devicestate"])
        elementos.append(itens["lastcontacted"])
        lista.append(elementos)
        devices[itens["devicealias"]] = itens["deviceaddress"]
        counter += 1

#for itens in lista:
#   print(itens[0]+1," " * (2 - len(str(itens[0]+1))), "- ",  itens[1] ," " * (35 - len(itens[1])), itens[3])

dispositivo = ""



################################################################
##apiMethod="https://"
##apiServer="api.remot3.it"
##apiVersion="/apv/v23.5"
##developerKey="MzUzREM3NEMtQkQ4Ri00QzRBLUEyNDYtNjkxMzI4RjEwMjk5"


#UID="82:00:00:09:36:14:34:97"



 

def proxyConnect(UID, token):
    while True:
        try:
            print("UID", UID)
            httplib2.debuglevel     = 0
            http                    = httplib2.Http()
            content_type_header     = "application/json"
        
          # this is equivalent to "whatismyip.com"
          # in the event your router or firewall reports a malware alert
          # replace this expression with your external IP as given by
          # whatismyip.com
        
            print(time.time())
            my_ip = requests.get('https://api.ipify.org/').text
            print (my_ip, time.time())
            ip = requests.get('https://checkip.amazonaws.com').text.strip()
            print(ip, time.time())
            proxyConnectURL = apiMethod + apiServer + apiVersion + "/device/connect"
        
            proxyHeaders = {
                        'Content-Type': content_type_header,
                        'developerkey': developerkey,
                        'token': token
                    }
        
            proxyBody = {
                        'deviceaddress': UID,
                        'hostip': my_ip,
                        'wait': "true"
                    }
        
            response, content = http.request( proxyConnectURL,
                                                  'POST',
                                                  headers=proxyHeaders,
                                                  body=json.dumps(proxyBody),                     
                                               )
        except:
            printException()
            
        try:
     
            data = json.loads(content.decode())["connection"]["proxy"]
            print(data)
            if "VNC" in dispositivo or "MCC" in dispositivo or "MQTT" in dispositivo or "RDP" in dispositivo or "SMB" in dispositivo:
                data = data[7:]
                data = data.split("/")
                hostname = data[0]
                porta = data[-1].split("=")[1]
                pyperclip.copy(hostname + ":"+ porta)
                print ("Copiado para área de transferência VNC:" + hostname + ":"+ porta)
                
                
            if "WEB" in dispositivo or "HTTP" in dispositivo:
                os.system("python -m webbrowser -t " + str(data))
    
            if "SSH" in dispositivo:
                data = data[7:]
                data = data.split(":")
                hostname = data[0]
                porta = data[1]
                pyperclip.copy(hostname)
                print("SSH - ",hostname, porta)
                subprocess.call(['putty ', "-ssh", hostname, porta])
                
    ##            print ("Copiado para área de transferência VNC:" + hostname + ":"+ porta)            
    ##            os.system("putty.exe -ssh " + hostname )
                
    
            break    
        except KeyError:
            print ("Key Error exception!")
            print (content)
        
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False
    
if __name__ == '__main__':
    while True:
        try:
            entrada = input("Busca por palavra chave ou enter para ver todos\n-> ").upper()
            
            if is_number(entrada):
                entrada = int(entrada)
                if  int(entrada) <= len(lista)+1 and int(entrada) > 0:
                    UID = lista[entrada - 1][2]
                    print(lista[entrada - 1][1], " - ",UID)
                    dispositivo = lista[entrada - 1][1]
                    #acertou = True
                    proxyConnect(UID, token)                

            else:
                #print("lista", str(entrada))
                for itens in lista:
                    
                    if str(entrada) in str(itens[1]) and not "EVO" in str(itens[1]):
                        if "VNC_RASP_CORTEL_CAPELA_02" in str(itens[1]):
                            print(itens[0]+1," " * (2 - len(str(itens[0]+1))), "-",  "REPOUSO ECUMENICA 1 CORTEL" ,"." * (35 - len("REPOUSO ECUMENICA 1 CORTEL")), itens[3], itens[4].split("+")[0].replace("T"," "))
                        elif "VNC_RASP_CAPELA_2_CERIMONIA_CORTEL" in str(itens[1]):
                            print(itens[0]+1," " * (2 - len(str(itens[0]+1))), "-",  "VNC ECUMENICA 1 CORTEL" ,"." * (35 - len("VNC ECUMENICA 1 CORTEL")), itens[3], itens[4].split("+")[0].replace("T"," "))
                        else:
                            print(itens[0]+1," " * (2 - len(str(itens[0]+1))), "-",  itens[1] ,"." * (35 - len(itens[1])), itens[3], itens[4].split("+")[0].replace("T"," "))               
                        # ~ print(itens[4])
                entrada = input("Escolha uma opção ").upper()
                if is_number(entrada):
                    try:
                        entrada = int(entrada)
                        if  int(entrada) <= len(lista)+1 and int(entrada) > 0:
                            UID = lista[entrada - 1][2]
                            print(lista[entrada - 1][1], " - ",UID)
                            dispositivo = lista[entrada - 1][1]
                            print(UID, token)
                            proxyConnect(UID, token)
                    except:
                        printException()
                else:
                    print("Opção inválida")             

        except Exception as e:
            printException()

