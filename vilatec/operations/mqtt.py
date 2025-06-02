# -*- coding: utf-8 -*-
import linecache
import time, datetime
import io
import os, sys
import threading
import paho.mqtt as versionMqttVerify
import paho.mqtt.client as mqtt
import paho.mqtt.client as mqtt_server
import threading
import json
from json.encoder import JSONEncoder
from instance.devices import Devices
from instance.config import Config
from vilatec.operations import saveFile
import urllib.request
import re
import subprocess
# from infra.check_internet import have_internet
from vilatec.operations.integracao import registrar, enviar, ler



class Mosquitto():
	def __init__(self, client, porta, desabilitado, print_exception):
		self.printException = print_exception
		self.client = client
		self.porta = porta
		self.counter_reset_inversor = 0
		# mqtt_version = self.parse_version(versionMqttVerify.__version__)

		# # Verifica se é versão 2.0.0 ou superior
		# if mqtt_version >= (2, 0, 0):
		# 	client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
		# else:
		# self.mqttc = mqtt.Client("ETEN")
		self.mqttc = mqtt.Client()
		self.mqttc.on_message = self.on_message
		self.mqttc.on_connect = self.on_connect
		self.appStarted = time.time()
		self.bool_troca_ativada = False
		self.testeDePressao = False
		self.nivel_dispositivo = None
		self.nivel_key = None
		self.dispositivos_desconhecidos = []
		self.pressao = None
		self.dispositivos_off = {}
		self.dispositivos_off["data"] = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
		self.erro = []
		self.desabilitado = desabilitado
		self.m3_total = 0
		self.m3_hora = 0
		self.m3_troca = 0
		self.pressao_provisoria = 0
		self.sifao_cheio = False
		self.devices = Devices()
		self.dispositivosMqtt = {}
		self.removidos = []
		self.printTroca = False
		self.nivel_tanque = "----"
		load_dispositivosMqtt = saveFile.load_dispositivosMqtt('/mnt/ramdisk/temp_disp.json')

		if len(load_dispositivosMqtt) > 0:
			# Adiciona chaves ausentes
			for dispositivo in self.devices.CONTROLADORES:
				if dispositivo in load_dispositivosMqtt:
					for chave in self.devices.CONTROLADORES[dispositivo]:
						if chave not in load_dispositivosMqtt[dispositivo]:
							load_dispositivosMqtt[dispositivo][chave] = self.devices.CONTROLADORES[dispositivo][chave]
				else:
					load_dispositivosMqtt[dispositivo] = self.devices.CONTROLADORES[dispositivo]

			# Remove dispositivos que não estão mais em CONTROLADORES
			dispositivos_existentes = list(load_dispositivosMqtt.keys())
			for dispositivo in dispositivos_existentes:
				if dispositivo not in self.devices.CONTROLADORES:
					del load_dispositivosMqtt[dispositivo]

			self.dispositivosMqtt.update(load_dispositivosMqtt)
		else:
			self.dispositivosMqtt.update(self.devices.CONTROLADORES)

		for elements in self.dispositivosMqtt.keys():
			if elements not in self.devices.CONTROLADORES.keys():
				self.removidos.append(elements)
				# self.dispositivosMqtt[elements] = {**self.devices.CONTROLADORES[elements]}

			if any( item in elements for item in self.desabilitado):
				self.dispositivosMqtt[elements].update({"DESABILITADO": True})
			else:
				self.dispositivosMqtt[elements].update({"DESABILITADO": False})

		for disp in self.removidos:
			'''
			remove o dispositivo se ele for descadastrado no devices
			'''
			del self.dispositivosMqtt[disp]
			print(disp, "REMOVIDO")
		self.nivel_sifao_key = None
		for elements in sorted(self.dispositivosMqtt.keys()):
			'''
			ACRESCENTA NOVAS CHAVES NOS DISPOSITIVOS
			'''
			if not any(key_ == "S_OSC_CONEXAO" for key_ in self.dispositivosMqtt[elements].keys()):
				self.dispositivosMqtt[elements]["S_OSC_CONEXAO"] = {"acumulado":0,"ultima_ocorrencia": time.time()}

				
			elif not isinstance(self.dispositivosMqtt[elements]["S_OSC_CONEXAO"], dict):
				'''CONVERSÃO DE INTEIRO PARADICIONÁRIO'''
				total = self.dispositivosMqtt[elements]["S_OSC_CONEXAO"]
				self.dispositivosMqtt[elements]["S_OSC_CONEXAO"] = {"acumulado":total, "ultima_ocorrencia": time.time()}
			
			if not any(key_ == "TIME_MSG" for key_ in self.dispositivosMqtt[elements].keys()):
				self.dispositivosMqtt[elements]["TIME_MSG"] = time.time() #adiciona chave para verificar se está online
			self.dispositivosMqtt[elements]["S_CONEXAO"] = "OFFLINE" #adiciona chave para verificar se está online
			if "EVAP" in elements and "CAB" in elements:
				if self.nivel_dispositivo is None:
					self.nivel_tanque = "----"
					self.nivel_dispositivo = elements
					for k in self.dispositivosMqtt[elements].keys():
						# print(k)
						if "S_NIVEL" in k and not "SIFAO" in k and  not "EVAP" in k:
							self.nivel_key = k
						if "SIFAO" in k:
							self.nivel_sifao_key = k
					if self.nivel_key:
						print("Dispositivo nível tanque", self.nivel_dispositivo, "Chave", self.nivel_key)


			if "NIVEL_TANQUE" in elements:
				self.nivel_tanque = "----"
				self.nivel_dispositivo = elements
				for k in self.dispositivosMqtt[elements].keys():
					if "S_NIVEL" in k and  not "SIFAO" in k:
						self.nivel_key = k
					if "SIFAO" in k:
						self.nivel_sifao_key = k
				print("Dispositivo nível tanque", self.nivel_dispositivo, "Chave", self.nivel_key)						


			if "VALVULA" in elements:

				# print(json.dumps(self.dispositivosMqtt[elements], sort_keys=True, indent=4))
				if not "S_ERRO" in self.dispositivosMqtt[elements].keys():
					self.dispositivosMqtt[elements]["S_ERRO"] = False

				if "CABINE" in elements and not "BL2" in elements:
					self.status_valvula_cabine = ""
					self.dispositivosMqtt[elements]["MEDIA_FLUXO_DE_AR"] = 0. # ADICIONA CHAVE
					self.dispositivosMqtt[elements]["COUNTER_FLUXO_DE_AR"] = 0 # ADICIONA CHAVE
					self.dispositivosMqtt[elements]["TOTAL_FLUXO_DE_AR"] = 0
					
					if "S_M3/h" in self.dispositivosMqtt[elements].keys():
						self.m3_hora = self.dispositivosMqtt[elements]["S_M3/h"]
						print("Metro cubico por hora = S_M3/h")

					elif "S_M3_TOTAL" in self.dispositivosMqtt[elements].keys():
						self.m3_total = self.dispositivosMqtt[elements]["S_M3_TOTAL"]
						print("Metro cubico total = S_M3_TOTAL")

					elif "S_SOMA_M3_AR" in self.dispositivosMqtt[elements].keys():
						self.m3_total = self.dispositivosMqtt[elements]["S_SOMA_M3_AR"]
						print("Metro cubico total = S_SOMA_M3_AR -> ".format(self.m3_total) )

					else:
						self.m3_hora = 0


					# print("VALVULA CABINE", self.dispositivosMqtt[elements])

			if "ARDUINO" in elements:
				self.dispositivosMqtt[elements]["MEDIA_FREQUENCIA"] = 0. # ADICIONA CHAVE
				self.dispositivosMqtt[elements]["COUNTER_FREQUENCIA"] = 0 # ADICIONA CHAVE
				self.dispositivosMqtt[elements]["MAIOR_PRESSAO"] = 0.
				self.dispositivosMqtt[elements]["MAIOR_FREQUENCIA"] = 0.
				self.dispositivosMqtt[elements]["LOOP_MSG_INVERSOR"] = time.time()
				self.dispositivosMqtt[elements]["S_INVERSOR_ANTERIOR"] = ""
				self.start_time_pressao = time.time()

			if "COLETOR" in elements:
				self.dispositivosMqtt[elements]["TEMPO_LIGADO"] = 0

		self.lastState = saveFile.load_last_state('/mnt/ramdisk/last_state.json')

		if len(self.lastState) > 0:
			if "turned_api" not in self.lastState.keys():
				self.lastState["turned_api"] = {}
				self.lastState["turned_api"]["total_sepultados"] = 0

			for k, v in self.devices.CONTROLADORES.items():
				if k not in self.lastState.keys():
					self.lastState[k] = {**{"S_CONEXAO": "OFFLINE"},**{"INTEGRACAO":False}}
					if "EVAP" in k:
						self.lastState[k].update({"INICIO_EVAPORACAO": time.time(), "FIM_EVAPORACAO": time.time(), "ENVIO_MSG":time.time(), "S_RES":"DESLIGADO"})

					if "ACESSO" in k:
						if "S_PORTA" in self.dispositivosMqtt[k].keys():
							self.lastState[k].update({"S_PORTA": ""})
						self.lastState[k].update({"ABERTURA": time.time(), "FECHAMENTO": time.time(), "ENVIO_MSG":time.time()})
		else:
			for elements in self.dispositivosMqtt.keys():
				# self.lastState[elements].update({**{"S_CONEXAO": "OFFLINE"},**{"INTEGRACAO":False}})
				self.lastState[elements] = {**{"S_CONEXAO": "OFFLINE"},**{"INTEGRACAO":False}, **{"turned_api": {} }}
				if "EVAP" in elements:
					self.lastState[elements].update({"INICIO_EVAPORACAO": time.time(), "FIM_EVAPORACAO": time.time(), "ENVIO_MSG":time.time(), "S_RES":"DESLIGADO"})

				if "ACESSO" in elements:
					if any("S_PORTA" in key for key in self.dispositivosMqtt[elements].keys()):
						self.lastState[elements].update({"S_PORTA": ""})
					self.lastState[elements].update({"ABERTURA": time.time(), "FECHAMENTO": time.time(), "ENVIO_MSG":time.time()})

		# self.mqttc.on_publish = on_publish
		self.mqttc.on_subscribe = self.on_subscribe
		self.mqttc.on_disconnect = self.on_disconnect
		# Uncomment to enable debug messages
		#~ self.mqttc.on_log = self.on_log
		self.inicio = time.time() + 20
		self.envia_telegram_single = None # variavel sentenciada para enviar telegramas
		self.envia_telegram_all = None # variavel sentenciada para enviar telegramas
		self.mqttc.connect("localhost", self.porta, 60)
		self.serial_port = None
		self.serial_data = ["","No Data"]
		thread = threading.Thread(target=self.mqttc.loop_forever)
		thread.start()
		thread1 = threading.Thread(target=self.verifica_online)
		thread1.start()
########################################################################
#################### FUNCOES ORIUNDAS DO app.py ########################
	def printException(self):
		...

	def msg_telegram_server_direta(self, msg):
		...
	def msg_telegram_server(self, msg):
		...
	def desativaTroca(self):
		self.bool_troca_ativada = False
		self.testeDePressao = False

	def desativaTeste(self):
		self.bool_troca_ativada = False
		self.testeDePressao = False

	def incluiErro(self, erro):
		existe = False
		if len(self.erro) > 0:
			for lista in self.erro:
				if lista == erro:
					existe = True
			if not existe:
				self.erro.append(str(erro))

		else:
			self.erro.append(erro)

	def atribui_var(self, var):
		...

	def get_erro(self):
		return self.erro

	def emit_status(self, msg):
		pass
		'''
		Referencia função de mesmo nome em app.py
		'''
	def on_disconnect(self, client, userdata,  rc):
		print("desconectado mqtt")
	def on_log(self, mqttc, obj, level, string):
		print(string)

	def on_connect(self, mqttc, obj, flags, rc):
		self.mqttc.subscribe("#", 0)

	def troca_sch(self):
		pass


	def msg_sistema(self, msg):
		pass
		#self.msg_sistema = function

########################################################################
########################################################################
	def on_subscribe(self, mqttc, obj, mid, granted_qos):
		print("subscribed")

	def envia_disp_desconhecidos(self):
		if len(self.dispositivos_desconhecidos) > 0:
			disp = "Existe dispositivo não configurado no sistema\n{}".format("\n".join(self.dispositivos_desconhecidos))
			self.msg_telegram_server_direta(disp)

	def on_message(self, mqttc, obj, msg):
		try:
			if "MCC\\RET" not in msg.topic:
				print(msg.topic)
			if msg.topic == "printTroca":
				self.printTroca = not self.printTroca
				print("Print troca =", self.printTroca)

			if msg.topic == "MCC\\SISTEMA":
				self.msg_sistema(msg)
				return

			data = {}
			try:
				self.turned = msg.payload.decode()
				data = json.loads(self.turned)
			except:
				return
			# if "EVAP_BL" in data["DISPOSITIVO"]:
			# 	print(data)
			dispositivo = data["DISPOSITIVO"]
			statusDict = data["STATUS"]
			statusDict["TIME_MSG"] = time.time()
			statusDict["S_CONEXAO"] = "ONLINE"
			dict_ = {}
			dict_.update(data["STATUS"])
			for key in dict_.keys():
				if "STATUS" in key:
					data["STATUS"][key.replace("STATUS_", "S_")] = data["STATUS"].pop(key)
			statusDict = data["STATUS"]
			try:
				
				doze_horas = (12*60*60)
				if self.appStarted + doze_horas < time.time():
					if "S_OSC_CONEXAO" in self.dispositivosMqtt[dispositivo].keys() and \
							isinstance(self.dispositivosMqtt[dispositivo]["S_OSC_CONEXAO"], dict):
						if time.time() - self.dispositivosMqtt[dispositivo]["S_OSC_CONEXAO"]["ultima_ocorrencia"] > doze_horas:
							if self.dispositivosMqtt[dispositivo]["S_CONEXAO"] == "ONLINE":
								self.dispositivosMqtt[dispositivo]["S_OSC_CONEXAO"]["acumulado"] = 0
								self.dispositivosMqtt[dispositivo]["S_OSC_CONEXAO"]["ultima_ocorrencia"] = time.time()				
						# print(dispositivo, key)
				self.dispositivosMqtt[dispositivo].update(statusDict)
			except:
				if dispositivo in self.devices.CONTROLADORES.keys():
					self.dispositivosMqtt[dispositivo]=statusDict
				elif dispositivo not in self.dispositivos_desconhecidos:
					self.msg_telegram_server_direta("Há um dispositivo inexistente no devices\n{}".format(dispositivo))
					self.dispositivos_desconhecidos.append(dispositivo)

				pass
			if dispositivo not in self.devices.CONTROLADORES.keys() and dispositivo in self.dispositivosMqtt.keys():
				del self.dispositivosMqtt[dispositivo]
				self.msg_telegram_server_direta("Removendo dispositivo inexistente no devices\n{}".format(dispositivo))
				self.dispositivos_desconhecidos.append(dispositivo)
				self.envia_disp_desconhecidos()


			# if "VALVULA" in dispositivo:
			# 	print(json.dumps(self.dispositivosMqtt[dispositivo], sort_keys=True, indent=4))
			# print(self.nivel_dispositivo, dispositivo, self.nivel_dispositivo == dispositivo)
			if self.nivel_dispositivo == dispositivo:
				# print(self.nivel_dispositivo, self.nivel_key)
				# print(json.dumps(statusDict, indent=4))
				if self.nivel_key in statusDict.keys():
					self.nivel_tanque = statusDict[self.nivel_key]
				else:
					print("NIVEL TANQUE NÃO ENCONTRADO EM {}".format(dispositivo))
				if self.nivel_sifao_key:
					if statusDict[self.nivel_sifao_key] == "CHEIO":
						self.nivel_tanque = self.nivel_tanque + " - S1"
						self.sifao_cheio = True
						# print("2", self.nivel_dispositivo, v2, self.nivel_tanque)
					if statusDict[self.nivel_sifao_key] == "VAZIO":
						self.nivel_tanque = self.nivel_tanque + " - S0"
						self.sifao_cheio = False

			if "ACESSO" in dispositivo and "ETEN" in dispositivo:
				self.acesso(dispositivo, statusDict)

			if "VALVULA_CABINE" in dispositivo and not "BL2" in dispositivo:
				try:
					if any(x == dispositivo for x in self.dispositivosMqtt.keys()):
						self.func_valvula_cabine(dispositivo, statusDict)
				except Exception as e:
					self.printException()

			if "ARDUINO" in dispositivo:
				try:
					self.arduino()
				except Exception as e:
					self.printException()

			# if self.inicio < time.time():
			if "EVAP" in dispositivo and "S_EVAP" in statusDict:
				self.evaporadora_tripla(dispositivo, statusDict)
				pass
			if "COLETOR" in dispositivo:
				self.coletor(dispositivo, statusDict)
				pass
		except Exception as e:
			self.printException()
			try:
				#~ print(msg.topic)
				if "ARDUINO" in msg.topic:
					if msg.payload.decode("utf-8", "ignore").rstrip() == 'STOP TROCA':
						self.bool_troca_ativada = False
					elif msg.payload.decode("utf-8", "ignore").rstrip() == 'STOP TESTE':
						self.testeDePressao = False
					else:
						serial_data = msg.payload.decode("utf-8").split("/")[1]
						print(msg.payload, serial_data)
						self.serial_port.write(serial_data.encode("utf-8"))

			except Exception as e:
				self.printException()

	def acesso(self, dispositivo, status):
		try:
			if "S_PORTA" in status.keys():
				if status["S_PORTA"] == "ABERTA":
					if self.lastState[dispositivo]["S_PORTA"] != status["S_PORTA"]:
						self.lastState[dispositivo]["S_PORTA"] = status["S_PORTA"]
						self.lastState[dispositivo]["ABERTURA"] = time.time()
						self.lastState[dispositivo]["ENVIO_MSG"] = time.time()
						saveFile.grava_ramfs(self.lastState, '/mnt/ramdisk/last_state.json')
						self.msg_telegram_server_direta("Porta da Eten aberta")

					if time.time() - self.lastState[dispositivo]["ENVIO_MSG"] > 60 * 10:
						self.lastState[dispositivo]["ENVIO_MSG"] = time.time()
						self.msg_telegram_server_direta("Porta da Eten aberta \n**Duração**\n{}".format(\
							self.tempo_passado(self.lastState[dispositivo]["ABERTURA"])))

				if status["S_PORTA"] == "ENTREABERTA":
					if self.lastState[dispositivo]["S_PORTA"] != status["S_PORTA"]:
						self.lastState[dispositivo]["S_PORTA"] = status["S_PORTA"]

						self.lastState[dispositivo]["ENVIO_MSG"] = time.time()
						# self.msg_telegram_server_direta("Porta da Eten entreaberta")

					if time.time() - self.lastState[dispositivo]["ENVIO_MSG"] > 60 * 30:
						self.lastState[dispositivo]["ENVIO_MSG"] = time.time()
						self.msg_telegram_server_direta("Porta da Eten entreaberta \n**Duração**\n{}".format(\
							self.tempo_passado(self.lastState[dispositivo]["ABERTURA"])))
				# print("status", status)
				# print("self.lastState[dispositivo]", self.lastState[dispositivo])
				if status["S_PORTA"] == "FECHADA" and (self.lastState[dispositivo]["S_PORTA"] != status["S_PORTA"]):
					self.lastState[dispositivo]["S_PORTA"] = status["S_PORTA"]
					self.lastState[dispositivo]["FECHAMENTO"] = time.time()
					self.lastState[dispositivo]["ENVIO_MSG"] = time.time()
					saveFile.grava_ramfs(self.lastState, '/mnt/ramdisk/last_state.json')
					self.msg_telegram_server_direta("Porta da Eten fechada após: {}".format(\
						self.tempo_passado(self.lastState[dispositivo]["ABERTURA"])))
		except:
			print(dispositivo)
			self.printException()

	def func_valvula_cabine(self, dispositivo, dic):
		for k2, v2 in dic.items():
			try:
				if "S_CALIB_" in k2:
					if "S_CALIB_0" not in k2:
						if v2[0] < 1. or  v2[1] < 1.:
							
							print("CALIBRACAO DO SENSOR MAF APRESENTA ERROS!")
							self.m3_total = "----"
							self.m3_hora = "----"

				if "S_M3/h" in k2 and re.search('\d', str(str(self.m3_total)+str(self.m3_hora))):#verifica se há numero em v2
					self.m3_hora = v2
					self.dispositivosMqtt[dispositivo]["MEDIA_FLUXO_DE_AR"] += v2
					self.dispositivosMqtt[dispositivo]["COUNTER_FLUXO_DE_AR"] += 1
					if self.dispositivosMqtt[dispositivo][k2] > self.dispositivosMqtt[dispositivo]["TOTAL_FLUXO_DE_AR"]:
						self.dispositivosMqtt[dispositivo]["TOTAL_FLUXO_DE_AR"] = self.dispositivosMqtt[dispositivo][k2]

				elif "S_AR_M3h" in k2 and re.search('\d', str(str(self.m3_total)+str(self.m3_hora))):#verifica se há numero em v2:
					self.m3_hora = v2
					self.dispositivosMqtt[dispositivo]["MEDIA_FLUXO_DE_AR"] += v2
					self.dispositivosMqtt[dispositivo]["COUNTER_FLUXO_DE_AR"] += 1
					if self.dispositivosMqtt[dispositivo][k2] > self.dispositivosMqtt[dispositivo]["TOTAL_FLUXO_DE_AR"]:
						self.dispositivosMqtt[dispositivo]["TOTAL_FLUXO_DE_AR"] = self.dispositivosMqtt[dispositivo][k2]

				elif "S_FLUXO_DE_AR" in k2:
					self.dispositivosMqtt[dispositivo]["MEDIA_FLUXO_DE_AR"] += self.dispositivosMqtt[dispositivo][k2]
					self.dispositivosMqtt[dispositivo]["COUNTER_FLUXO_DE_AR"] += 1



				if "S_M3_TOTAL" in k2 and re.search('\d', str(v2)):#verifica se há numero em v2:
					if "S_VERSAO" in self.dispositivosMqtt[dispositivo].keys():
						if self.extrair_versao_tupla(self.dispositivosMqtt[dispositivo]["S_VERSAO"])[:2] == (1, 5):		
							self.m3_total = v2
							if self.dispositivosMqtt[dispositivo][k2] > self.dispositivosMqtt[dispositivo]["TOTAL_FLUXO_DE_AR"]:
								self.dispositivosMqtt[dispositivo]["TOTAL_FLUXO_DE_AR"] = v2

					elif "VERSAO" in self.dispositivosMqtt[dispositivo].keys():
						if self.extrair_versao_tupla(self.dispositivosMqtt[dispositivo]["VERSAO"])[:2] == (1, 5):					
							self.m3_total = v2
							if self.dispositivosMqtt[dispositivo][k2] > self.dispositivosMqtt[dispositivo]["TOTAL_FLUXO_DE_AR"]:
								self.dispositivosMqtt[dispositivo]["TOTAL_FLUXO_DE_AR"] = v2								

				if "S_SOMA_M3_AR" in self.dispositivosMqtt[dispositivo].keys():
					if self.extrair_versao_tupla(self.dispositivosMqtt[dispositivo]["S_VERSAO"]) > (1,5):
						self.m3_total = self.dispositivosMqtt[dispositivo]["S_SOMA_M3_AR"]

				if "S_VALVULA" in k2:
						self.status_valvula_cabine = v2
					# if v2 == "FECHADA" and self.dispositivosMqtt[dispositivo]["S_FLUXO_DE_AR"] > 10:
					# 	if "ERRO SENSOR MAF" in self.erro:
					# 		~ continue
					# 	~ else:
					# 		~ if not "ERRO SENSOR MAF" in self.erro:
					# 			~ self.incluiErro("ERRO SENSOR MAF")
					# 			~ if self.envia_telegram_all:
					# 				~ self.envia_telegram_all("Sensor MAF com defeito")



			except Exception as e:
				print(v2)
				self.printException()



	def extrair_versao_tupla(self, texto):
		match = re.search(r'(\d+(?:\.\d+)+)', texto)
		if match:
			return tuple(map(int, match.group(1).split(".")))
		else:
			return (0,)

	def media_fluxo_de_ar(self):
		for k, v in Devices.CONTROLADORES.items():
			if "VALVULA_CABINE" in k:
				if self.dispositivosMqtt[k]["MEDIA_FLUXO_DE_AR"] != 0 and self.dispositivosMqtt[k]["COUNTER_FLUXO_DE_AR"] != 0:
					return self.dispositivosMqtt[k]["MEDIA_FLUXO_DE_AR"] / self.dispositivosMqtt[k]["COUNTER_FLUXO_DE_AR"]
				else:
					return 0.

	def zera_fluxo_de_ar(self):
		self.m3_troca = self.m3_total
		for k, v in Devices.CONTROLADORES.items():
			if "VALVULA_CABINE" in k:
				self.dispositivosMqtt[k]["MEDIA_FLUXO_DE_AR"] = 0.
				self.dispositivosMqtt[k]["COUNTER_FLUXO_DE_AR"] = 0.
				return

	def fluxo_de_ar_atual(self):
		
		return self.m3_total - self.m3_troca


	def arduino(self):
		frequencia = 0
		for k, v in self.dispositivosMqtt.items():
			if "ARDUINO" in k:
				a = 0
				for k2, v2 in v.items():
					# print(k, k2, v2)
					try:
						if "pressao" in k2:
							if self.dispositivosMqtt[k][k2] < self.dispositivosMqtt[k]["MAIOR_PRESSAO"]:
								elapsed_time = 0
								if self.pressao_provisoria == None:
									self.start_time_pressao = time.time()
									self.pressao_provisoria = self.dispositivosMqtt[k][k2]
									# print()
									# print("PRESSAO PROVISORIA", self.pressao_provisoria, time.time())
								else:



									elapsed_time = time.time() - self.start_time_pressao
									if elapsed_time >= 5 and self.pressao_provisoria is not None:
										self.dispositivosMqtt[k]["MAIOR_PRESSAO"] = self.pressao_provisoria
										# print()
										# print("SETOU MAIOR PRESSAO", self.dispositivosMqtt[k]["MAIOR_PRESSAO"], time.time())
										self.pressao_provisoria = None
										continue

									if self.dispositivosMqtt[k][k2] -10 > self.pressao_provisoria:
										self.start_time_pressao = time.time()
										# print()
										# print("RESETOU PRESSAO",  self.dispositivosMqtt[k][k2], self.pressao_provisoria, time.time())
										self.pressao_provisoria = None
										continue
									# print("CONDICAO PARA INCREMENTAR",self.pressao_provisoria - self.dispositivosMqtt[k][k2])
									if self.pressao_provisoria - self.dispositivosMqtt[k][k2] < 10:
										# print()
										# print("INCREMENTOU A PRESSAO", self.pressao_provisoria, self.dispositivosMqtt[k][k2])
										self.pressao_provisoria = self.dispositivosMqtt[k][k2]
									# elif self.pressao_provisoria - self.dispositivosMqtt[k][k2] > 10:
									# 	print("DESCARTOU INCREMENTO",  self.pressao_provisoria, self.dispositivosMqtt[k][k2])
							# else:
							# 	self.pressao_provisoria = None # zera o contador

						# if "pressao" in k2:

						# 	if self.dispositivosMqtt[k][k2] < self.dispositivosMqtt[k]["MAIOR_PRESSAO"]:
						# 		self.dispositivosMqtt[k]["COUNTER_MAIOR_PRESSAO"] += 1
						# 		if self.dispositivosMqtt[k]["COUNTER_MAIOR_PRESSAO"] == 3:
						# 			self.dispositivosMqtt[k]["MAIOR_PRESSAO"] = self.dispositivosMqtt[k][k2]
						# 			self.dispositivosMqtt[k]["COUNTER_MAIOR_PRESSAO"] = 0
						# 			# print("ATRIBUIU PRESSAO", self.dispositivosMqtt[k]["COUNTER_MAIOR_PRESSAO"])

						# 	else:
						# 		self.dispositivosMqtt[k]["COUNTER_MAIOR_PRESSAO"] = 0
								# print("Maior pressao", self.dispositivosMqtt["ARDUINO"]["MAIOR_PRESSAO"])

						if "frequencia" in k2 or "S_FREQUENCIA" in k2:
							a += 1
							if self.dispositivosMqtt[k][k2] > self.dispositivosMqtt[k]["MAIOR_FREQUENCIA"]:
								self.dispositivosMqtt[k]["MAIOR_FREQUENCIA"] = self.dispositivosMqtt[k][k2]


						if self.dispositivosMqtt[k]["S_INVERSOR_ANTERIOR"] == "falha"\
								and self.dispositivosMqtt[k]["S_INVERSOR"] == "INV_OK":
							self.dispositivosMqtt[k]["S_INVERSOR_ANTERIOR"] = "ok"
							self.counter_reset_inversor = 0
							self.msg_telegram_server("Inversor de frequência reativado.")

						if self.dispositivosMqtt[k]["S_INVERSOR"] == "INV_FAIL" and self.dispositivosMqtt[k]["S_INVERSOR_ANTERIOR"] != "falha":
								self.dispositivosMqtt[k]["S_INVERSOR_ANTERIOR"] = "falha"
								self.msg_telegram_server("Inversor de frequência em falha!")

						# if self.dispositivosMqtt[k]["S_INVERSOR"] == "INV_FAIL" and\
						# 		self.dispositivosMqtt["ARDUINO"]["LOOP_MSG_INVERSOR"] < time.time():
						# 	if self.counter_reset_inversor < 3:
						# 		self.serial_port.write(b'RESET_INV,30\n')
						# 		self.counter_reset_inversor += 1
						# 		self.dispositivosMqtt["ARDUINO"]["LOOP_MSG_INVERSOR"] = time.time() + (60 * 10)
						# 		self.dispositivosMqtt[k]["S_INVERSOR_ANTERIOR"] = "falha"
						# 		self.msg_telegram_server("Inversor de frequência em falha, tentando reiniciar")
						# 	else:
						# 		self.msg_telegram_server("Inversor de freqûencia permanentemente em falha!")
						# 		self.dispositivosMqtt["ARDUINO"]["LOOP_MSG_INVERSOR"] = time.time() + (60 * 30)

					except Exception as e:
						self.printException()
				# if a < 1:
				# 	print("def arduino() chave nao encontrada")


	def zera_leituras(self):
		for k, v in self.dispositivosMqtt.items():
			if "ARDUINO" in k:
				self.dispositivosMqtt[k]["MEDIA_FREQUENCIA"] = 0.
				self.dispositivosMqtt[k]["MAIOR_FREQUENCIA"] = 0.
				self.dispositivosMqtt[k]["MAIOR_PRESSAO"] = 0.
				self.dispositivosMqtt[k]["COUNTER_MAIOR_PRESSAO"] = 0

			if "VALVULA_CABINE" in k:
				self.dispositivosMqtt[k]["MEDIA_FLUXO_DE_AR"] = 0.
				self.dispositivosMqtt[k]["COUNTER_FLUXO_DE_AR"] = 0
				self.dispositivosMqtt[k]["TOTAL_FLUXO_DE_AR"] = 0

	def coletor(self, dispositivo, status):
		try:
			if "S_NIVEL" not in self.lastState[dispositivo].keys() or "S_EVAP" not in self.lastState[dispositivo].keys():
				self.dispositivosMqtt[dispositivo]["OSCILACOES_COLETORA"] = 0
				self.lastState[dispositivo]["S_NIVEL"] = status["S_NIVEL"]
		except:
			...
			
		DISPOSITIVOS_MQTT = self.dispositivosMqtt
		coletora = DISPOSITIVOS_MQTT[dispositivo]
		evaporador = False
		for k, v in DISPOSITIVOS_MQTT.items():
			if dispositivo[-3:] in k and "EVAPORADOR" in k:
				for k2, v2 in DISPOSITIVOS_MQTT[k].items():
					if "S_NIVEL_EVAPORADOR" in k2:
						if v2 != "CHEIO":
							evaporador = True

		try:
			''' verifica se existe chave no dicionario; caso não, cria'''
			DISPOSITIVOS_MQTT[dispositivo]["TIMEOUT"] == False
		except:
			self.dispositivosMqtt[dispositivo]["TIMEOUT"] = False
		try:
			if coletora["S_NIVEL"] == "CHEIO" and  coletora["S_BOMBA"] == "DESLIGADO":
				if DISPOSITIVOS_MQTT[dispositivo]["TIMEOUT"] == False:
					for k, v in DISPOSITIVOS_MQTT.items():
						if dispositivo[-3:] in k and "EVAPORADOR" in k:
							for k2, v2 in DISPOSITIVOS_MQTT[k].items():
								if "S_NIVEL_EVAPORADOR" in k2:
									if v2 != "CHEIO":
										envio = self.mqttc.publish(dispositivo, "LIGA_BOMBA", qos=2)
										self.msg_telegram_server(dispositivo + " cheia, ligando a bomba")
				else:
					if "{} falhou".format(dispositivo) not in self.erro:
						self.incluiErro("{} falhou".format(dispositivo))
			elif coletora["S_BOMBA"] == "LIGADO" and coletora["TEMPO_LIGADO"] == 0:
				self.dispositivosMqtt[dispositivo]["TEMPO_LIGADO"] = time.time()

			elif coletora["S_BOMBA"] == "LIGADO" and time.time() - coletora["TEMPO_LIGADO"] > 180 or evaporador:
				envio = self.mqttc.publish(dispositivo, "DESLIGA_BOMBA", qos=2)

			elif coletora["S_BOMBA"] == "DESLIGADO" and coletora["TEMPO_LIGADO"] > 0:
				elapsed_time = time.time() - coletora["TEMPO_LIGADO"]
				fim = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
				self.dispositivosMqtt[dispositivo]["TIMEOUT"] = True
				self.dispositivosMqtt[dispositivo]["TEMPO_LIGADO"] = 0
				self.msg_telegram_server("{} {} desligada após {}".format(dispositivo,coletora["S_NIVEL"].lower(), fim))
				if coletora["S_NIVEL"] == "VAZIO":
					saveFile.operacoesColetoras("{} {} {} {}\n".format(\
						time.strftime("%d/%m/%Y-%H:%M:%S"), fim, dispositivo, coletora["S_NIVEL"].lower()))
				elif coletora["S_NIVEL"] == "CHEIO":
					saveFile.falhasColetoras("{} {} {} {}\n".format(\
						time.strftime("%d/%m/%Y-%H:%M:%S"), fim, dispositivo, coletora["S_NIVEL"].lower()))
				else:
					saveFile.falhasColetoras("{} {} {} {}\n".format(\
						time.strftime("%d/%m/%Y-%H:%M:%S"), fim, dispositivo, coletora["S_NIVEL"].lower()))

			elif coletora["S_NIVEL"] == "VAZIO" and coletora["TEMPO_LIGADO"] > 0:
				elapsed_time = time.time() - coletora["TEMPO_LIGADO"]
				fim = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
				self.dispositivosMqtt[dispositivo]["TEMPO_LIGADO"] = 0

				self.msg_telegram_server("{} {} desligada após {}".format(dispositivo, coletora["S_NIVEL"].lower(), fim))

				saveFile.operacoesColetoras("{} {} {} {}\n".format(\
					time.strftime("%d/%m/%Y-%H:%M:%S"), fim, dispositivo, coletora["S_NIVEL"].lower()))

		except Exception as e:
			self.printException()

	def zera_oscilacao_coletora(self):
		for k, v in self.dispositivosMqtt.items():
			if "EVAP" in k and "S_EVAP" in v.keys():
				self.dispositivosMqtt[k]["OSCILACOES_COLETORA"] = 0
				self.dispositivosMqtt[k]["OSCILACOES_EVAPORADORA"] = 0
			if "COLETORA" in k and "S_NIVEL" in v.keys():
				self.dispositivosMqtt[k]["OSCILACOES_COLETORA"] = 0
				self.dispositivosMqtt[k]["OSCILACOES_EVAPORADORA"] = 0
			if "NIVEL" in k and "S_NIVEL" in v.keys():
				self.dispositivosMqtt[k]["OSCILACOES_COLETORA"] = 0
				self.dispositivosMqtt[k]["OSCILACOES_EVAPORADORA"] = 0

	def evaporadora_tripla(self, dispositivo, status):
		try:
			# print(json.dumps(status, indent=4))
			if "S_COL" in self.lastState[dispositivo].keys() or "S_EVAP" in self.lastState[dispositivo].keys():
				if "OSCILACOES" not in self.dispositivosMqtt[dispositivo].keys():
					self.dispositivosMqtt[dispositivo]["OSCILACOES_COLETORA"] = 0
					self.dispositivosMqtt[dispositivo]["OSCILACOES_EVAPORADORA"] = 0
					self.lastState[dispositivo]["S_COL"] = status["S_COL"]
					self.lastState[dispositivo]["S_EVAP"] = status["S_EVAP"]

			if "S_COL" not in self.dispositivosMqtt[dispositivo].keys():
				self.dispositivosMqtt[dispositivo]["S_COL"] = self.lastState[dispositivo]["S_COL"]
				self.lastState[dispositivo]["S_COL"] = status["S_COL"]
				self.lastState[dispositivo]["S_EVAP"] = status["S_EVAP"]

			if "S_COL"  in self.lastState[dispositivo].keys() and "S_COL" in self.dispositivosMqtt[dispositivo]:
				if self.dispositivosMqtt[dispositivo]["S_COL"] != self.lastState[dispositivo]["S_COL"]:
					self.dispositivosMqtt[dispositivo]["OSCILACOES_COLETORA"] += 1
					self.lastState[dispositivo]["S_COL"] = self.dispositivosMqtt[dispositivo]["S_COL"]
			else:
				self.lastState[dispositivo]["S_COL"] = self.dispositivosMqtt[dispositivo]["S_COL"]
				# print("{} não contém chave S_COL".format(dispositivo))

			if "S_EVAP"  in self.lastState[dispositivo].keys() and "S_EVAP" in self.dispositivosMqtt[dispositivo]:
				if self.dispositivosMqtt[dispositivo]["S_EVAP"] != self.lastState[dispositivo]["S_EVAP"]:
					self.dispositivosMqtt[dispositivo]["OSCILACOES_EVAPORADORA"] += 1
					self.lastState[dispositivo]["S_EVAP"] = self.dispositivosMqtt[dispositivo]["S_EVAP"]
			else:
				self.lastState[dispositivo]["S_EVAP"] = self.dispositivosMqtt[dispositivo]["S_EVAP"]
				# print("{} não contém chave S_EVAP".format(dispositivo))

		except:
			self.printException()



		try:
			# self.lastState[elements] = {"INICIO_EVAPORACAO": 0, "FIM_EVAPORACAO": 0, "ENVIO_MSG":0, "S_RESISTENCIA":""}
			if status["S_RES"] == "LIGADO":
				if self.lastState[dispositivo]["S_RES"] == "DESLIGADO":
					self.lastState[dispositivo]["S_RES"] = "LIGADO"
					self.lastState[dispositivo]["INICIO_EVAPORACAO"] = time.time()
					self.msg_telegram_server_direta("Resistencia de {} ligada".format(dispositivo))

				if time.time() - self.lastState[dispositivo]["ENVIO_MSG"] > 3600:
					self.lastState[dispositivo]["ENVIO_MSG"] = time.time()
					self.msg_telegram_server_direta("Resistencia de {} ligada\n**Duração**\n{}".format(dispositivo,\
						self.tempo_passado(self.lastState[dispositivo]["INICIO_EVAPORACAO"])))

			if "S_RES" in status.keys() and status["S_RES"] == "DESLIGADO" and "S_RES" in self.lastState[dispositivo].keys() and self.lastState[dispositivo]["S_RES"] == "LIGADO":
				self.lastState[dispositivo]["S_RES"] = "DESLIGADO"
				self.lastState[dispositivo]["ENVIO_MSG"] = time.time()
				self.lastState[dispositivo]["FIM_EVAPORACAO"] = time.time()
				self.msg_telegram_server_direta("Resistência de {} desligada após:\n{}\n**Níveis**\nEvaporador {}\nColetora {}".format(dispositivo,\
					self.tempo_passado(self.lastState[dispositivo]["INICIO_EVAPORACAO"]), status["S_EVAP"], status["S_COL"]))

		except:
			self.printException()

	def drenar_coletoras(self):
		try:
			for k, v in self.dispositivosMqtt.items():
				if "EVAP" in k and "S_COL" in v.keys():
					if v["S_COL"] == "CHEIO" or v["S_COL"] == "MEIO":
						self.bool_troca_ativada = False
						self.emit_status("Realizando a retirada de condensado da tubulação")
						# time.sleep(3)
						self.operacao_coletora = True
						resultado_acionamento = self.aciona_valvulas("FECHA", aciona_reverso = ["VALVULA_AZ_BY"])
						if len(resultado_acionamento) > 0:
							self.emit_status("Falha na retirada de condensado, coletando informações...")
							self.msg_telegram_server_direta("Não foi possível realizar a operação de esvaziamento das coletoras, por falhas nos equipamentos abaixo\n{}".format("\n".join(resultado_acionamento)))
							self.operacao_coletora = False
							return

						self.serial_port.write(b'SCT,800\n')
						self.thread_coleta_condensado = threading.Thread(target=self.coleta_condensado)
						self.thread_coleta_condensado.start()
						return
		except:
			self.printException()

	def coleta_condensado(self):
		try:
			for k, v in self.dispositivosMqtt.items():
				if "EVAP" in k and "S_COL" in v.keys():
					if v["S_EVAP"] == "CHEIO" and v["S_RES"] == "DESLIGADO":
						self.emit_status("Evaporadora já está cheia, ligando a evaporadora")
						self.mqttc.publish(k, "LIGA_RESISTENCIA", qos=2)
						continue
					if not self.abre_fecha_simples(k, "ABRE"):
						self.msg_telegram_server("a válvula de {} não abriu para esvaziar a coletora".format(k))
						self.operacao_coletora = False
						continue
					pressao_mais_alta = self.pressao
					inicio = time.time() + 120
					while inicio > time.time():
						if pressao_mais_alta > self.pressao:
							pressao_mais_alta = self.pressao
						if self.dispositivosMqtt[k]["S_EVAP"] == "CHEIO" or self.dispositivosMqtt[k]["S_VAL"] == "FECHADA":
							self.msg_telegram_server_direta("{} câmara de evaporaçao cheia após procedimento\nPressão máxima {}".format(k, pressao_mais_alta))
							break
						if self.dispositivosMqtt[k]["S_COL"] == "VAZIO":
							self.msg_telegram_server_direta("Coletora de {} esvaziada\nPressão máxima {}".format(k, pressao_mais_alta))
							break
						if self.dispositivosMqtt[k]["S_COL"] == "ERRO" or self.dispositivosMqtt[k]["S_EVAP"] == "ERRO":
							self.msg_telegram_server_direta("O sensor de nível apresentou erro durante a coleta de condensado em {}".format(k))
							break

					if inicio <= time.time():
						self.serial_port.write(b'STOP\n')
						self.msg_telegram_server_direta("Coletora de {} esvaziada\nPressão máxima {}".format(k, pressao_mais_alta))

			self.operacao_coletora = False
			self.serial_port.write(b'SCT,20\n')
		except:
			self.printException

	def evaporador(self, dispositivo, status):
		DISPOSITIVOS_MQTT = self.dispositivosMqtt
		try:
			if "S_NIVEL" not in self.lastState[dispositivo].keys():
				self.dispositivosMqtt[dispositivo]["OSCILACOES_EVAPORADORA"] = 0
				self.lastState[dispositivo]["S_EVAP"] = status["S_EVAP"]
		except:
			...

		if self.dispositivosMqtt[dispositivo]["S_COL"] != self.lastState[dispositivo]["S_COL"]:
			self.dispositivosMqtt[dispositivo]["OSCILACOES_COLETORA"] += 1
			self.lastState[dispositivo]["S_COL"] = self.dispositivosMqtt[dispositivo]["S_COL"]

		if self.dispositivosMqtt[dispositivo]["S_EVAP"] != self.lastState[dispositivo]["S_EVAP"]:
			self.dispositivosMqtt[dispositivo]["OSCILACOES_EVAPORADORA"] += 1
			self.lastState[dispositivo]["S_EVAP"] = self.dispositivosMqtt[dispositivo]["S_EVAP"]


		try:
			'''Carrega a função com o nome e o status das evaporadoras'''
			try:
				DISPOSITIVOS_MQTT[dispositivo]["DURACAO_RESISTENCIA"] == 0
			except KeyError:
				self.dispositivosMqtt[dispositivo]["DURACAO_RESISTENCIA"] = 0

			try:
				if DISPOSITIVOS_MQTT[dispositivo]["S_RESISTENCIA"] == "LIGADO" and\
				DISPOSITIVOS_MQTT[dispositivo]["DURACAO_RESISTENCIA"] == 0:
					operacao = saveFile.readArquivo("../instance/status/"+dispositivo, "DURACAO_RESISTENCIA")
					print(operacao)
					saveFile.writeArquivo("{}-\n".format(time.time()),"../instance/status/"+dispositivo, "DURACAO_RESISTENCIA")#dados, pasta, arquivo
					self.dispositivosMqtt[dispositivo]["DURACAO_RESISTENCIA"] = time.time()
					operacao = saveFile.readArquivo("../instance/status/"+dispositivo, "DURACAO_RESISTENCIA")
					if len(operacao) > 0:
						inicio = float(operacao[0].rstrip().split("-")[0])
						if inicio > 15482018100.0:
							self.dispositivosMqtt[dispositivo]["DURACAO_RESISTENCIA"] = inicio

						else:
							saveFile.writeArquivo("{}-\n".format(time.time()),"../instance/status/"+dispositivo, "DURACAO_RESISTENCIA")#dados, pasta, arquivo
							#print("passou2")
							self.dispositivosMqtt[dispositivo]["DURACAO_RESISTENCIA"] = time.time()
							# ~ print("passou3")
							# ~ print()
			except Exception as e:
				print('\b'*30, end = '')
				print("Atualizar rotina evap", end = '')
			try:
				for k, v in DISPOSITIVOS_MQTT[dispositivo].items():
					if "S_NIVEL" in k and not "TANQUE" in k and not "SIFAO" in k:
						if v == "CHEIO" and status["S_RESISTENCIA"] == "DESLIGADO":

							envio = self.mqttc.publish(dispositivo, "LIGA_RESISTENCIA", qos=2)
							self.msg_telegram_server("{} cheio, ligando a resistência".format(dispositivo.lower()))
							saveFile.writeArquivo("{}-\n".format(time.time()),"../instance/status/"+dispositivo, "DURACAO_RESISTENCIA")#dados, pasta, arquivo
			except Exception as e:
				self.printException()
			if DISPOSITIVOS_MQTT[dispositivo]["DURACAO_RESISTENCIA"] > 0 and DISPOSITIVOS_MQTT[dispositivo]["S_RESISTENCIA"] == "DESLIGADO":
				operacao = saveFile.readArquivo("../instance/status/"+dispositivo, "DURACAO_RESISTENCIA")
				self.dispositivosMqtt[dispositivo]["DURACAO_RESISTENCIA"] = 0
				inicio = float(operacao[0].rstrip().split("-")[0])
				elapsed_time = time.time() - inicio
				fim = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
				self.msg_telegram_server("{} desligou após {} ".format(dispositivo, fim))
				operacao =  "{}-{}\n".format(fim, time.strftime("%d/%m/%Y %H:%M:%S"))
				saveFile.writeArquivo(operacao, "../instance/status/"+dispositivo, "DURACAO_RESISTENCIA")#dados, pasta, arquivo

		except Exception as e:
			self.printException()

	def verifica_online(self):
		''' Verifica qual dispositivo está online '''
		urllib.request.urlopen("http://localhost:8000")
		self.troca_sch()

		data = {
			"codigo_cliente": Config.COD_CLIENTE,
			"codigo_estacao": Config.COD_ESTACAO,
			"codigo_bloco": "",
			"codigo_sub_bloco": "",
			"codigo_equipamento": "",
			"duracao": "",
			"situacao_teste": "",
			"mensagem": "",
			"valor": "",
			"indicacao": ""
		}
		time.sleep(5)
		tempo_iniciado = time.time() + 20
		while True:
			try:
				agora = time.time()
				_dispositivosMqtt = {}
				_dispositivosMqtt.update(**self.dispositivosMqtt)

				for elements in sorted(_dispositivosMqtt):
					try:
						cod_bloco = None
						if "COD_BLOCO" in self.dispositivosMqtt[elements]:
							cod_bloco = self.dispositivosMqtt[elements]["COD_BLOCO"]

						cod_sub_bloco = None
						if "COD_SUB_BLOCO" in self.dispositivosMqtt[elements]:
							cod_sub_bloco = self.dispositivosMqtt[elements]["COD_SUB_BLOCO"]

						data["codigo_bloco"] = cod_bloco
						data["codigo_sub_bloco"] = cod_sub_bloco
						data["codigo_equipamento"] = elements
						if agora - _dispositivosMqtt[elements]["TIME_MSG"] > 10 :
							self.lastState[elements]["S_CONEXAO"] = "OFFLINE"
							self.dispositivosMqtt[elements]["S_CONEXAO"] = "OFFLINE"

							if agora - _dispositivosMqtt[elements]["TIME_MSG"] > 60:
								if self.lastState[elements]["INTEGRACAO"] == False:
									data["duracao"] = "00:00:00"
									data["situacao_teste"] = "FALHA"
									data["mensagem"] = "EQUIPAMENTO OFFLINE"
									data["valor"] = ""
									data["indicacao"] = ""
									method = "LEITURA_EQUIPAMENTO_ESTACAO"
									if cod_bloco:
										method = "LEITURA_EQUIPAMENTO"
									registrar(method, data)
									enviar(method)
									self.lastState[elements]["INTEGRACAO"] = True
							self.dispositivos_off[elements]="{}".format(self.tempo_passado(_dispositivosMqtt[elements]["TIME_MSG"]))
							
							self.dispositivos_off["data"]=datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
							if elements == "ARDUINO":
								self.msg_telegram_server("**Atenção**\nPorta usb parou de responder, resetando o arduino")
								if self.serial_port is not None:
									self.serial_port.setDTR(False)
									time.sleep(1)
									self.serial_port.flushInput()
									self.serial_port.setDTR(True)
								else:
									print("Porta Serial não instanciada")
							if elements == "NIVEL_TANQUE":
								self.nivel_tanque = "----"


						if self.lastState[elements]["S_CONEXAO"] == "OFFLINE" and self.dispositivosMqtt[elements]["S_CONEXAO"] == "ONLINE"\
								and elements in self.dispositivos_off.keys():
							self.lastState[elements]["S_CONEXAO"] = "ONLINE"
							if isinstance(self.dispositivosMqtt[elements]["S_OSC_CONEXAO"], dict):
								self.dispositivosMqtt[elements]["S_OSC_CONEXAO"]["acumulado"] += 1
								self.dispositivosMqtt[elements]["S_OSC_CONEXAO"]["ultima_ocorrencia"] = time.time()
								self.dispositivosMqtt[elements]["S_OSC_CONEXAO"]["duracao"] = self.dispositivos_off[elements]
							else:
								self.dispositivosMqtt[elements]["S_OSC_CONEXAO"] += 1
							# print(elements, "Ficou online")
							try:
								if self.lastState[elements]["INTEGRACAO"] == True:
									integra_online = False
									if elements in self.dispositivosMqtt.keys():
										integra_online = True
									data["duracao"] = self.dispositivos_off[elements][-8:]
									data["situacao_teste"] = "SUCESSO"
									data["mensagem"] = "EQUIPAMENTO VOLTOU A FICAR ONLINE"
									data["valor"] = ""
									data["indicacao"] = ""

									if integra_online:
										method = "LEITURA_EQUIPAMENTO_ESTACAO"
										if cod_bloco:
											method = "LEITURA_EQUIPAMENTO"
										registrar(method, data)
										self.lastState[elements]["INTEGRACAO"] = False
							except:
								self.printException()
								print("FALHA NO BANCO DE DADOS")
							self.dispositivos_off.pop(elements, None) # exclui o dispositivo offline do dicionario
					except Exception as e:

						# print("adicionando dispositivo ao indice", elements, " " * 20,  end="\r")
						print(elements)
						self.printException()

				time.sleep(1)
			except Exception as e:
				print(e)
				self.printException()

	# def envia_integracao(self, dados):

	def aciona_valvulas(self, comando, aciona_reverso=[]):
		'''
		Metodo para acionar varias valvulas seja abrindo ou fechando
		'''
		if comando == "ABRE":
			inverso = "FECHA"
		if comando == "FECHA":
			inverso = "ABRE"
		erro = []
		for k in sorted(self.dispositivosMqtt.keys()):
			if "VALVULA" in k:
				if k == aciona_reverso:
					if not self.abre_fecha_simples(k, inverso):
						erro.append(k)
				else:
					if not self.abre_fecha_simples(k, comando):
						erro.append(k)
		return erro


	def abre_fecha_simples(self, dispositivo, comando):#(ABRE OU FECHA, ABERTA OU FECHADA)
		'''
		Retorna true ou false
		'''
		try:
			if any( item in dispositivo for item in self.desabilitado):
				return True

			meta = ""
			antes = ""
			status_key = ""
			bloco = ""
			for k, v in self.dispositivosMqtt[dispositivo].items():
				if comando in k:
					comando = v
				if "S_VALVULA" in k and not "FUNCIONAMENTO" in k:
					status_key, antes = k, v
			if status_key == "" or antes == "":
				print("Status da válvula não encontrado. {} {}".format(status_key, antes))
				return False
			if "ABRE" in comando:
				meta = "ABERTA"

			if "FECHA" in comando:
				meta = "FECHADA"
			# if self.dispositivosMqtt[dispositivo]["S_VALVULA"] == meta:
			# 	return True
			if self.dispositivosMqtt[dispositivo]["S_CONEXAO"] == "OFFLINE":
				if "VALVULA_CABINE" in dispositivo:
					self.msg_telegram_server("{} offline".format(dispositivo))
				print("ABRE_FECHA_SIMPLES", dispositivo, "OFFLINE")
				return False
			if "S_VALVULA" in self.dispositivosMqtt[dispositivo].keys():
				if self.dispositivosMqtt[dispositivo]["S_VALVULA"] == "ERRO":
					self.dispositivosMqtt[dispositivo]["S_FALHA_FC"] = True
					print("ABRE_FECHA_SIMPLES", dispositivo, "Fim de curso em falha")
					self.msg_telegram_server("{} Fim de curso em falha".format(dispositivo))
					return False

			if "S_VAL" in self.dispositivosMqtt[dispositivo].keys():
				if self.dispositivosMqtt[dispositivo]["S_VAL"] == "ERRO":
					self.dispositivosMqtt[dispositivo]["S_FALHA_FC"] = True
					print("ABRE_FECHA_SIMPLES", dispositivo, "Fim de curso em falha")
					self.msg_telegram_server("{} Fim de curso em falha".format(dispositivo))
					return False

			if antes != meta:
				tempoLimite = time.time() + 30
				envio = self.mqttc.publish(dispositivo, comando, qos=2)

				if meta == "FECHADA":
					self.emit_status("Fechando a válvula 1 {}".format(dispositivo))

				if meta == "ABERTA":
					self.emit_status("Abrindo a válvula 1 {}".format(dispositivo))

				tentativas = 1
				tempo_passado = time.time() + 3
				key_tempo_op = ""
				for k, v in self.dispositivosMqtt[dispositivo].items():
					if "TEMPO" in k and "OPERACAO" in k:
						key_tempo_op = k
						break
				while (tempoLimite > time.time()):

					if self.dispositivosMqtt[dispositivo]["S_CONEXAO"] == "ONLINE":
						if tempo_passado < time.time():
							tentativas += 1
							self.dispositivosMqtt[dispositivo]["S_TENTATIVAS"] = tentativas
							tempo_passado = time.time() + 1
							envio = self.mqttc.publish(dispositivo, comando, qos=2)
							self.emit_status("Acionando {}, tentativa:{} comando: {}".format(dispositivo, tentativas, comando))
							print("Acionando {}, tentativa:{} comando: {}".format(dispositivo, tentativas, comando), end="\r")

						try:
							tempo_op = 0

							try:
								tempo_op = int(''.join(filter(str.isdigit, self.dispositivosMqtt[dispositivo][key_tempo_op])))
							except:
								...

							if tempo_op > 2798:
								self.emit_status("{} não {}".format(bloco, meta.lower()))
								print("{} não {} tempo limite de 2800 excedido".format(dispositivo, meta.lower()))
								self.msg_telegram_server("{} não {} tempo limite de 2800 excedido".format(dispositivo, meta.lower()))
								return False

						except:
							self.printException()
							pass


						if self.dispositivosMqtt[dispositivo][status_key] == meta:
							self.emit_status("{} {}".format(dispositivo, meta.lower()))
							print("{} {} após {} tentativas".format(dispositivo, meta.lower(), tentativas ))
							# if self.dispositivosMqtt[dispositivo]["S_ERRO"] == True: #precisa concluir
							return True
					else:
						self.emit_status("{} offline".format(dispositivo))
						print("{} offline".format(dispositivo))
						#self.msg_telegram_server("{} ficou offline durante acionamento".format(dispositivo))
						return False
					time.sleep(.1)

				if self.dispositivosMqtt[dispositivo]["S_CONEXAO"] == "OFFLINE":
					print("ABRE_FECHA_SIMPLES", dispositivo, "OFFLINE")
					# self.msg_telegram_server("{} está offline durante acionamento".format(dispositivo))
					saveFile.erroDispositivo(dispositivo, comando)
					return False

				if tempoLimite <= time.time():
					self.dispositivosMqtt[dispositivo]["S_ERRO"] = True
					print("{} não {} após {} tentativas              ".format(dispositivo, meta.lower(), tentativas))
					self.msg_telegram_server("{} não {} após {} tentativas".format(dispositivo, meta.lower(), tentativas))
					return False
			else:
				self.dispositivosMqtt[dispositivo]["S_FALHA_FC"] = False
				#~ print("VERIFICADO AGORA {} já {}".format(dispositivo, meta))
				return True
		except:

			self.printException()
			return False

	def tempo_passado(self, tempo):
		# segundos = time.time() - tempo
		# dias = round(segundos / 86400)
		# minutos = round((segundos % 3600)) // 60
		# hora = round(segundos // 3600) % 24
		# segundos = round(segundos % 60)

		segundos = time.time() - tempo
		
		dias = int(segundos // 86400)
		segundos_restantes = segundos % 86400
		
		hora = int(segundos_restantes // 3600)
		segundos_restantes %= 3600
		
		minutos = int(segundos_restantes // 60)
		segundos = int(segundos_restantes % 60)
		
		if dias > 0:
			if dias == 1:
				return "{} dia {:0>2}:{:0>2}:{:0>2}".format(dias, hora, minutos, segundos)
			else:
				return "{} dias {:0>2}:{:0>2}:{:0>2}".format(dias, hora, minutos, segundos)			
		else:
			return "{:0>2}:{:0>2}:{:0>2}".format(hora, minutos, segundos)

	# Converte versão em string para tupla de inteiros
	def parse_version(self, vstr):
		return tuple(map(int, vstr.split(".")))


class MosquittoServer():
	def __init__(self, config, mosquitto, versao, print_exception):
		self.printException = print_exception
		self.config = config
		self.mosquitto = mosquitto
		self.client_server = self.config.CEMITERIO
		self.p = self.config.PORTA_MQTT_SERVER
		self.id = 0
		self.ip = ""		
		if self.config.COD_CLIENTE == 'CPS_001' and self.config.COD_ESTACAO == 'ETEN_001':
			self.ip_servidor = "10.8.0.10"
		else:
			self.ip_servidor = "10.10.0.1"

		self.versao = versao
		self.DISPOSITIVOS_MQTT = {}
		self.mqttc_server = mqtt_server.Client()
		# self.mqttc_server = mqtt_server.Client(mqtt_server.CallbackAPIVersion.VERSION1, self.client_server, transport="tcp")
		self.mqttc_server.on_message = self.on_message_server
		self.server_connected = "Desconectado"
		self.mqttc_local_to_server = None
		self.sepultados = None
		self.desativaTroca = None
		self.desativaTeste = None
		self.data_mqtt_server = {}
		self.data_mqtt_server["MSG_TELEGRAM"] = {"msg":"", "id":0}
		self.data_mqtt_server["VERSAO"] = self.versao
		self.serial_port_server = None
		self.mqttc_server.on_connect = self.on_connected_server
		self.mqttc_server.on_subscribe = self.on_subscribe_server
		self.mqttc_server.on_disconnect = self.on_disconnect_server
		self.thread_loop_mqtt = None
		# Uncomment to enable debug messages
		#~ self.mqttc_server.on_log = self.on_log_server
		self.inicio = time.time() + 20
		self.send_telegram_single = "" # variavel sentenciada para enviar telegramas
		self.send_telegram_all = "" # variavel sentenciada para enviar telegramas
		self.thread = threading.Thread(target=self.connect_mqtt_server)
		self.thread.start()
		self.thread_send_server = threading.Thread(target=self.send_server)
		self.thread_send_server.start()

	def printException(self):
		...
	def drenar_coletoras(self):
		...

	def msg_telegram_server(self, msg):
		self.id += 1
		self.data_mqtt_server["MSG_TELEGRAM"].update(**{"msg":msg, "id":self.id})

	def msg_telegram_server_direta(self, msg):
		self.id += 1
		self.data_mqtt_server["MSG_TELEGRAM"].update(**{"msg":msg, "id":str(self.id)})

	def troca_sch(self):
		pass

	def realiza_teste_estanqueidade(self):
		pass

	def on_log_server(self, client, userdata, level, buf):
		print("Log: ", buf)

	def connect_mqtt_server(self):
		while self.server_connected != "Conectado":
			print("Conectando ao servidor externo", self.ip_servidor)
			try:
				if "SHOWROOM" in self.client_server :
					self.mqttc_server.connect(self.ip_servidor, self.p, 60)
				else:
					self.mqttc_server.connect(self.ip_servidor, self.p, 60)
				self.server_connected = "Conectado"
				if self.thread_loop_mqtt == None:
					self.thread_loop_mqtt = threading.Thread(target=self.mqttc_server.loop_forever)
					self.thread_loop_mqtt.start()

			except Exception as e:
				print("Conexao servidor falhou")
				print("Tentando conexão server rede local")
				try:
					self.mqttc_server.connect("172.17.2.91", self.p, 60)
					self.server_connected = "Conectado"
					if self.thread_loop_mqtt == None:
						self.thread_loop_mqtt = threading.Thread(target=self.mqttc_server.loop_forever)
						self.thread_loop_mqtt.start()
				except Exception as e:
					print("Conexao server rede local falhou")

			time.sleep(5)

	def on_disconnect_server(self, client, userdata,  rc):
		try:
			self.server_connected = "Desconectado"
			print("Mqtt desconectado")
			self.thread = threading.Thread(target=self.connect_mqtt_server)
			self.thread.start()
		except:
			self.printException()

	def on_connected_server(self, mqttc_server, obj, flags, rc):
		self.server_connected = "Conectado"
		print("Conectado ao server mqtt")
		self.topic = "eten/"+ self.client_server
		self.mqttc_server.subscribe(self.topic, qos=1)

	def _emit_status_server(self, msg):
		'''
		Referenciada em app.py
		'''
		pass

	def _emit_status_server(self, msg):
		'''
		Referenciada em app.py
		'''
		pass
	def emit_status_server(self, function):
		'''
		Referencia função de mesmo nome em app.py
		'''
		self._emit_status = function

	def msg_sistema_server(self, msg):
		pass

	def msg_sistema_server(self, function):
		self.msg_sistema = function

	def on_subscribe_server(self, mqttc_server, obj, mid, granted_qos):
		print("subscribed server")

	def ler_api(self):
		pass

	def on_message_server(self, mqttc, obj, msg):			
			try:
				self.turned = msg.payload.decode()
				data = json.loads(self.turned)
				dataSave = ""
				print(json.dumps(data, indent=4, sort_keys=True))
				for k,v in data.items():
					store = ""
					if k == "drenar coletoras":
						self.drenar_coletoras()

					if k == "MQTT_LOCAL":
						print(v.split(",")[0], v.split(",")[1])
						envio = self.mqttc_local_to_server.publish(v.split(",")[0], v.split(",")[1], qos=2)

					if k == "PRINT TERMINAL":
						self.mosquitto.printTroca = not self.mosquitto.printTroca
						if self.mosquitto.printTroca:
							print("Print troca habilitado")
						else:
							print("Print desabilitado")
					if k == "ENVIAR SERIAL":
						print("SERIAL DATA = ", v, end = '')
						self.serial_port_server.write(v.encode("utf-8"))
						dataSave = "COMANDO SERIAL " + v
					if k == 'UPDATE':
						print("Realizando upgrade...")
						store = os.popen(v)
						dataSave = store.read()
						print("Upgrade finalizado...")
					if k == 'COMANDO SHELL':
						store = os.popen(v)
						dataSave = store.read()
					if k == 'TROCA GASOSA':
						print("Troca_gasosa mqtt server")
						self.troca_sch()
						dataSave = k
					if k == 'TESTE':
						print("Realiza teste mqtt server")
						self.realiza_teste_estanqueidade()
						dataSave = k
					if k == 'LER API':
						print("Ler api")
						self.ler_api()

					if k == 'DESABILITA':
						print("Cancela Troca mqtt server")
						self.mosquitto.bool_troca_ativada = False
						self.desativaTeste = True
						self.desativaTroca = True
						dataSave = k

					if k == 'HABILITA':
						print("Cancela Troca mqtt server")
						self.mosquitto.bool_troca_ativada = False
						self.desativaTeste = False
						self.desativaTroca = False
						self.testeDePressao = False
						self.bool_troca_ativada = False
						dataSave = k

					if k == 'CANCELA TESTE':
						print("Cancela teste mqtt server")
						self.desativaTeste = True
						self.desativaTroca = True
						dataSave = k

					if k == 'REINICIAR APP':
						store = os.popen('sudo systemctl restart nginx')
						dataSave = store.read()
					try:
						data = ""
						with open('../instance/LOG/log_update.txt', "r") as f:
							data = f.read()

						with open('../instance/LOG/log_update.txt', "w") as f:
							f.write(str(time.strftime("%d/%m/%Y-%H:%M:%S"))+dataSave+"\n"+data)

					except FileNotFoundError:
						if os.path.exists('../instance/LOG') == False:
							os.makedirs('../instance/LOG')

						with open('../instance/LOG/log_update.txt', "w") as f:
							f.write(str(time.strftime("%d/%m/%Y-%H:%M:%S"))+dataSave+"\n")

			except Exception as e:
				self.printException()
				return

	def send_server(self):
		inicio = time.time() - 1
		self.data_mqtt_server["COD_EST"] = self.config.COD_ESTACAO
		self.data_mqtt_server["COD_CLI"] = self.config.COD_CLIENTE

		def obter_ip_valido():
			try:
				result = subprocess.run(["hostname", "-I"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
				ip_list = result.stdout.strip().split()
			except Exception as e:
				print("Erro ao executar 'hostname -I':", e)
				return "127.0.0.1"

			for ip in ip_list:
				if ip.startswith("10.10.0"):
					return ip
			for ip in ip_list:
				if ip.startswith("10.8.0"):
					return ip
			if ip_list:
				return ip_list[0]  # Primeiro IP local
			return "127.0.0.1"  # Fallback final

		while True:
			try:
				if time.time() > inicio:
					inicio = time.time() + 10

					try:
						with open('/proc/uptime', 'r') as f:
							uptime_seconds = float(f.readline().split()[0])
							uptime_string = str(datetime.timedelta(seconds=uptime_seconds))

						ip = obter_ip_valido()
						self.data_mqtt_server["IP"] = ip
						self.ip = ip

						if self.data_mqtt_server is not None:
							self.data_mqtt_server["upTime"] = uptime_string
							self.data_mqtt_server["sepultados"] = self.sepultados
							self.data_mqtt_server["His.Test.pressao"] = "{}".format(self.ler_pressoes())

					except Exception:
						self.printException()
						if self.data_mqtt_server is not None:
							self.data_mqtt_server["His.Test.pressao"] = "file not found"

				if self.server_connected == "Conectado":
					try:
						del self.data_mqtt_server["conexao"]
					except:
						pass

					dicionario = {
						"STATUS": self.data_mqtt_server,
						"ETEN": self.client_server,
						"DISPOSITIVOS": self.DISPOSITIVOS_MQTT
					}
					data_mqtt = json.dumps(dicionario)
					self.mqttc_server.publish("eten/{}/out".format(self.client_server), data_mqtt, qos=1)

			except Exception as e:
				self.printException()

			if self.config.COD_CLIENTE == 'CPS_001' and self.config.COD_ESTACAO == 'ETEN_001':
				time.sleep(1800)
			else:
				time.sleep(1)



	def ler_pressoes(self):
		try:
			arquivo = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'instance/LOG', "teste_estanqueidade.txt"))
			dados = ""
			with io.open(arquivo,'r',encoding='utf8') as f:
				dados = f.readlines()
			dict_valvulas = {}
			string = ""
			try:
				for line in dados:
					infolist = line.split()
					if len(infolist) > 3 and "VALVULA" in infolist[2]:
						if infolist[2] not in dict_valvulas.keys():
							dict_valvulas[infolist[2]] = {"ultima": "\n{}\n     {} D= {} P= {} AV= {}\n".format(\
								infolist[2], infolist[0].split("-")[0], infolist[1], infolist[5], infolist[8])}
						elif len(dict_valvulas[infolist[2]]) < 3:
							if len(dict_valvulas[infolist[2]]) < 2:
								dict_valvulas[infolist[2]].update({"penultima":"     {} D= {} P= {} AV={}\n".format(\
									infolist[0].split("-")[0], infolist[1], infolist[5], infolist[8])})
							elif len(dict_valvulas[infolist[2]]) < 3:
								dict_valvulas[infolist[2]].update({"antepenultima":"     {} D= {} P= {} AV={}\n".format(\
									infolist[0].split("-")[0], infolist[1], infolist[5], infolist[8])})

				for k in sorted(dict_valvulas.keys()):
					string = string + dict_valvulas[k]["ultima"]
					if "penultima" in dict_valvulas[k].keys():
						string = string + dict_valvulas[k]["penultima"]
					if "antepenultima" in dict_valvulas[k].keys():
						string = string + dict_valvulas[k]["antepenultima"]
				return string
			except:
				self.printException()
				print("ERRO LENDO HISTÓRICO DE TESTES DE ESTANQUEIDADE")

		except FileNotFoundError:
			return "ERRO LENDO HISTÓRICO DE TESTES DE ESTANQUEIDADE"
		# try:
		# 	list_pressoes = []
		# 	arquivo = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'instance/LOG', "historico_pressao.txt"))

		# 	t = os.path.getmtime(arquivo)
		# 	alterado = datetime.datetime.fromtimestamp(t).strftime('%H:%M:%S %d/%m/%Y')
		# 	dados = ""
		# 	with io.open(arquivo,'r',encoding='utf8') as f:
		# 		dados = f.readlines()
		# 	for line in dados:
		# 		if len(line.rstrip().split("=")) > 1:
		# 			if "NICO" not in line:
		# 				bloco, press = line.rstrip().split("=")
		# 				pressao = press.split(",")[-1]
		# 				pressao2 = press.split(",")[-2]
		# 				if len(bloco.split("-")[0].replace("sucção bloco", "")) > 1:
		# 					list_pressoes.append([bloco, float(pressao2[1:]), float(pressao[1:])])
		# 				else:
		# 					list_pressoes.append([bloco, float(pressao2), float(pressao)])
		# 			else:
		# 				bloco, press = line.rstrip().split("=")
		# 				pressao = press.split(",")[-1]
		# 				pressao2 = press.split(",")[-2]
		# 				list_pressoes.append(["BLOCO 1", float(pressao2), float(pressao)])
		# 	return (alterado, list_pressoes)
		# except FileNotFoundError:
		# 	return ("Erro", "Arquivo não encontrado")