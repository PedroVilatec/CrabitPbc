# -*- coding: utf-8 -*-
versao = "1.2.6.5"
import sys, os, repackage
repackage.up()
import linecache
from infra.lib_sensors_db import get_sensors_id
from instance.config import Config
from instance.devices import Devices
from vilatec.operations.mqtt import Mosquitto, MosquittoServer
from vilatec.operations.pzem_004 import BTPOWER
from vilatec.operations.sheet import Sheet
from vilatec.operations.telegram import Bot
from vilatec.operations import saveFile
from vilatec.operations.op_facade import setTime, updateData, alertEmail, dailyEmail
from vilatec.infra.raspserial import getSerial
from vilatec.infra.check_internet import have_internet
from vilatec.operations.duplicate_filter import FiltraDuplicidade
import json
import serial
import serial.tools.list_ports
import sqlite3
import datetime
import schedule
import math
import time
import logging
from logging.config import dictConfig

from vilatec.operations.integracao import registrar, enviar, ler
import atributos
from flask import Flask, send_from_directory, abort
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import pkg_resources
from threading import Thread
import subprocess

import os
import subprocess



# subprocess.Popen(["vncserver", "-geometry", "1600x1200", "-randr", "1600x1200,1440x900,1024x768"])
# -------CONEXAO BANCO DE DADOS-------#
#~ import urllib.request
#~ import datetime
#~ import psycopg2
HORA_ENVIO_EMAIL = "09:03" # Hora de realizar o envio do email com o relatório diário
ATUALIZA_HORA_TESTE = "00:00" # Hora de atualizar a hora de realizar o teste de acordo com a planilha
ATUALIZA_HORA_TROCAS = "00:00" # Hora de atualizar as horas de realizar as trocas de acordo com a planilha

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
INSTANCE_DIR = os.path.join(os.path.dirname(ROOT_DIR), 'instance')  # /home/pi/Crabit/instance

app = Flask(__name__, instance_path=INSTANCE_DIR)
app.root_path = ROOT_DIR
db_uri = 'sqlite:///{}'.format(os.path.join(INSTANCE_DIR, 'banco', 'vilatec.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'secret!'

# socketio = SocketIO(app)
socketio = SocketIO(app, logger=True, engineio_logger=True)

db = SQLAlchemy(app)
pzem = BTPOWER()
thread = None
thread_email = None
thread_mqtt = None
HORA_TESTE_ESTANQUEIDADE_1 = "00:00"
pressao = 0
sys.stdout.write("\x1b]2;%s\x07" % 'GUNICORN') # Altera o título do terminal
global status_web
global analog_value
status_web = ""
mosquittoServer = None
global telegram_bot
telegram_bot = None
sheet = None
thread_online = None
devices = Devices()
desabilitado = []
# subprocess.Popen("vncserver -geometry 1600x1200 -randr 1600x1200,1440x900,1024x768",\
# 		shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
# 		close_fds=False)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler = logging.FileHandler('../instance/log_app.txt')
file_handler.setFormatter(formatter)
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
filtra = FiltraDuplicidade()
logger.addFilter(filtra.filtro)

def printException():
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	error = 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
	# logger.error(error)
	print (error)

try:
	mosquitto = Mosquitto(Config.CEMITERIO, Config.PORTA_MQTT_LOCAL, Config.DESABILITADO, printException)
	for elements in Config.DESABILITADO:
		print(elements, "DESATIVADO")
except AttributeError:
		printException()
		raise("ATUALIZE O SISTEMA")

mosquittoServer = MosquittoServer(Config, mosquitto, versao, printException)

mosquittoServer.mqttc_local_to_server = mosquitto.mqttc
mosquittoServer.desativaTroca = mosquitto.bool_troca_ativada
mosquitto.msg_telegram_server = mosquittoServer.msg_telegram_server
mosquitto.msg_telegram_server_direta = mosquittoServer.msg_telegram_server_direta
mosquittoServer.drenar_coletoras = mosquitto.drenar_coletoras



def ler_api():
	try:
		inicio = time.time()
		dict = {"codigo_cliente": Config.COD_CLIENTE, "codigo_estacao_tratamento": Config.COD_ESTACAO}
		lido = ler("LER_CONFIG", dict)
		fim = inicio - time.time()
		# print("Ler api", json.dumps(lido, indent = 4))
		# for k, v in mosquitto.dispositivosMqtt.items():
		# 	if "VALVULA_AM" in k and not "BY" in k:
		# 		if "sub_blocos" in mosquitto.lastState["turned_api"].keys():
		# 			for _blocos in mosquitto.lastState["turned_api"]["sub_blocos"]:
		# 				if _blocos["bloco"] == v["COD_BLOCO"]:
		# 					...
							# print("Dispositivo:", k, "Codigo do bloco:", _blocos["bloco"], "Sepultados", _blocos["quantidade_sepultado"])
		if "turned_api" not in mosquitto.lastState.keys():
			mosquitto.lastState["turned_api"] = {}
		mosquitto.lastState["turned_api"]["latencia"] = fim
		emit_status('Latência {}'.format(fim))
		print('Latência API {}'.format(fim))
		# print(lido)
		# if isinstance(lido, dict):
		mosquitto.lastState["turned_api"].update(lido)
		# else:
		# 	print(lido)
	except Exception as e:
		print("Erro ao ler api", printException())
		emit_status("Erro lendo API")
		time.sleep(5)

	try:
		print("Enviando leitura da estanqueidade")
		enviar("LEITURA_ESTANQUEIDADE")
		emit_status("Envio da estanqueidade realizado com sucesso!")
		print("Envio da estanqueidade realizado")
		time.sleep(5)
	except Exception as e:
		emit_status("Erro Enviando leitura estanqueidade API")
		time.sleep(5)
		print("Erro enviando leitura estanqueidade", e)

	try:
		print("Enviando leitura da troca gasosa")
		enviar("LEITURA_TROCA_GASOSA")
		emit_status("Envio da troca gasosa realizado com sucesso!")
		print("Envio da troca gasosa realizado")
		time.sleep(5)
	except Exception as e:
		emit_status("Erro Enviando leitura troca gasosa API")
		print("Erro enviando leitura troca gasosa", e)



# mosquittoServer.ler_api = ler_api

# Modelo da tabela para armazenamento das informacoes app Mauricio
class Registro(db.Model):
	__tablename__ = 'registros_webhook'  # Nome personalizado da tabela
	id = db.Column(db.Integer, primary_key=True)
	dados = db.Column(db.Text, nullable=False)
	enviado = db.Column(db.Boolean, default=False)

with app.app_context():
	db.create_all()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
backup_etens = os.path.join(ROOT_DIR, "../", 'instance','backup_etens.json')
last_backup_etens = os.path.join(ROOT_DIR, "../", 'instance','last_backup_etens.json')


dictConfig({
	'version': 1,
	'formatters': {'default': {
		'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
	}},
	'handlers': {
		'default_handler': {
			'class': 'logging.FileHandler',
			'encoding': "UTF-8",
			'formatter': 'default',
			'filename': 'crabit.log'
		}
	},
	'root': {
		'level': 'INFO',
		'handlers': ['default_handler']
	}
})


def salva_ramfs():
	saveFile.grava_ramfs(mosquitto.dispositivosMqtt, '/mnt/ramdisk/temp_disp.json')
	saveFile.grava_ramfs(mosquitto.lastState, '/mnt/ramdisk/last_state.json')

def grava_ramfs():
	saveFile.grava_ramfs(mosquitto.dispositivosMqtt, backup_etens)
	saveFile.grava_ramfs(mosquitto.lastState, last_backup_etens)

schedule.every(10).minutes.do(salva_ramfs)
schedule.every(3).hours.do(grava_ramfs)
schedule.every().day.at("07:10").do(mosquitto.drenar_coletoras)
schedule.every().day.at("00:00").do(mosquitto.zera_oscilacao_coletora)
schedule.every(4).hours.do(mosquitto.envia_disp_desconhecidos)

def atualiza_integracao():
	print("INICIANDO ATUALIZA INTEGRACAO")
	teste2 = Thread(target=ler_api)
	teste2.start()

schedule.every(1).hours.do(atualiza_integracao)

def onlineServices():
		global mosquittoServer
		global telegram_bot
		global sheet

		while True:
			if mosquittoServer.server_connected == "Conectado":
				try:
					if telegram_bot == None:
						telegram_bot = Bot(Config.CEMITERIO)
						telegram_bot.envia_telegram_all( "Sistema iniciado")
						mosquitto.envia_telegram_single = telegram_bot.envia_telegram_single
						mosquitto.envia_telegram_all = telegram_bot.envia_telegram_all

				except Exception as e:
					print("Erro telepot  ", e)
			else:
				print(mosquittoServer.server_connected)
			time.sleep(10)

def emit_status(_str):
	global status_web
	data = {'estado': _str}
	json_data = json.dumps(data)
	status_web = _str
	socketio.emit('status', json_data)
mosquitto.emit_status = emit_status # instancia a funcao emit_status em mqtt.py


@socketio.on("message")
def received_socket(str):
	'''
	Funçao chamada pela página web e/ou pelo app
	'''
	if str == "teste_api":
		print("Ler API")
		ler_api()
		# print("ZERA FLUXO", *100)
		# mosquitto.zera_fluxo_de_ar()
		# print("teste_api", getTotalSepultados())
		# ler_api()
		# print("teste_api", "FIM DA INTERACAO")


	if str == "teste_estanqueidade":
		# if Config.CEMITERIO != "SANTO AMARO EMLURB":
		teste_estanqueidade()


	if str == "troca_gasosa":
		#~ if Config.CEMITERIO != "SANTO AMARO ENLURB":
		troca_sch()




#~ def troca_efic():
	#~ """
	#~ Função para enviar o comando para o arduino realizar a troca mais o teste de eficiência
	#~ """
	#~ ser.write("EFIC\n".encode('utf-8'))


#~ def troca():
	#~ """
	#~ Função para enviar o comando para o arduino realizar a troca
	#~ """

	#~ ser.write("TESTE,30,100,10,80\n".encode('utf-8'))


#~ def teste_diario():
	#~ """
	#~ Função para enviar o comando para o arduino realizar o teste diário
	#~ """
	#~ ser.write("STRING\n".encode('utf-8')) #CRIAR STRING PARA FAZER O TESTE DIARIO


def formatarData(data):
	"""
	Função que converte datas de formato AAAA-MM-DD em DD/MM/AAAA

	:param data: String de data no formato AAAA-MM-DD
	:return: String de data no formato DD/MM/AAAA
	"""
	ano, mes, dia = str(data).split("-")
	return dia + '/' + mes + '/' + ano


def getEmails():
	"""
	Função de retorno de emails a serem enviados mensagens de alerta e de relatório

	:return: emails
	"""
	conn = sqlite3.connect('/home/pi/Crabit/instance/banco/vilatec.db')
	c = conn.cursor()
	emails = list(c.execute("SELECT email FROM usuario"))
	c.close()
	conn.close()
	list_emails = []
	for email in emails:
		list_emails.append(email[0])
	return list_emails


def email():
	date_now = datetime.datetime.now()
	email_date = date_now - datetime.timedelta(days=1)
	data = formatarData(email_date.date())
	emails = getEmails()
	dailyEmail(emails, data)

#schedule.every().day.at(HORA_ENVIO_EMAIL).do(email) # Rotina do envio do email
def curva_turbina():
	ser.write(('STOP\n').encode('utf-8'))
	time.sleep(5)
	for analog_value in range(0, 255):
		ser.write(('TURBINA,'+str(analog_value)+'\n').encode('utf-8'))
		time.sleep(10)

def troca_gasosa():
	pressao_sct = Config.PRESSAO_SCT
	# if "CAMPO SANTO" in Config.CEMITERIO :
	# 	now = datetime.datetime.now()
	# 	if now.hour < 19 and now.hour > 6:
	# 		print("Troca gasosa com rotação reduzida entre 07h e 19h apenas para as Eten's Campo Santo")
	# 		pressao_sct = "10"


	m3 = None
	valvula_cabine=""
	for k, v in devices.CONTROLADORES.items():
		if "VALVULA_CABINE" in k  and not "BL2" in k:
			valvula_cabine = k
			for k2, v2 in mosquitto.dispositivosMqtt[valvula_cabine].items():
				if "S_M3/h" in k2:
					m3 = v2
				if "S_M3_TOTAL" in k2:
					m3 = v2
			break
	global analog_value
	data = {
		"codigo_cliente": Config.COD_CLIENTE,
		"codigo_estacao": Config.COD_ESTACAO,
		"codigo_bloco": "",
		"codigo_sub_bloco": "",
		"fluxo_de_ar": "",
		"pressao": 0,
		"frequencia": 0,
		"quantidade_sepultados": 0,
		"temperatura_media": 0,
		"umidade": 0,
		"situacao_teste": "",
		"mensagem": "",
		"duracao": ""
	}
	try:
		if mosquitto.bool_troca_ativada == True:
			inicio = time.time()
			if telegram_bot and mosquittoServer.server_connected == "Conectado":
				telegram_bot.envia_telegram_all( "Iniciando a troca gasosa.")

			ser.write(('TURBINA,60\n').encode('utf-8'))
			time.sleep(10)
			#~ comando_serial = 'BOMBA,'+str(Config.DURACAO_BOMBA_DAGUA)+'\n'
			vazio = ["VAZIO", "BAIXO", "----"]
			if not Config.BOMBEAMENTO_FORCADO and mosquitto.nivel_tanque in vazio:
				emit_status("Nível do reservatório baixo. Bomba não será ligada")
				print("Nível do reservatório baixo. Bomba não será ligada")
				time.sleep(2)
			else:
				if Config.BOMBEAMENTO_FORCADO:
					print("COD_CLIENTE {} Bombeando fluido independente do nível".format(Config.COD_CLIENTE))
				ser.write(('BOMBA,'+str(Config.DURACAO_BOMBA_DAGUA)+'\n').encode('utf-8'))
				infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,"+str(Config.DURACAO_BOMBA_DAGUA), qos=2)
				breaker = False
				for segundo in range(Config.DURACAO_BOMBA_DAGUA, -1, -1):
					emit_status("Preparando para troca gasosa. Bombeando fluido, %02d:%02d" % (0, segundo))
					#~ print("Preparando para troca gasosa. Bombeando fluido, %02d:%02d" % (0, segundo))
					if mosquitto.bool_troca_ativada == False or mosquittoServer.desativaTroca:
						ser.write(b'STOP\n')
						infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,0", qos=2)
						ser.write(b'BOMBA,0\n')
						emit_status("Troca gasosa cancelada")
						return
					time.sleep(1)

			ser.write(b'BOMBA,0\n')
			infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,0", qos=2)
			time.sleep(1)
			#ser.write(b'STOP\n')
			#~ comando_serial = 'SCT,'+str(Config.PRESSAO_SCT)+'\n'
			aciona_valvula = False
			ser.write('TURBINA,128\n'.encode('utf-8'))
			time.sleep(0.5)
			ser.write(('SCT,'+str(pressao_sct)+'\n').encode('utf-8'))
			VALVULAS = ["VALVULA_AM","VALVULA_AZ"]
			valvulas_azuis = []
			valvulas_amarelas = []
			for disp in sorted(devices.CONTROLADORES.keys()):
				'''
				Contabiliza as valvulas existentes, fecha a valvula bypass azul e abre a valvula bypass amarela
				'''
				if any( item in disp for item in VALVULAS):
					error = None
					DISP_OFF = None
					if disp in mosquitto.dispositivosMqtt.keys():
						DISP_OFF = mosquitto.dispositivosMqtt[disp]["S_CONEXAO"] == "OFFLINE"
					if "AM_BY" in disp:
						if DISP_OFF:
							error = "Inicio:{}   Sepultados:{}  {} Offline\n".format(\
							str(time.strftime("%d/%m/%Y-%H:%M:%S")), getTotalSepultados(), disp)
						elif not mosquitto.abre_fecha_simples(disp, "ABRE"):
							print(disp, "Nao abriu para realizacao da troca gasosa")
							error = "Inicio:{}   Sepultados:{}  {} Nao abriu\n".format(\
							str(time.strftime("%d/%m/%Y-%H:%M:%S")), getTotalSepultados(), disp)
						else:
							print(disp, "Abriu para realizacao da troca gasosa")
					elif "AZ_BY" in disp:
						if DISP_OFF:
							error = "Inicio:{}   Sepultados:{}  {} Offline\n".format(\
							str(time.strftime("%d/%m/%Y-%H:%M:%S")), getTotalSepultados(), disp)
						elif not mosquitto.abre_fecha_simples(disp, "FECHA"):
							print(disp, "Nao fechou para realizacao da troca gasosa")
							error = "Inicio:{}   Sepultados:{}  {} Nao fechou\n".format(\
							str(time.strftime("%d/%m/%Y-%H:%M:%S")), getTotalSepultados(), disp)
						else:
							print(disp, "Fechou para realizacao da troca gasosa")
					elif "AZ" in disp:
						valvulas_azuis.append(disp)
					elif "AM" in disp:
						tem_valvula = True
						valvulas_amarelas.append(disp)

					if error:
						saveFile.falhaTroca(error)

			total_de_blocos = len(valvulas_amarelas)

			abre_valvula_cabine = mosquitto.abre_fecha_simples(valvula_cabine, "ABRE")
			for elements in range(1, len(valvulas_amarelas)):
				error = None
				'''
				Fecha todas as valvulas menos a primeira azul e amarela
				'''
				if not mosquitto.abre_fecha_simples(valvulas_amarelas[elements], "FECHA"):
					try:
						print(valvulas_amarelas[elements], "Nao fechou para troca gasosa")
						final = time.time() - inicio
						error = "{} não fechou\n".format(valvulas_amarelas[elements])
						data["codigo_bloco"] = mosquitto.dispositivosMqtt[valvulas_amarelas[elements]]["COD_BLOCO"]
						data["codigo_sub_bloco"] = mosquitto.dispositivosMqtt[valvulas_amarelas[elements]]["COD_SUB_BLOCO"]

						data["data_leitura"] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
						data["fluxo_de_ar"] = 0
						data["pressao"] = 0
						data["frequencia"] = 0
						data["quantidade_sepultados"] = 0
						data["temperatura_media"] = 0
						data["umidade"] = 0
						data["duracao"] = ""

						data["situacao_teste"] = "FALHA"
						data["mensagem"] = error
						salvar_json_mauricio("LEITURA_TROCA_GASOSA", data)
						registrar("LEITURA_TROCA_GASOSA", data)
					except:
						printException()
				if not mosquitto.abre_fecha_simples(valvulas_azuis[elements], "FECHA"):
					#~ print(valvulas_azuis[elements], "Nao fechou para troca gasosa", "linha 338")
					final = time.time() - inicio
					error = "{} não fechou\n".format(valvulas_azuis[elements])
					data["codigo_bloco"] = mosquitto.dispositivosMqtt[valvulas_azuis[elements]]["COD_BLOCO"]
					data["codigo_sub_bloco"] = mosquitto.dispositivosMqtt[valvulas_azuis[elements]]["COD_SUB_BLOCO"]

					data["data_leitura"] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
					data["fluxo_de_ar"] = 0
					data["pressao"] = 0
					data["frequencia"] = 0
					data["quantidade_sepultados"] = 0
					data["temperatura_media"] = 0
					data["umidade"] = 0
					data["duracao"] = ""

					data["situacao_teste"] = "FALHA"
					data["mensagem"] = error
					salvar_json_mauricio("LEITURA_TROCA_GASOSA", data)
					registrar("LEITURA_TROCA_GASOSA", data)
				if error:
					saveFile.falhaTroca(error)
			intervalo_bomba = time.time() + 180
			for index in range(total_de_blocos):
				mosquitto.zera_fluxo_de_ar()
				for k, v in devices.CONTROLADORES.items():
					if "VALVULA_CABINE" in k or "VCAB" in k:
						abre_valvula_cabine = mosquitto.abre_fecha_simples(k, "ABRE")
						break
				inicio = time.time()
				mosquitto.zera_leituras()
				if not mosquitto.abre_fecha_simples(valvulas_amarelas[index], "ABRE"):
					print(valvulas_amarelas[index], "Nao abriu para troca gasosa, passando para proximo bloco")
					final = time.time() - inicio
					resultado = "Inicio:{} Duracao:{}  Sepultados:{} {} não abriu\n".format(
					str(time.strftime("%d/%m/%Y-%H:%M:%S")), str(time.strftime("%H:%M:%S", time.gmtime(final))),\
							getTotalSepultados(), valvulas_amarelas[index])
					saveFile.falhaTroca(resultado)
					resultado_api = "{} não abriu\n".format(valvulas_amarelas[index])
					data["codigo_bloco"] = mosquitto.dispositivosMqtt[valvulas_amarelas[index]]["COD_BLOCO"]
					data["codigo_sub_bloco"] = mosquitto.dispositivosMqtt[valvulas_amarelas[index]]["COD_SUB_BLOCO"]

					data["data_leitura"] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
					data["fluxo_de_ar"] = 0
					data["pressao"] = 0
					data["frequencia"] = 0
					data["quantidade_sepultados"] = 0
					data["temperatura_media"] = 0
					data["umidade"] = 0
					data["duracao"] = ""

					data["situacao_teste"] = "FALHA"
					data["mensagem"] = resultado_api
					registrar("LEITURA_TROCA_GASOSA", data)
					salvar_json_mauricio("LEITURA_TROCA_GASOSA", data)
					continue
				if not mosquitto.abre_fecha_simples(valvulas_azuis[index], "ABRE"):
					print(valvulas_azuis[index], "Nao abriu para troca gasosa. a troca continuará... ")
					final = time.time() - inicio
					resultado = "Inicio:{} Duracao:{}  Sepultados:{} {} não abriu\n".format(
					str(time.strftime("%d/%m/%Y-%H:%M:%S")), str(time.strftime("%H:%M:%S", time.gmtime(final))),\
							getTotalSepultados(), valvulas_azuis[index])
					saveFile.falhaTroca(resultado)
					resultado_api = "{} não abriu\n".format( valvulas_azuis[index])
					data["codigo_bloco"] = mosquitto.dispositivosMqtt[valvulas_azuis[index]]["COD_BLOCO"]
					data["codigo_sub_bloco"] = mosquitto.dispositivosMqtt[valvulas_azuis[index]]["COD_SUB_BLOCO"]

					data["data_leitura"] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
					data["fluxo_de_ar"] = 0
					data["pressao"] = 0
					data["frequencia"] = 0
					data["quantidade_sepultados"] = 0
					data["temperatura_media"] = 0
					data["umidade"] = 0
					data["duracao"] = ""

					data["situacao_teste"] = "FALHA"
					data["mensagem"] = resultado_api
					registrar("LEITURA_TROCA_GASOSA", data)
					salvar_json_mauricio("LEITURA_TROCA_GASOSA", data)
				try:
					data["codigo_bloco"] = mosquitto.dispositivosMqtt[valvulas_amarelas[index]]["COD_BLOCO"]
				except:
					raise Exception("{}: BLOCO NÃO CADASTRADO".format(valvulas_amarelas[index]))

				try:
					data["codigo_sub_bloco"] = mosquitto.dispositivosMqtt[valvulas_amarelas[index]]["COD_SUB_BLOCO"]
				except:
					raise Exception("{}: SUB BLOCO NÃO CADASTRADO".format(valvulas_amarelas[index]))


				
				for minuto in range(Config.DURACAO_TROCA_GASOSA -1, -1, -1):
					for segundo in range(59, -1, -1):
						if mosquitto.bool_troca_ativada == False or mosquittoServer.desativaTroca:
							ser.write(b'STOP\n')
							ser.write(b'BOMBA,0\n')
							infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,0", qos=2)
							emit_status("Troca gasosa cancelada")
							return

						dict_ard = mosquitto.dispositivosMqtt["ARDUINO"]

						try:
							emit_status("Troca gasosa em {} {:02d}:{:02d} | M³ ar {:.3f}".format(valvulas_amarelas[index],minuto, segundo, mosquitto.fluxo_de_ar_atual()))
							print("\b"*200, end = '\r')							
							# print("{} {:02}:{:02} P={} m³/h={:.2f} m³total={} an_val={} freq={} MP={}".format(valvulas_amarelas[index].replace("VALVULA_", ""), minuto, segundo, dict_ard["pressao"], mosquitto.m3_hora, mosquitto.fluxo_de_ar_atual(), dict_ard["S_ANALOG VALUE"],dict_ard['frequencia'], dict_ard["MAIOR_PRESSAO"]), end = '')
							if mosquitto.printTroca:
								print("{} {:02}:{:02} P={} m³/h={:.2f} m³total={:.3f} m³={:.3f} m³troca={:.3f}  an_val={} freq={} MP={}  ".format(valvulas_amarelas[index].replace("VALVULA_", ""), minuto, segundo, dict_ard["pressao"], mosquitto.m3_hora, mosquitto.m3_total, mosquitto.m3_troca, mosquitto.fluxo_de_ar_atual(), dict_ard["S_ANALOG VALUE"],dict_ard['frequencia'], dict_ard["MAIOR_PRESSAO"]), end = '')
								# print("Valv. {} {:02}:{:02} Press={} m³/h={:.2f}  ar(m³)={:.3f}  an_val/freq= {}|{} MP={}  ".format(valvulas_amarelas[index].replace("VALVULA_", ""), minuto, segundo, dict_ard["pressao"], mosquitto.m3_hora, mosquitto.fluxo_de_ar_atual(), dict_ard["S_ANALOG VALUE"],dict_ard['frequencia'], dict_ard["MAIOR_PRESSAO"]), end = '')
						except:
							printException()


						if mosquitto.dispositivosMqtt[valvula_cabine]["S_VALVULA"] == "ABERTA"\
							and mosquitto.dispositivosMqtt[valvulas_azuis[index]]["S_VALVULA"] == "ABERTA":
							ser.write(('SCT,'+str(pressao_sct)+'\n').encode('utf-8'))
						else:
							ser.write(('SCT, '+str(pressao_sct)+'\n').encode('utf-8'))
						time.sleep(1)

						if intervalo_bomba < time.time() and mosquitto.nivel_tanque != "VAZIO":
							intervalo_bomba = time.time() + 180
							vazio = ["VAZIO", "BAIXO", "----"]
							if not Config.BOMBEAMENTO_FORCADO and mosquitto.nivel_tanque in vazio:
								emit_status("Nível do reservatório baixo. Bomba não será ligada")
								time.sleep(2)
							else:
								if Config.BOMBEAMENTO_FORCADO:
									print("COD_CLIENTE {} Bombeando fluido independente do nível".format(Config.COD_CLIENTE))
								analog_ant = str(analog_value)
								ser.write(b'TURBINA,60\n')
								time.sleep(5)
								ser.write(('BOMBA,'+str(Config.DURACAO_BOMBA_DAGUA)+'\n').encode('utf-8'))
								infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,"+str(Config.DURACAO_BOMBA_DAGUA), qos=2)
								for segundo in range(Config.DURACAO_BOMBA_DAGUA, -1, -1):
									emit_status("Bombeando fluido, {:02}:{:02}".format(0, segundo))
									time.sleep(1)
									if mosquitto.bool_troca_ativada == False or mosquittoServer.desativaTroca:
										ser.write(b'STOP\n')
										infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,0", qos=2)
										ser.write(b'BOMBA,0\n')
										emit_status("Troca gasosa cancelada")
										return

								ser.write(('TURBINA,'+analog_ant+'\n').encode('utf-8'))
								time.sleep(1)
								ser.write(b'BOMBA,0\n')
								infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,0", qos=2)

				final = time.time() - inicio
				resultado = "Inicio:{} Duracao:{} {} Fluxo_de_ar:{} Pressão:{} Frequência:{} Sepultados:{}\n".format(
				str(time.strftime("%d/%m/%Y-%H:%M:%S")), str(time.strftime("%H:%M:%S", time.gmtime(final))), valvulas_amarelas[index],
					round(mosquitto.fluxo_de_ar_atual(), 4), mosquitto.dispositivosMqtt["ARDUINO"]["MAIOR_PRESSAO"],\
						mosquitto.dispositivosMqtt["ARDUINO"]["MAIOR_FREQUENCIA"], getTotalSepultados())
				saveFile.resultadoTroca(resultado)
				# if telegram_bot and mosquittoServer.server_connected == "Conectado":
				# 	telegram_bot.envia_telegram_all( resultado)
				print("\nresultado da troca gasosa", resultado)

				data["fluxo_de_ar"] = mosquitto.fluxo_de_ar_atual()
				data["pressao"] = mosquitto.dispositivosMqtt["ARDUINO"]["MAIOR_PRESSAO"]
				data["frequencia"] = mosquitto.dispositivosMqtt["ARDUINO"]["MAIOR_FREQUENCIA"]
				data["quantidade_sepultados"] = int(getTotalSepultados())
				data["temperatura_media"] = mosquitto.dispositivosMqtt["ARDUINO"]["temperatura"]
				data["umidade"] = mosquitto.dispositivosMqtt["ARDUINO"]["umidade"]
				data["situacao_teste"] = "SUCESSO"
				data["mensagem"] = "TROCA GASOSA REALIZADA COM SUCESSO"
				data["data_leitura"] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
				data["duracao"] = str(time.strftime("%H:%M:%S", time.gmtime(final)))
				registrar("LEITURA_TROCA_GASOSA", data)
				salvar_json_mauricio("LEITURA_TROCA_GASOSA", data)
				# print("TROCA GASOSA REALIZADA COM SUCESSO", data)


				if index + 1 < len(valvulas_amarelas):
					mosquitto.abre_fecha_simples(valvulas_amarelas[index+1], "ABRE")
				if index + 1 < len(valvulas_azuis):
					mosquitto.abre_fecha_simples(valvulas_azuis[index+1], "ABRE")				
				for elements in range(len(valvulas_amarelas)):
					if index + 1 < len(valvulas_amarelas) and valvulas_amarelas[index+1] != valvulas_amarelas[elements]:					
						mosquitto.abre_fecha_simples(valvulas_amarelas[elements], "FECHA")
					else:
						if index + 1 < len(valvulas_amarelas):
							print("Não fechando a válvula " + valvulas_amarelas[index+1])
					if index + 1 < len(valvulas_azuis) and valvulas_azuis[index+1] != valvulas_azuis[elements]:
						mosquitto.abre_fecha_simples(valvulas_azuis[elements], "FECHA")	
					else:
						if index + 1 < len(valvulas_azuis):
							print("Não fechando a válvula " + valvulas_azuis[index+1])


				#~ if primeiro_range == True: #Condição para que não acione a primeira válvula duas vezes
					#~ primeiro_range = False
					#~ saveFile.resultadoTroca(primeira_amarela,resultado)
				#~ else:
					#~

			mosquitto.bool_troca_ativada = False
			ser.write(b'BOMBA,0\n')
			infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,0", qos=2)
			ser.write(b'SCT,20\n')

			aciona_valvula = False
			aciona_valvula = mosquitto.abre_fecha_simples(valvula_cabine, "FECHA")  # retorna True ou False
			if not aciona_valvula:
				mosquitto.incluiErro(aciona_valvula)
				saveFile.falhaTroca("{} Valvula cabine não fechou após troca gasosa\n".format(time.strftime("%d/%m/%Y-%H:%M:%S")))
				if telegram_bot and mosquittoServer.server_connected == "Conectado":
					telegram_bot.envia_telegram_all("Valvula cabine não fechou após troca gasosa")
				pass
			
			# if not "ETEN PARQUE DAS FLORES" in Config.CEMITERIO:
			# 	enviar("LEITURA_TROCA_GASOSA")

		
			for disp, v in sorted(devices.CONTROLADORES.items()):
				'''
				abre as válvulas amarelas após a troca
				'''
				if "AM" in disp:
					if not mosquitto.abre_fecha_simples(disp, "ABRE"):
						print(disp, "Nao abriu após realizacao da troca gasosa")
			emit_status("Troca gasosa finalizada")
			mosquitto.bool_troca_ativada = False
			enviar_pendentes()
			enviar("LEITURA_TROCA_GASOSA")

	except Exception as e:
		mosquitto.bool_troca_ativada = False
		printException()

def troca_sem_valvulas_amarelas():
	mosquitto.zera_fluxo_de_ar()
	valvula_cabine = ""
	for k, v in devices.CONTROLADORES.items():
		if "VALVULA_CABINE" in k or "VCAB" in k:
			valvula_cabine = k
	global analog_value
	data = {
		"codigo_cliente": Config.COD_CLIENTE,
		"codigo_estacao": Config.COD_ESTACAO,
		"codigo_bloco": "",
		"codigo_sub_bloco": "",
		"fluxo_de_ar": "",
		"pressao": 0,
		"frequencia": 0,
		"quantidade_sepultados": 0,
		"temperatura_media": 0,
		"umidade": 0,
		"situacao_teste": "",
		"mensagem": "",
		"duracao": ""
	}
	try:
		if mosquitto.bool_troca_ativada == True:
			inicio = time.time()
			if telegram_bot and mosquittoServer.server_connected == "Conectado":
				telegram_bot.envia_telegram_all( "Iniciando a troca gasosa.")

			#~ duracao_troca = Config.DURACAO_TROCA_GASOSA
			vazio = ["VAZIO", "BAIXO", "----"]

			if not Config.BOMBEAMENTO_FORCADO and mosquitto.nivel_tanque in vazio:
				emit_status("Nível do reservatório baixo. Bomba não será ligada")
				time.sleep(2)
			else:
				if Config.BOMBEAMENTO_FORCADO:
					print("COD_CLIENTE {} Bombeando fluido independente do nível".format(Config.COD_CLIENTE))
				ser.write(b'STOP\n')

				ser.write(('TURBINA,50\n').encode('utf-8'))
				#~ comando_serial = 'BOMBA,'+str(Config.DURACAO_BOMBA_DAGUA)+'\n'
				ser.write(('BOMBA,'+str(Config.DURACAO_BOMBA_DAGUA)+'\n').encode('utf-8'))
				infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,"+str(Config.DURACAO_BOMBA_DAGUA), qos=2)

				breaker = False

				for segundo in range(Config.DURACAO_BOMBA_DAGUA, -1, -1):
					emit_status("Preparando para troca gasosa. Bombeando fluido, %02d:%02d" % (0, segundo))
					#~ print("Preparando para troca gasosa. Bombeando fluido, %02d:%02d" % (0, segundo))
					if mosquitto.bool_troca_ativada == False:
						ser.write(b'STOP\n')
						infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,0", qos=2)
						ser.write(b'BOMBA,0\n')
						emit_status("Troca gasosa cancelada")
						return
					time.sleep(1)

			ser.write(b'BOMBA,0\n')
			infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,0", qos=2)
			time.sleep(1)
			#ser.write(b'STOP\n')
			#~ comando_serial = 'SCT,'+str(Config.PRESSAO_SCT)+'\n'
			aciona_valvula = False
			ser.write('TURBINA,128\n'.encode('utf-8'))
			time.sleep(0.5)
			ser.write(('SCT,'+str(Config.PRESSAO_SCT)+'\n').encode('utf-8'))
			VALVULAS = ["VALVULA_AM","VALVULA_AZ"]
			for disp in sorted(devices.CONTROLADORES.keys()):
				'''
				Contabiliza as valvulas existentes, fecha a valvula bypass azul e abre a valvula bypass amarela
				'''
				if any( item in disp for item in VALVULAS):
					error = None
					DISP_OFF = mosquitto.dispositivosMqtt[disp]["S_CONEXAO"] == "OFFLINE"
					if "AM_BY" in disp:
						if DISP_OFF:
							error = "Inicio:{}   Sepultados:{}  {} Offline\n".format(\
							str(time.strftime("%d/%m/%Y-%H:%M:%S")), getTotalSepultados(), disp)
						elif not mosquitto.abre_fecha_simples(disp, "ABRE"):
							print(disp, "Nao abriu para realizacao da troca gasosa")
							error = "Inicio:{}   Sepultados:{}  {} Nao abriu\n".format(\
							str(time.strftime("%d/%m/%Y-%H:%M:%S")), getTotalSepultados(), disp)
						else:
							print(disp, "Abriu para realizacao da troca gasosa")

					elif "AZ_BY" in disp:
						if DISP_OFF:
							error = "Inicio:{}   Sepultados:{}  {} Offline\n".format(\
							str(time.strftime("%d/%m/%Y-%H:%M:%S")), getTotalSepultados(), disp)
						elif not mosquitto.abre_fecha_simples(disp, "FECHA"):
							print(disp, "Nao fechou para realizacao da troca gasosa")
							error = "Inicio:{}   Sepultados:{}  {} Nao fechou\n".format(\
							str(time.strftime("%d/%m/%Y-%H:%M:%S")), getTotalSepultados(), disp)
						else:
							print(disp, "Fechou para realizacao da troca gasosa")
					elif "AZ" in disp:
						print("Foi detectado valvula amarela no sistema, verifique as configuracoes")
						sys.exit(0)
					elif "AM" in disp:
						print("Foi detectado valvula azul no sistema, verifique as configuracoes")
						sys.exit(0)

					if error:
						saveFile.falhaTroca(error)

			inicio = time.time()
			mosquitto.zera_leituras()
			intervalo_bomba = time.time() + 180
			for minuto in range(Config.DURACAO_TROCA_GASOSA -1, -1, -1):
				aciona_valvula = mosquitto.abre_fecha_simples(valvula_cabine, "ABRE")
				if not aciona_valvula:
					print("Valvula cabine nao abriu para troca gasosa")
				for segundo in range(59, -1, -1):
					if mosquitto.bool_troca_ativada == False:
						ser.write(b'STOP\n')
						ser.write(b'BOMBA,0\n')
						infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,0", qos=2)
						emit_status("Troca gasosa cancelada")
						return
					emit_status("Troca gasosa em {} {:02d}:{:02d}".format("Bloco 1",minuto, segundo))
					try:
						# print("{} {:02}:{:02} P={} m³/h={:.2f} m³total={} an_val={} freq={} MP={}".format(valvulas_amarelas[index].replace("VALVULA_", ""), minuto, segundo, dict_ard["pressao"], mosquitto.m3_hora, mosquitto.fluxo_de_ar_atual(), dict_ard["S_ANALOG VALUE"],dict_ard['frequencia'], dict_ard["MAIOR_PRESSAO"]), end = '')
						# if mosquitto.printTroca:
						if True:
							# print("{} {:02}:{:02} P={} m³/h={:.2f} m³total={:.3f} m³={:.3f} m³troca={:.3f}  an_val={} freq={} MP={}  ".format(valvulas_amarelas[index].replace("VALVULA_", ""), minuto, segundo, dict_ard["pressao"], mosquitto.m3_hora, mosquitto.m3_total, mosquitto.m3_troca, mosquitto.fluxo_de_ar_atual(), dict_ard["S_ANALOG VALUE"],dict_ard['frequencia'], dict_ard["MAIOR_PRESSAO"]), end = '')
							print("Valvula unica {:02}:{:02} Press={} m³/h={:.2f}  ar(m³)={:.3f}  an_val/freq= {}|{} MP={}  ".format( minuto, segundo, dict_ard["pressao"], mosquitto.m3_hora, mosquitto.fluxo_de_ar_atual(), dict_ard["S_ANALOG VALUE"],dict_ard['frequencia'], dict_ard["MAIOR_PRESSAO"]), end = '')
					except:
						printException()					
					
					if mosquitto.dispositivosMqtt[valvula_cabine]["S_VALVULA"] == "ABERTA":
						ser.write(('SCT,'+str(Config.PRESSAO_SCT)+'\n').encode('utf-8'))
					else:
						ser.write(('SCT,100\n').encode('utf-8'))

					time.sleep(1)
					if intervalo_bomba < time.time():
						intervalo_bomba = time.time() + 180
						vazio = ["VAZIO", "BAIXO", "----"]
						if not Config.BOMBEAMENTO_FORCADO and mosquitto.nivel_tanque in vazio:
							emit_status("Nível do reservatório baixo. Bomba não será ligada")
							time.sleep(2)
						else:
							if Config.BOMBEAMENTO_FORCADO:
								print("COD_CLIENTE {} Bombeando fluido independente do nível".format(Config.COD_CLIENTE))
							analog_ant = str(analog_value)
							ser.write(b'STOP\n')
							ser.write(b'TURBINA,60\n')
							time.sleep(.5)
							ser.write(('BOMBA,'+str(Config.DURACAO_BOMBA_DAGUA)+'\n').encode('utf-8'))
							infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,"+str(Config.DURACAO_BOMBA_DAGUA), qos=2)
							for segundo in range(Config.DURACAO_BOMBA_DAGUA, -1, -1):
								emit_status("Bombeando fluido, {:02}:{:02}".format(0, segundo))
								time.sleep(1)
								if mosquitto.bool_troca_ativada == False:
									ser.write(b'STOP\n')
									infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,0", qos=2)
									ser.write(b'BOMBA,0\n')
									emit_status("Troca gasosa cancelada")
									return
							ser.write(('TURBINA,'+analog_ant+'\n').encode('utf-8'))
							time.sleep(1)
							ser.write(b'BOMBA,0\n')
							infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,0", qos=2)
			final = time.time() - inicio
			resultado = "Inicio:{} Duracao:{} Fluxo_de_ar:{} Pressão:{} Frequência:{} Sepultados:{}\n".format(
			str(time.strftime("%d/%m/%Y-%H:%M:%S")), str(time.strftime("%H:%M:%S", time.gmtime(final))),\
				round(mosquitto.fluxo_de_ar_atual(),4), mosquitto.dispositivosMqtt["ARDUINO"]["MAIOR_PRESSAO"],\
					mosquitto.dispositivosMqtt["ARDUINO"]["MAIOR_FREQUENCIA"], getTotalSepultados())
			if telegram_bot and mosquittoServer.server_connected == "Conectado":
				telegram_bot.envia_telegram_all( resultado)
			print("resultado troca", resultado)
			saveFile.resultadoTroca(resultado)
			try:
				data["fluxo_de_ar"] = mosquitto.fluxo_de_ar_atual()
				data["pressao"] = mosquitto.dispositivosMqtt["ARDUINO"]["MAIOR_PRESSAO"]
				data["frequencia"] = mosquitto.dispositivosMqtt["ARDUINO"]["MAIOR_FREQUENCIA"]
				data["quantidade_sepultados"] = int(getTotalSepultados())
				data["temperatura_media"] = mosquitto.dispositivosMqtt["ARDUINO"]["temperatura"]
				data["umidade"] = mosquitto.dispositivosMqtt["ARDUINO"]["umidade"]
				data["situacao_teste"] = "SUCESSO"
				data["mensagem"] = "TESTE REALIZADO COM SUCESSO"
				data["duracao"] = str(time.strftime("%H:%M:%S", time.gmtime(final)))
				registrar("LEITURA_TROCA_GASOSA", data)
				salvar_json_mauricio("LEITURA_TROCA_GASOSA", data)
				ser.write(b'BOMBA,0\n')
				infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,0", qos=2)
				ser.write(b'SCT,20\n')
				aciona_valvula = False
				aciona_valvula = mosquitto.abre_fecha_simples(valvula_cabine, "FECHA")  # retorna True ou False
				if not aciona_valvula:
					mosquitto.incluiErro(aciona_valvula)
					saveFile.falhaTroca("{} Valvula cabine não fechou após troca gasosa\n".format(time.strftime("%d/%m/%Y-%H:%M:%S")))
					if telegram_bot and mosquittoServer.server_connected == "Conectado":
						telegram_bot.envia_telegram_all("Valvula cabine não fechou após troca gasosa")
					pass
				enviar("LEITURA_TROCA_GASOSA")
				# if not "ETEN PARQUE DAS FLORES" in Config.CEMITERIO:
				# 	enviar("LEITURA_TROCA_GASOSA")
			except:
				printException()
			emit_status("Troca gasosa finalizada")
			mosquitto.bool_troca_ativada = False

	except Exception as e:
		mosquitto.bool_troca_ativada = False
		printException()
def sifaoCheio():
	if mosquitto.sifao_cheio:
		emit_status("Sinal de nível sifão cheio!")
		mosquittoServer.msg_telegram_server("**Atenção**\nSinal de nível sifão cheio!")
		ser.write(b'STOP\n')
		print("Sinal de nível sifão cheio!")
		return True
	return False

def troca_sch():
	if  mosquittoServer.desativaTroca:
		emit_status("Troca gasosa desabilitada!")
		mosquittoServer.msg_telegram_server("**Atenção**\nTroca gasosa desabilitada!")
		return
	if sifaoCheio():
		mosquitto.bool_troca_ativada = False
		return

	if ser is not None:
	#~ if Config.CEMITERIO != "MCC LAB":
		if mosquitto.testeDePressao == True:
			emit_status("Existe um teste de estanqueidade em curso, aguarde a conclusão")

		if mosquitto.testeDePressao == False and mosquitto.bool_troca_ativada == False:
			#~ if Config.CEMITERIO != "SANTO AMARO EMLURB":
				print("Iniciando troca por schedule")
				mosquitto.bool_troca_ativada = True
				any_valvula = False
				for key in devices.CONTROLADORES.keys():
					if "VALVULA_AM" in key and not "BY" in key:
						any_valvula = True
						break
				if any_valvula:
					print("Troca gasosa com válvulas amarelas")
					troca = Thread(target=troca_gasosa)
					troca.start()
				else:
					print("Troca gasosa sem válvulas amarelas")
					troca = Thread(target=troca_sem_valvulas_amarelas)
					troca.start()
		else:
			emit_status("Já existe uma operação de troca gasosa em curso")
	else:
		if ser is None:

			mosquitto.incluiErro("Porta Serial não detectada!")
			emit_status("Porta Serial não detectada!")
		if mosquittoServer.desativaTeste or mosquittoServer.desativaTroca:
			emit_status("Troca gasosa desabilitada!")

mosquitto.troca_sch = troca_sch #para a classe Mosquitto acessar a funcao
mosquittoServer.troca_sch = troca_sch
time.sleep(10)
schedule.every().hour.do(troca_sch)

def sch_email():
	while True:
		schedule.run_pending()
		time.sleep(1)
		pass
"""

BANCO DE DADOS

Tabelas do banco de dados com seus atributos

"""


# class Obito(db.Model):
# 	"""

# 	Tabela do banco referente aos sepultados

# 	"""
# 	__tablename__ = "obito"
# 	_id = db.Column(db.INT, primary_key=True, autoincrement=True, nullable=False)
# 	nome = db.Column(db.VARCHAR(200), nullable=False)
# 	data_sepultamento = db.Column(db.DATE, nullable=False)
# 	hora_sepultamento = db.Column(db.TIME, nullable=False)
# 	loculo = db.Column(db.INT, nullable=False)

# 	def __init__(self, nome, data_sepult, hora_sepult, loculo):
# 		self.nome = nome
# 		self.data_sepultamento = data_sepult
# 		self.hora_sepultamento = hora_sepult
# 		self.loculo = loculo


# class Historico_Obito(db.Model):
# 	"""

# 	Tabela do banco espelho da tabela 'obito', onde os registros não são apagados

# 	"""
# 	__tablename__ = "historico_obito"
# 	_id = db.Column(db.INT, primary_key=True, autoincrement=True, nullable=False)
# 	loculo = db.Column(db.INT, nullable=False)
# 	nome = db.Column(db.VARCHAR(200), nullable=False)
# 	data_sepultamento = db.Column(db.DATE, nullable=False)
# 	hora_sepultamento = db.Column(db.TIME, nullable=False)

# 	def __init__(self, nome, data_sepult, hora_sepult, loculo):
# 		self.nome = nome
# 		self.data_sepultamento = data_sepult
# 		self.hora_sepultamento = hora_sepult
# 		self.loculo = loculo


class Sensor(db.Model):
	"""

	Tabela do banco referente aos valores ideiais dos sensores e seus intervalos de tolerância

	"""
	__tablename__ = "sensor"

	_id = db.Column(db.INT, primary_key=True, autoincrement=True, nullable=False)
	nome = db.Column(db.VARCHAR(100), nullable=False)
	valor_ideal = db.Column(db.VARCHAR(100))
	intervalo = db.Column(db.VARCHAR(100))

	def __init__(self, nome, valor, intervalo):
		self.nome = nome
		self.valor_ideal = valor
		self.intervalo = intervalo


class Tipo_Sensor(db.Model):
	"""

	Tabela do banco referente aos tipos de sensores existentes na estação

	"""
	__tablename__ = "tipo_sensor"

	_id = db.Column(db.VARCHAR(100), primary_key=True, nullable=False)
	tipo = db.Column(db.VARCHAR(100), nullable=False)

	def __init__(self, id, tipo):
		self._id = id
		self.tipo = tipo


class Usuario(db.Model):
	"""

	Tabela do banco referente aos usuários que irão receber os emails com as notificações.

	"""
	__tablename__ = "usuario"

	_id = db.Column(db.INT, primary_key=True, autoincrement=True, nullable=False)
	nome = db.Column(db.VARCHAR(200), nullable=False)
	email = db.Column(db.VARCHAR(200), nullable=False)

	def __init__(self, nome, email):
		self.nome = nome
		self.email = email

def controlValues(emails, value_dict):
	sensor_ideal_value = Sensor.query.all()
	trans_table = str.maketrans('ã', 'a')

	for obj in sensor_ideal_value:
		name = obj.nome.translate(trans_table).lower()
		ideal_value = float(obj.valor_ideal)
		intervalo = float(obj.intervalo)
		min, max = ideal_value - intervalo, ideal_value + intervalo

		id = ''

		sensor = get_sensors_id()
		for info in sensor:
			if info[1].lower() == name:
				id = info[0]

		try:
			value = float(value_dict[id])
			if value > max or value < min:
				alertEmail(emails, name, str(value), str(ideal_value))
		except:
			print("Nao existe valor ideal cadastrado")


def background_thread():
	"""
	Thread que é responsável por mostrar na tela as informações vindas do arduino.
	"""
	conn = sqlite3.connect('/home/pi/Crabit/instance/banco/vilatec.db')
	cursor = conn.cursor()
	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS leitura_consumo (
			id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
			data DATE NOT NULL,
			tarifa NUMERIC(10,4),
			valor NUMERIC(10,4),
			leitura_acumulada NUMERIC(15,4),
			leitura_dia NUMERIC(15,4),
			leitura_mes NUMERIC(15,4)
		)
		"""
	)


	# lendo os dados
	db_data = cursor.execute("""
	SELECT * FROM leitura_consumo;
	""").fetchall()
	conn.commit()

	#inserindo os valores caso nao haja dados na tabela
	if len(db_data) == 0:
		tarifa_inicial = 0.5493
		valor_inicial = 0.0000
		consumo_inicial = float(format(pzem.values['consumo']/1000))
		leitura_diaria_inicial = 0.0000
		leitura_mensal_inicial = 0.0000

		cursor.execute(""" INSERT INTO leitura_consumo (data, tarifa, valor, leitura_acumulada, leitura_dia, leitura_mes)
		VALUES (?, ?, ?, ?, ?, ?)
		""", (datetime.datetime.strptime("2021-01-01","%Y-%m-%d").date(), tarifa_inicial, valor_inicial, consumo_inicial, leitura_diaria_inicial, leitura_mensal_inicial))

		db_data = cursor.execute("""
		SELECT * FROM leitura_consumo;
		""").fetchall()

		conn.commit()

	consumo_anterior = db_data[-1][-1]
	tarifa = db_data[-1][2]
	data = db_data[-1][1]
	mes = data[5] + data[6]
	cursor.close()
	conn.close()
	dataDict = {"DISPOSITIVO":"ARDUINO", "STATUS":{}}
	string = []
	global pressao
	mosquitto.pressao = pressao
	global status_web
	global ser
	global analog_value
	global versao
	completo = 0
	incompleto = 0
	append_serial = ""
	while True:

		try:
			for i in range(0, len(string)):
				if not isinstance(string[i], str):
					line = string[i].decode("utf-8", "ignore")
				else:
					line = string[i]

				if "PSEG" in line:
					emit_status("SCT com pressão de segurança")

				if "CSP1" in line:
					emit_status("Calibrar sensores de pressão 1")

				if "CSP2" in line:
					emit_status("Calibrar sensores de pressão 2")									

				if "TROCA_GASOSA" in line:
					#~ if Config.CEMITERIO != "SANTO AMARO ENLURB":
					troca_sch()
					# os.system("DISPLAY=:0 xset TOTAL_FLUXO_DE_AR force on")

				if "LIGA_TELA" in line:
					#~ pyautogui.moveTo(100, 150)
					liga_tela()
					# os.system("DISPLAY=:0 xset TOTAL_FLUXO_DE_AR force on")

				elif "TESTE_PRESSAO" in line:
					liga_tela()
					# os.system("DISPLAY=:0 xset TOTAL_FLUXO_DE_AR force on")
					if not mosquitto.testeDePressao:
							teste_estanqueidade()
							if telegram_bot and mosquittoServer.server_connected == "Conectado":
								telegram_bot.envia_telegram_all("Teste de estanqueidade botão painel")
					else:

						time.sleep(1)
						emit_status("Já existe um teste de estanqueidade em curso")
						time.sleep(2)
						#~ if Config.CEMITERIO == "MCC LAB":
							#~ ser.write(b'STOP\n')

				elif find_between_r( line, "<", ">") != "":
					try:
						line = find_between_r( line, "<", ">")
						# line = line[1:-3]
						# # line = line[:-3]
						lista = line.split(',')
						nivel_tanque = ""
						if len(lista[3]) == 6:
							lista[3] = lista[3][:-1]
						if len(lista) > 8:
							try:
								temperatura = int(float(lista[0]))
							except (ValueError, IndexError):
								# printException()
								temperatura = 0							
							try:
								umidade = int(float(lista[1]))
							except (ValueError, IndexError):
								# printException()
								umidade = 0
							try:
								pressao = int(lista[2].split(".")[0]) * -1
							except (ValueError, IndexError):
								# printException()
								pressao = 0
							try:
								frequencia = float(lista[3])
							except:
								frequencia = 0

							status_inversor = lista[4]
							h2s = lista[5]
							reset_inv = lista[6]
							reset_12v = lista[7]
							status_bomba = lista[8]
							try:
								analog_value = lista[9].split(":")[1]
							except:
								...
							jump = False
							try:
								fluxo_de_ar = round(mosquitto.m3_hora, 2), # sensor6
							except:
								fluxo_de_ar = 0
							dataDict = {
								"DISPOSITIVO":"ARDUINO",
								"STATUS":{
								"DESABILITADOS":Config.DESABILITADO,
								"frequencia": frequencia,
								"S_INVERSOR": status_inversor,
								"S_H2S":h2s,
								"pressao": pressao,
								"S_RESET INV":reset_inv,
								"S_RESET 12V": reset_12v,
								"S_BOMBA":status_bomba,
								"S_ANALOG VALUE":analog_value,
								'temperatura': temperatura, # sensor1
								'umidade': umidade,# sensor2
								'conexao': "{} - IP {} - {}".format(mosquittoServer.server_connected, mosquittoServer.ip, datetime.datetime.now().strftime("%H:%M:%S")),
								'valvula_cabine': getattr(mosquitto, 'status_valvula_cabine', "OFFLINE"),  # sensor4
								'fluxo_de_ar': fluxo_de_ar,
								'nivel_tanque': mosquitto.nivel_tanque,
								'corrente': pzem.values['corrente'],
								'voltagem': pzem.values['voltagem'],
								'consumo': round((consumo_anterior),3),
								'valor_kwh':round((consumo_anterior)* tarifa, 2),
								'status_web':status_web,
								'versao':versao,
								'troca_gasosa':mosquitto.bool_troca_ativada,
								'teste_de_est':mosquitto.testeDePressao,
								# 'disp_off_dict':{k: v for k,v in mosquitto.dispositivos_off.items() if k not in "data"},
								'Erro':mosquitto.erro#,
								# 'disp_off':"Atualizado {}\n{} de {}".format(mosquitto.dispositivos_off["data"], len(mosquitto.dispositivos_off)-1, len(devices.CONTROLADORES))
									}
								}
							json_data = json.dumps(dataDict["STATUS"])
							socketio.emit('sensors', json_data)
							ard = json.dumps(dataDict)
							# print(json.dumps(dataDict, indent=4))
							infot = mosquitto.mqttc.publish("MCC\\RET_VALVULA", ard, qos=2)

							mosquittoServer.data_mqtt_server.update(dataDict["STATUS"])
							pop = mosquittoServer.data_mqtt_server.pop('disp_off_dict', None)
							pop = mosquittoServer.data_mqtt_server.pop('disp_off', None)							
							mosquittoServer.DISPOSITIVOS_MQTT.update(mosquitto.dispositivosMqtt)
							completo += 1
					except Exception as e:
						print(line)
						printException()
						print("Error <>")
				else:
					if "<" in line:
						incompleto +=1
						append_serial = line
						# print(line, "leitura completa", completo,  "Leitura incompleta", incompleto)

			if ser is not None:
				if ser.isOpen():
					if ser.in_waiting > 0:
						time.sleep(.05)
						string = ser.readlines()
						if append_serial != "" and len(string)  > 0:
							string[0] = append_serial.encode("utf-8") + string[0]
							# print("CONCATE", string[0])
							append_serial = ""
						# print(string)
							

			else:
				string = ["<0,0,0,0,0,0,0,0,0,0,0>"]
				time.sleep(.2)
			time.sleep(.3)
		except Exception as e:
			string = ["<0,0,0,0,0,0,0,0,0,0,0>"]
			printException()

@app.route('/imagens/<filename>')
def imagens(filename):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        abort(403)  # Bloqueia arquivos não permitidos	
    return send_from_directory(os.path.join(INSTANCE_DIR, 'imagens'), filename)

@app.route("/")
def index():
	"""
	Página principal, onde são mostrados os dados em tempo real.
	"""
	d1 = datetime.datetime.strptime(Config.DATA_MANU, "%d/%m/%Y")
	d2 = datetime.datetime.now()
	diff = d2 - d1
	days = diff.days
	months, days = days // 30, days % 30
	global thread
	global thread_email
	global thread_online
	if thread is None:
		thread = Thread(target=background_thread)
		thread.start()

	#~ if thread_online is None:
		#~ thread_online = Thread(target=onlineServices)
		#~ thread_online.start()

	if thread_email is None:
		thread_email = Thread(target=sch_email)
		thread_email.start()

	totalRows = getTotalSepultados()
	serial = getSerial()
	version_verify = None
	try:
		version = pkg_resources.get_distribution('flask_socketio').version
	except pkg_resources.DistributionNotFound:
		version = 'unknown'

	if version.startswith('5.'):
		script_path = '/static/scripts/socket.io.4.6.1.js'
	else:
		script_path = '/static/scripts/socket.io.min.js'

	if months >= Config.PRAZO_MANU:
		return render_template("index_alerta.html", title=Config.CEMITERIO, socketio_script=script_path, quant=totalRows, serial=Config.CEMITERIO.upper())

	else:

		return render_template("index.html", title=Config.CEMITERIO, socketio_script=script_path, quant=totalRows, serial=Config.CEMITERIO.upper())

"""
OPERAÇÕES DE USUÁRIO
"""
@app.route("/cadastrarUsuario")
def cadastrarUsuario():
	"""
	Função de redirecionamento para a página de cadastro de usuário
	"""
	return render_template("cadastroUsuario.html")


@app.route("/cadastroUsuario", methods=["GET", "POST"])
def cadastroUsuario():
	"""
	Função que realiza o cadastro de usuário no banco, com as informações fornecidas na paǵina de cadastro de usuário
	"""
	# if request.method == "POST":
	# 	nome = request.form.get("nome")
	# 	email = request.form.get("email")

	# 	if nome and email:
	# 		usuario = Usuario(nome, email)
	# 		db.session.add(usuario)
	# 		db.session.commit()

	return redirect(url_for("index.html"))


@app.route("/listaUsuarios")
def listaUsuarios():
	"""
	Função que mostra na tela a lista de usuários cadastrados
	"""
	usuarios = Usuario.query.all()
	return render_template("listaUsuarios.html", usuarios=usuarios)

@app.route("/excluirUsuario/<int:_id>")
def excluirUsuario(_id):
	"""
	Função para realizar a remoção de um usuário do sistema
	"""
	# usuario = Usuario.query.filter_by(_id=_id).first()
	# db.session.delete(usuario)
	# db.session.commit()
	return redirect(url_for("index.html"))

@app.route("/editarUsuario/<int:_id>", methods=["GET", "POST"])
def editarUsuario(_id):
	"""
	Função para realizar edição nos dados de um usuário
	"""
	# usuario = Usuario.query.filter_by(_id=_id).first()

	# if request.method == "POST":
	# 	nome = request.form.get("nome")
	# 	email = request.form.get("email")

	# 	if nome and email:
	# 		usuario.nome = nome
	# 		usuario.email = email
	# 		db.session.commit()

	# 	return redirect(url_for("listaUsuarios"))

	return render_template("index.html")

"""
OPERAÇÕES DE SEPULTADOS
"""
@app.route("/cadastrarSepultado")
def cadastrarSepultado():
	"""
	Função de redirecionamento para a página de cadastro de sepultado
	"""
	return render_template("index.html")


@app.route("/cadastroSepultado", methods=["GET", "POST"])
def cadastroSepultado():
	"""
	Função para cadastrar um sepultado
	"""
	# if (request.method == "POST"):
	# 	nome = request.form.get("nome")
	# 	data_sepult = request.form.get("data_sepult")
	# 	hora = request.form.get("hora_sepult")
	# 	hora_sepult = datetime.time(int(hora[:2]), int(hora[3:]))
	# 	ano = data_sepult[6] + data_sepult[7] + data_sepult[8] + data_sepult[9]
	# 	mes = data_sepult[3] + data_sepult[4]
	# 	dia = data_sepult[0] + data_sepult[1]
	# 	data_obj = datetime.date(int(ano), int(mes), int(dia))
	# 	loculo = request.form.get("loculo")

	# 	if (nome and data_sepult and hora_sepult and loculo):
	# 		c = Obito(nome, data_obj, hora_sepult, loculo)
	# 		hc = Historico_Obito(nome, data_obj, hora_sepult, loculo)
	# 		db.session.add(c)
	# 		db.session.add(hc)
	# 		db.session.commit()
	# 		if telegram_bot and mosquittoServer.server_connected == "Conectado":
	# 			telegram_bot.envia_telegram_all("Cadastro de sepultamento:\nNome:\n%s\nLoculo:\n%sHora:\n%s"%(nome, loculo, hora_sepult))
	# 		if sheet and mosquittoServer.server_connected == "Conectado":
	# 			sheet.updateListBody([loculo, nome, data_sepult, hora])

	return render_template("index.html")


@app.route("/editarSepultado/<int:_id>", methods=["GET", "POST"])
def editarSepultado(_id):
	"""
	Função para editar os dados de um sepultado
	"""
	# sepultado = Obito.query.filter_by(_id=_id).first()
	# historico_sepultado = Historico_Obito.query.filter_by(_id=_id).first()
	# if request.method == "POST":
	# 	nome = request.form.get("nome")
	# 	data_sepult = request.form.get("data_sepult")
	# 	hora = request.form.get("hora_sepult")
	# 	hora_sepult = datetime.time(int(hora[:2]), int(hora[3:5]))
	# 	ano = data_sepult[6] + data_sepult[7] + data_sepult[8] + data_sepult[9]
	# 	mes = data_sepult[3] + data_sepult[4]
	# 	dia = data_sepult[0] + data_sepult[1]
	# 	data_obj = datetime.date(int(ano), int(mes), int(dia))
	# 	loculo = request.form.get("loculo")

	# 	if nome and data_sepult and hora_sepult and loculo:
	# 		sepultado.nome = nome
	# 		sepultado.data_sepultamento = data_obj
	# 		sepultado.hora_sepultamento = hora_sepult
	# 		sepultado.loculo = loculo
	# 		if sheet and mosquittoServer.server_connected == "Conectado":
	# 			sheet.updateBody(historico_sepultado.loculo, [loculo, nome, data_sepult, hora])
	# 		if telegram_bot and mosquittoServer.server_connected == "Conectado":
	# 			telegram_bot.envia_telegram_all("Edicao de dados sepultado:\nNome:\n%s\nLoculo:\n%sHora:\n%s"%(nome, loculo, hora_sepult))
	# 		historico_sepultado.nome = nome
	# 		historico_sepultado.data_sepultamento = data_obj
	# 		historico_sepultado.hora_sepultamento = hora_sepult
	# 		historico_sepultado.loculo = loculo

	# 		db.session.commit()

	# 		return redirect(url_for("listaSepultados"))

	# dataFormatada = formatarData(sepultado.data_sepultamento)
	# horaFormatada = formatarHora(sepultado.hora_sepultamento)
	return render_template("index.html")
	# return render_template("editarSepultado.html", sepultado=sepultado, data=dataFormatada, hora=horaFormatada)


@app.route("/excluirSepultado/<int:_id>")
def excluirSepultado(_id):
	"""
	Função para realizar a remoção de um sepultado do banco
	"""
	# sepultado = Obito.query.filter_by(_id=_id).first()
	# if sheet and mosquittoServer.server_connected == "Conectado":
	# 	sheet.deleteBody(str(sepultado.loculo))
	# db.session.delete(sepultado)
	# db.session.commit()
	# if telegram_bot and mosquittoServer.server_connected == "Conectado":
	# 	telegram_bot.envia_telegram_all("Sepultado excluído:\n%s"%(sepultado.loculo))
	return render_template("index.html")
	# return redirect(url_for("listaSepultados"))


@app.route("/listaSepultados")
def listaSepultados():
	"""
	Função para demontrar a lista de sepultados
	"""
	# sepultados = Obito.query.all()
	return render_template("index.html")
	# return render_template("listaSepultados.html", sepultados=sepultados)

@app.route("/params")
def params():
	# arg1 = request.args['arg1']
	# arg2 = request.args['arg2']
	# print(arg1, arg2)
	# devices = mosquitto.dispositivosMqtt
#
	return render_template("index.html")
	# return render_template("listaValvulas.html", devices=devices)

@app.route("/listaValvulas")
def listaValvulas():
	"""
	Função para demontrar a lista de sepultados
	"""
	# devices = mosquitto.dispositivosMqtt
	return render_template("index.html")
	# return render_template("listaValvulas.html", devices=devices)


@app.route("/listaHistoricoSepultados")
def listaHistoricoSepultados():
	"""
	Função para demonstrar o histórico de sepultados
	"""
	# historico_sepultados = Historico_Obito.query.all()
	return render_template("index.html")
	# return render_template("listaHistoricoSepultados.html", sepultados=historico_sepultados)


"""
OPERAÇÕES DE VALOR IDEAL
"""
@app.route("/cadastrarValorIdeal")
def cadastrarValorIdeal():
	"""
	Função de redirecionamento para página de cadastro de valor ideal
	"""
	# sensores = Tipo_Sensor.query.all()
	return render_template("index.html")
	# return render_template("cadastroValorIdeal.html", sensores=sensores)


@app.route("/cadastroValorIdeal", methods=["GET", "POST"])
def cadastroValorIdeal():
	"""
	Função para cadastrar um novo valor ideal
	"""
	# if request.method == "POST":
	# 	nome_sensor = request.form.get("nome_sensor")
	# 	valor_ideal = request.form.get("valor_ideal")
	# 	intervalo = request.form.get("intervalo")
	# 	if nome_sensor and valor_ideal and intervalo:
	# 		valor = Sensor(nome_sensor, valor_ideal, intervalo)
	# 		db.session.add(valor)
	# 		db.session.commit()
	# 		if sheet and mosquittoServer.server_connected == "Conectado":
	# 			sheet.setValuesParameters()
	return render_template("index.html")
	# return redirect(url_for("listaValoresIdeais"))


def registerValues(values):
	values_len, sensor_len = len(values), len(Config.SENSORS_NAME)
	if values_len == sensor_len:
		for index in range(values_len):
			sensor = Config.SENSORS_NAME[index]
			value_db = Sensor.query.filter_by(nome=sensor).first()
			if float(value_db.valor_ideal) == float(values[index]):
				pass
			else:
				value_db.valor = float(values[index])
				db.session.commit()
	else:
		print("ideal values - list out of range")


@app.route("/editarValorIdeal/<string:nome>", methods=["GET", "POST"])
def editarValorIdeal(nome):
	"""
	Função para editar os dados de um valor ideal
	"""
	# sensor = Sensor.query.filter_by(nome=nome).first()
	# if request.method == "POST":
	# 	nome_sensor = request.form.get("nome_sensor")
	# 	valor = request.form.get("valor_ideal")
	# 	intervalo = request.form.get("intervalo")
	# 	if nome_sensor and valor and intervalo:
	# 		sensor.nome = nome_sensor
	# 		sensor.valor_ideal = valor
	# 		sensor.intervalo = intervalo
	# 		db.session.commit()
	# 		if sheet and mosquittoServer.server_connected == "Conectado":
	# 			sheet.setValuesParameters()
	# 		return redirect(url_for("listaValoresIdeais"))
	# return render_template("editarValorIdeal.html", sensor=sensor)
	return render_template("index.html")


@app.route("/excluirValorIdeal/<int:_id>")
def excluirValorIdeal(_id):
	"""
	Função para realizar a remoção de um valor ideal
	"""
	# valor = Sensor.query.filter_by(_id=_id).first()
	# nome = valor.nome
	# db.session.delete(valor)
	# db.session.commit()
	# if sheet and mosquittoServer.server_connected == "Conectado":
	# 	sheet.deleteValueParameter(nome)

	# return redirect(url_for("listaValoresIdeais"))
	return render_template("index.html")

@app.route("/listaValoresIdeais")
def listaValoresIdeais():
	"""
	Função para listar os valores ideais cadastrados
	"""
	# sensores = Sensor.query.all()
	# return render_template("listaValoresIdeais.html", sensores=sensores)
	return render_template("index.html")


"""
OPERAÇÕES COM SENSORES
"""
@app.route("/listaSensores")
def listaSensores():
	"""
	Função para listar na tela os sensores cadastrados
	"""
	# sensores = Tipo_Sensor.query.all()
	# return render_template("listaSensores.html", sensores=sensores)
	return render_template("index.html")


@app.route("/cadastrarSensor")
def cadastrarSensor():
	"""
	Função de redirecionamento para a página de cadastro de um novo sensor
	"""
	# return render_template("cadastroSensor.html")
	return render_template("index.html")


@app.route("/cadastroSensor", methods=["GET", "POST"])
def cadastroSensor():
	"""
	Função de cadastro de um novo sensor
	"""
	# if request.method == "POST":
	# 	id = request.form.get("id")
	# 	tipo = request.form.get("tipo")

	# 	if id and tipo:
	# 		sensor = Tipo_Sensor(id, tipo)
	# 		db.session.add(sensor)
	# 		db.session.commit()

	# return redirect(url_for("listaSensores"))
	return render_template("index.html")


@app.route("/excluirSensor/<string:_id>")
def excluirSensor(_id):
	"""
	Função para realizar a remoção de um sensor
	"""
	# sensor = Tipo_Sensor.query.filter_by(_id=_id).first()
	# db.session.delete(sensor)
	# db.session.commit()

	# return redirect(url_for("listaSensores"))
	return render_template("index.html")


@app.errorhandler(Exception)
def unhandled_exception(e):
	"""
	Função que mostra na tela uma determinada página quando ocorre qualquer tipo de erro
	"""
	app.logger.error("Unhadled exception: %s" % (e))
	print(e)
	return render_template("error.html")


def formatarHora(hora):
	"""
	Função para formatar a hora e mostrar na tela de edição de sepultados
	"""
	# return str(hora)[:5]
	return render_template("index.html")


def getTotalSepultados():
	try:
		total = ""
		if "turned_api" in mosquitto.lastState and "total_sepultados" in mosquitto.lastState["turned_api"]:
			total = mosquitto.lastState["turned_api"]["total_sepultados"]

		if str(total).isdigit():
			mosquittoServer.sepultados = 'API {}'.format(total)
			return int(total)
		else:
			mosquittoServer.sepultados = 'API {}'.format(0)
			return 0
			# conn = sqlite3.connect('/home/pi/Crabit/instance/banco/vilatec.db')troca_sch
			# c = conn.cursor()
			# totalRows = list(c.execute("SELECT COUNT(*) FROM obito").fetchall())[0][0]
			# c.close()
			# conn.close()
			# mosquittoServer.sepultados = 'local {}'.format(totalRows)
			# return totalRows

	except Exception as e:
		printException()
		return 0
		...
		# conn = sqlite3.connect('/home/pi/Crabit/instance/banco/vilatec.db')
		# c = conn.cursor()
		# totalRows = list(c.execute("SELECT COUNT(*) FROM obito").fetchall())[0][0]
		# c.close()
		# conn.close()
		# mosquittoServer.sepultados = 'local {}'.format(totalRows)
		# return totalRows

	# """
	# Função que conta no banco quantos sepultados existem

	# :return: Valor inteiro indicando a quantidade de sepultados no momento
	# """


def verifica_pressao_bloco(dispositivo, comando, _temValvula, cod_bloco="BL_001", cod_sub_bloco="SUB_001"):#return string
	global pressao
	pressao_mais_baixa = 0
	breaker = False
	breaker_while = False
	if "ABRE" in comando:
		meta = "abriu"

	if "FECHA" in comando:
		meta = "fechou"

	data = {
		"codigo_cliente": Config.COD_CLIENTE,
		"codigo_estacao": Config.COD_ESTACAO,
		"codigo_bloco": cod_bloco+'',
		"codigo_sub_bloco": cod_sub_bloco+'',
		"duracao": "",
		"situacao_teste": "",
		"mensagem": "",
		"pressao_ideal": "",
		"pressao_obtida": "",
		"valor_analogo": ""
	}
	
	try:
		if _temValvula:
			bloco = ""
			resultado = []
			for k in sorted(devices.CONTROLADORES.keys()):
				if "VALVULA" in k or "VCAB" in k:
					if "AM_BY" in k:
						aciona_valvula = mosquitto.abre_fecha_simples(k, "ABRE")
						if not aciona_valvula:
							resultado.append("{} não abriu".format(k))
							print("Valvula", k, "não abriu para teste de estanqueidade")
						continue
					if k != dispositivo:
						aciona_valvula = mosquitto.abre_fecha_simples(k, "FECHA")
						if not aciona_valvula:
							resultado.append("{} não fechou".format(k))
							print("Valvula", k, "não fechou para teste de estanqueidade")
			falha = ""
			if len(resultado) > 0:
				falha = "\n".join(resultado)
				if telegram_bot and mosquittoServer.server_connected == "Conectado":
					telegram_bot.envia_telegram_all("**FALHA TESTE ESTANQUEIDADE**\n{}".format(falha))
				

				# data["data_leitura"] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
				# data["fluxo_de_ar"] = 0
				# data["pressao"] = 0
				# data["frequencia"] = 0
				# data["quantidade_sepultados"] = 0
				# data["temperatura_media"] = 0
				# data["umidade"] = 0
				# data["duracao"] = ""

				# data["situacao_teste"] = "FALHA"
				# data["mensagem"] = falha
				# registrar("LEITURA_ESTANQUEIDADE", data)
				# salvar_json_mauricio("LEITURA_ESTANQUEIDADE", data)
				# return falha
			bloco = dispositivo
			emit_status("Acionando valvula {}".format(bloco))
			time.sleep(1)
			aciona_valvula = mosquitto.abre_fecha_simples(dispositivo, comando)  # retorna True ou False
			if not aciona_valvula:
				emit_status("Comando não realizado, informando ao suporte técnico.")
				if telegram_bot and mosquittoServer.server_connected == "Conectado":
					telegram_bot.envia_telegram_all("Problema executando comando {} {}".format(bloco, comando.lower()))
					mosquitto.incluiErro("{} Falha {} nao {}".format(time.strftime("%d/%m/%Y-%H:%M:%S"), dispositivo, meta))
				print(" busca do erro Falha {} {}".format( bloco, comando.lower()))
				
				falha2 = " | {} nao {}\n".format(dispositivo, meta)
				falha = "{}{}".format(falha, falha2)

				# data["data_leitura"] = ""
				# data["fluxo_de_ar"] = 0
				# data["pressao"] = 0
				# data["frequencia"] = 0
				# data["quantidade_sepultados"] = 0
				# data["temperatura_media"] = 0
				# data["umidade"] = 0
				# data["duracao"] = ""

				# data["situacao_teste"] = "FALHA"
				# data["mensagem"] = falha
				# registrar("LEITURA_ESTANQUEIDADE", data)
				# salvar_json_mauricio("LEITURA_ESTANQUEIDADE", data)
				# return "{} Falha {} nao {}".format(time.strftime("%d/%m/%Y-%H:%M:%S"), dispositivo, meta)
			else:
				emit_status("Acionamento da {} realizado.".format(bloco))
				elapsed_time = time.time() + 60
				print("Pressao inicial", pressao, dispositivo)
				while pressao < -10 and elapsed_time > time.time():
					print(("Aguardando a pressão estabilizar {} - {}".format(pressao, round(elapsed_time - time.time()))))
					emit_status("Aguardando a pressão estabilizar {} - {}".format(pressao, round(elapsed_time - time.time())))
					ser.write(b'STOP\n')
					time.sleep(1)
				if elapsed_time <= time.time():
						falha = "{}Pressão de -50 não atingida em um minuto\n".format(falha)
						# mosquitto.testeDePressao = False
						emit_status("T. E. cancelado. Pressão de -50 não atingida em um minuto")
						# data["data_leitura"] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
						# data["fluxo_de_ar"] = 0
						# data["pressao"] = 0
						# data["frequencia"] = 0
						# data["quantidade_sepultados"] = 0
						# data["temperatura_media"] = 0
						# data["umidade"] = 0
						# data["duracao"] = ""
						# data["situacao_teste"] = "FALHA"
						# data["mensagem"] = "Pressão de -50 não atingida em um minuto"
						# registrar("LEITURA_ESTANQUEIDADE", data)
						# salvar_json_mauricio("LEITURA_ESTANQUEIDADE", data)
						# return


			inicio = time.time()
			breaker = False
			breaker_while = False
			counter_pressao_estavel = 0
			pressao_mais_baixa_instavel = 0
			verifica_final = False
			time_verifica_pressao_atingida = time.time()
			while breaker_while == False:
				minuto = int(Config.REGRESSIVA)
				breaker = False
				for minuto in range(minuto - 1, -1, -1):
					if breaker == True:
						break
					for segundo in range(59, -1, -1):
						if mosquitto.testeDePressao == False:
							ser.write(b'STOP\n')
							emit_status("Teste de estanqueidade cancelado")
							# data["data_leitura"] = str(time.strftime('%Y-%m-%d %H:%M:%S'))
							# data["fluxo_de_ar"] = 0
							# data["pressao"] = 0
							# data["frequencia"] = 0
							# data["quantidade_sepultados"] = 0
							# data["temperatura_media"] = 0
							# data["umidade"] = 0
							# data["duracao"] = ""
							# data["situacao_teste"] = "FALHA"
							# data["mensagem"] = "Teste de estanqueidade cancelado"
							# registrar("LEITURA_ESTANQUEIDADE", data)
							# salvar_json_mauricio("LEITURA_ESTANQUEIDADE", data)
							return
						if breaker == True:
							break
						elapsed_time = time.time() - inicio

						emit_status("Teste de estanqueidade | %s | timer: %02d:%02d | Checkpoint %.1f | Duração %s"  %(bloco, minuto, segundo, pressao_mais_baixa, time.strftime("%H:%M:%S", time.gmtime(elapsed_time))))
						string_pressao = "TURBINA,"+str(Config.ANALOG_VALUE)+"\n"
						ser.write(string_pressao.encode('utf-8'))
						tempo_verificacao_pressao = time.time() + 1

						# while tempo_verificacao_pressao > time.time():

						# 	if verifica_final == True and float(pressao) > float(pressao_mais_baixa):
						# 		verifica_final = False
						# 	if float(pressao) < float(pressao_mais_baixa):
						# 		pressao_mais_baixa = float(pressao)

						# 		if float(pressao_mais_baixa) <= float(Config.PRESSAO_IDEAL):
						# 			if time_verifica_pressao_atingida < time.time():
						# 				time_verifica_pressao_atingida = time.time() + 10 #período em que a pressao deve permanecer estável
						# 				if verifica_final == True:
						# 					emit_status("Verificação do {} finalizada".format(bloco))
						# 					time.sleep(1)
						# 					breaker_while = True
						# 					breaker = True
						# 					break
						# 				verifica_final = True

						# 		breaker = True #instrucao para resetar o countdown
						# 		break
						# 		# ~ if minuto == 0:
						# 			# ~ if telegram_bot and mosquittoServer.server_connected == "Conectado":
						# 				# ~ telegram_bot.envia_telegram_single("334240998", "valor setado abaixo de 1 minuto em {}".format(bloco))
						# 	pressao_mais_baixa = float(pressao)
						# 	time.sleep(.1)

						while tempo_verificacao_pressao > time.time():
							if pressao_mais_baixa_instavel >= pressao_mais_baixa:
								counter_pressao_estavel = 0

							if float(pressao) < float(pressao_mais_baixa):
								pressao_mais_baixa_instavel = float(pressao)
								if counter_pressao_estavel < 20:
										counter_pressao_estavel += 1
								if counter_pressao_estavel == 20:
									counter_pressao_estavel = 0
									pressao_mais_baixa = pressao_mais_baixa_instavel
									pressao_mais_baixa_instavel = pressao_mais_baixa
									if float(pressao_mais_baixa) < float(Config.PRESSAO_IDEAL):
										emit_status("Verificação do {} finalizada".format(bloco))
										time.sleep(1)
										breaker_while = True
										breaker = True
										break
									breaker = True #instrucao para resetar o countdown
									break
								# ~ if minuto == 0:
									# ~ if telegram_bot and mosquittoServer.server_connected == "Conectado":
										# ~ telegram_bot.envia_telegram_single("334240998", "valor setado abaixo de 1 minuto em {}".format(bloco))
							time.sleep(.1)

				if minuto == 0 and segundo == 0:
					breaker_while = True
			final = time.time()
			duracao = final - inicio
			if len(falha) > 0:
				
				resultante ="F - {} {} {} P.I {} {} {} an {} sep {} \n".\
					format(time.strftime("%d/%m/%Y-%H:%M:%S"), time.strftime("%H:%M:%S", time.gmtime(duracao)),\
					bloco,  Config.PRESSAO_IDEAL, pressao_mais_baixa, round(Config.PRESSAO_IDEAL - pressao_mais_baixa),\
					str(Config.ANALOG_VALUE), getTotalSepultados())
				saveFile.falhaTeste("{} falha {}".format(resultante, falha)) # primeira ocorrência
			else:
				resultante ="{} {} {} P.I {} {} {} an {} sep {}\n".\
								format(time.strftime("%d/%m/%Y-%H:%M:%S"), time.strftime("%H:%M:%S", time.gmtime(duracao)),\
								bloco,  Config.PRESSAO_IDEAL, pressao_mais_baixa, round(Config.PRESSAO_IDEAL - pressao_mais_baixa),\
								str(Config.ANALOG_VALUE), getTotalSepultados())				
			saveFile.historico_pressao(bloco, pressao_mais_baixa)
			
			saveFile.resultadoTeste(resultante)
			if len(falha) > 0:
				data["situacao_teste"] = "FALHA"
				data["mensagem"] = falha
			else:
				data["situacao_teste"] = "SUCESSO"
				data["mensagem"] = "Teste de estanqueidade realizado com sucesso"
			data["duracao"] = time.strftime("%H:%M:%S", time.gmtime(duracao))
			data["pressao_ideal"] = round(Config.PRESSAO_IDEAL,2)
			data["pressao_obtida"] = round(pressao_mais_baixa,2)
			data["valor_analogo"] = Config.ANALOG_VALUE
			registrar("LEITURA_ESTANQUEIDADE", data)
			salvar_json_mauricio("LEITURA_ESTANQUEIDADE", data)
			return resultante

		else:
			bloco = "Bloco 1"
			'''
			passa pelo trexo se houver apenas a válvula da cabine no bloco
			'''
			aciona_valvula = False
			for k, v in mosquitto.dispositivosMqtt.items():
				if "VALVULA_CABINE" in k or "VCAB" in k:
					for k2, v2 in v.items():
						if "FECHA" in k2:
							aciona_valvula = mosquitto.abre_fecha_simples(k, "FECHA")  # retorna True ou False
							break
					break
			if not aciona_valvula:
				msg = "Válvula cabine não fechou para teste de estanqueidade.\n"
				if telegram_bot and mosquittoServer.server_connected == "Conectado":
					telegram_bot.envia_telegram_all(msg)
				emit_status(msg)
				saveFile.falhaTeste(msg)
				return (msg)
			ser.write(b'STOP\n')
			time.sleep(2)
			inicio = time.time()
			breaker = False
			breaker_while = False
			while breaker_while == False:
				minuto = int(Config.REGRESSIVA)
				breaker = False
				for minuto in range(minuto - 1, -1, -1):
					if breaker == True:
						break
					for segundo in range(59, -1, -1):
						if breaker == True:
							break
						elapsed_time = time.time() - inicio
						emit_status("Teste de estanqueidade| %s | timer: %02d:%02d | Checkpoint %.1f duração %s"  %(bloco, minuto, segundo, pressao_mais_baixa, time.strftime("%H:%M:%S", time.gmtime(elapsed_time))))
						tempo_verificacao_pressao = time.time() + 1
						comando_serial = "TURBINA,"+str(Config.ANALOG_VALUE)+"\n"
						ser.write(comando_serial.encode('utf-8'))
						while tempo_verificacao_pressao > time.time():
							if float(pressao) < float(pressao_mais_baixa):
								pressao_mais_baixa = float(pressao)
								breaker = True
								break
							if float(pressao_mais_baixa) <= float(Config.PRESSAO_IDEAL):
								emit_status("Verificação do {} finalizada".format(bloco))
								print("Verificação do {} finalizada".format(bloco))
								time.sleep(1)
								breaker_while = True
								breaker = True
								break
							time.sleep(.2)
				if minuto == 0 and segundo == 0:
					breaker_while = True
			final = time.time()
			duracao = final - inicio
			_dispositivo = "BLOCO ÚNICO"
			resultante ="{} {} {} P.I {} {} {} an {} sep {}\n".\
							format(time.strftime("%d/%m/%Y-%H:%M:%S"), time.strftime("%H:%M:%S", time.gmtime(duracao)),\
							bloco,  Config.PRESSAO_IDEAL, pressao_mais_baixa, round(Config.PRESSAO_IDEAL - pressao_mais_baixa),\
							str(Config.ANALOG_VALUE), getTotalSepultados())
			saveFile.historico_pressao(_dispositivo, pressao_mais_baixa)
			try:
				if telegram_bot and mosquittoServer.server_connected == "Conectado":
					telegram_bot.envia_telegram_single("856567468", resultante)
				pass
			except:
				printException()
				pass
			saveFile.resultadoTeste(resultante)
			if not aciona_valvula:
				data["situacao_teste"] = "FALHA"
				data["mensagem"] = "Teste de realizado com falha"
			else:
				data["situacao_teste"] = "SUCESSO"
				data["mensagem"] = "Teste de realizado com sucesso"
			data["duracao"] = time.strftime("%H:%M:%S", time.gmtime(duracao))
			data["pressao_ideal"] = round(Config.PRESSAO_IDEAL,2)
			data["pressao_obtida"] = round(pressao_mais_baixa,2)
			data["valor_analogo"] = Config.ANALOG_VALUE

			registrar("LEITURA_ESTANQUEIDADE", data)
			salvar_json_mauricio("LEITURA_ESTANQUEIDADE", data)
			return resultante #string
	except:
		printException()

def teste_estanqueidade():
	if sifaoCheio():
		return
	teste = Thread(target=realiza_teste_estanqueidade)
	teste.start()

def realiza_teste_estanqueidade():
	'''
	Realiza teste de estanqueidade e verifica nivel das coletoras
	'''
	try:
		if mosquitto.testeDePressao == True:
			emit_status("Já existe um teste de estanqueidade em curso")
			return
		mosquitto.bool_troca_ativada = False
		mosquitto.testeDePressao = True
		dispositivos = mosquitto.dispositivosMqtt
		resultado_teste = []
		nivel_coletoras = []
		resultado_teste.append("{\nRealizado em "+ str(time.strftime("%d/%m/%Y-%H:%M:%S"))+"\n")
		temValvula = False
		for elements in sorted(dispositivos.keys()):
			if "COLETORA" in elements:
				nivel_coletoras.append(elements+" "+dispositivos[elements]["S_NIVEL"]+"\n")
			if "VALVULA" in elements and "AM" in elements and not "BY" in elements:
				temValvula = True
				ser.write(b'BOMBA,0\n')
				infot = mosquitto.mqttc.publish("BOMBA", "BOMBA,0", qos=2)
				for comando in sorted(dispositivos[elements]):
					if "ABRE" in comando:
						try:
							cod_bloco = "BL_001"
							if "COD_BLOCO" in dispositivos[elements]:
								cod_bloco = dispositivos[elements]["COD_BLOCO"]

							cod_sub_bloco = "SUB_001"
							if "COD_SUB_BLOCO" in dispositivos[elements]:
								cod_sub_bloco = dispositivos[elements]["COD_SUB_BLOCO"]

							verifica_pressao = verifica_pressao_bloco(elements, comando, temValvula, cod_bloco, cod_sub_bloco)
							time.sleep(3)
							if mosquitto.testeDePressao == False:
								emit_status("Teste de estanqueidade cancelado")
								ser.write(b'STOP\n')
								return
							resultado_teste.append(verifica_pressao)
							print("resultado_teste", resultado_teste)
						except Exception as e:
							if telegram_bot and mosquittoServer.server_connected == "Conectado":
								try:
									telegram_bot.envia_telegram_single("334240998", e)
								except Exception as e:
									mosquitto.incluiErro(e)
							if e not in mosquitto.erro:
								mosquitto.incluiErro(e)
		if not temValvula:
			resultado_teste.append(verifica_pressao_bloco("None", "None", temValvula))# string
		saveFile.nivelColetoras("{}".format(time.strftime("%d/%m/%Y-%H:%M:%S")).join(nivel_coletoras))
		abrindo = []
		for k in sorted(devices.CONTROLADORES.keys()):
			if "VALVULA" in k or "VCAB" in k:
				if "AM" in k:
					if not mosquitto.abre_fecha_simples(k, "ABRE"):
						abrindo.append("{}\n".format(k))
		if len(abrindo) > 0:
			formatText=" Não abriu".join(abrindo)
			if telegram_bot and mosquittoServer.server_connected == "Conectado":
				telegram_bot.envia_telegram_all("** ATENÇÃO **\nAs válvulas abaixo não abriram após teste de estanqueidade:\n{}".format(formatText))
			print("corrigir tratamento da falha")
			saveFile.falhaTeste("Valvulas não abriram após teste: {}".format(formatText))
		aciona_valvula = False
		for k, v in mosquitto.dispositivosMqtt.items():
			if "VALVULA_CABINE" in k or "VCAB" in k:
				for k2, v2 in v.items():
					if "ABRE" in k2:
						aciona_valvula = mosquitto.abre_fecha_simples(k, "ABRE")  # retorna True ou False
						break
				break
		if not aciona_valvula:
			saveFile.falhaTeste("Válvula da cabine não abriu após teste de estanqueidade\n")
			if telegram_bot and mosquittoServer.server_connected == "Conectado":
				telegram_bot.envia_telegram_all("Válvula da cabine não abriu após teste de estanqueidade")
				telegram_bot.envia_telegram_pressao()
				pass
			
		emit_status("Teste de estanqueidade finalizado")
		time.sleep(3)
		if getTotalSepultados() > 0:
			ser.write(b'SCT,50\n')
		else:
			ser.write(b'STOP\n')
		mosquitto.testeDePressao = False
		emit_status("")
		enviar_pendentes()
		enviar("LEITURA_ESTANQUEIDADE")
		# if not "ETEN PARQUE DAS FLORES" in Config.CEMITERIO:
		# 	enviar("LEITURA_ESTANQUEIDADE")

	except Exception as e:
		mosquitto.testeDePressao = False
		if getTotalSepultados() > 0:
			ser.write(b'SCT,50\n')
		else:
			ser.write(b'STOP\n')
		if telegram_bot and mosquittoServer.server_connected == "Conectado":
			telegram_bot.envia_telegram_single("334240998", str(e))
		printException()

# if Config.CEMITERIO != "SANTO AMARO EMLURB":
schedule.every().day.at(HORA_TESTE_ESTANQUEIDADE_1).do(teste_estanqueidade)


def measure_temp():
		''' Retorna a temperatura da cpu'''
		temp = os.popen("vcgencmd measure_temp").readline()
		temp = temp.replace("'C","")
		return (float(temp.replace("temp=","")) - 24)


def temperatura_interna():
	conn = sqlite3.connect('/home/pi/Crabit/instance/banco/vilatec.db')
	cursor = conn.cursor()

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS temperatura_interna (
			id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
			data DATE NOT NULL,
			temp_manha NUMERIC(10,4),
			temp_tarde NUMERIC(10,4),
			temp_noite NUMERIC(10,4)
		)
		"""
	)
	conn.commit()


	check = list(cursor.execute("SELECT * FROM temperatura_interna").fetchall())
	conn.commit()

	manha = list(cursor.execute("SELECT temp_manha FROM temperatura_interna").fetchall())
	tarde = list(cursor.execute("SELECT temp_tarde FROM temperatura_interna").fetchall())
	noite = list(cursor.execute("SELECT temp_noite FROM temperatura_interna").fetchall())
	conn.commit()


	if len(check) == 0 or (manha[-1][0] and tarde[-1][0] and noite[-1][0]):
		cursor.execute("INSERT INTO temperatura_interna (data, temp_manha) VALUES (CURRENT_TIMESTAMP, ?)", (mosquitto.dispositivosMqtt["ARDUINO"]["temperatura"],))
		conn.commit()

	else:
		try:
			if tarde[-1][0]:
				logging.info("Temperatura da tarde " + str(tarde[-1][0]) + " do dia " + str(datetime.date.today()) + " ja inserido")
			else:
				cursor.execute("UPDATE temperatura_interna set temp_tarde = ?", (mosquitto.dispositivosMqtt["ARDUINO"]["temperatura"],))
				conn.commit()
				return
			if noite[-1][0]:
				logging.info("Temperatura da noite ", str(noite[-1][0]), " do dia ", str(datetime.date.today()), "ja inserido")
			else:
				cursor.execute("UPDATE temperatura_interna set temp_noite = ?", (mosquitto.dispositivosMqtt["ARDUINO"]["temperatura"],))
				conn.commit()

		except Exception as e:
			print("Erro temp interna", str(e))

		manha = list(cursor.execute("SELECT temp_manha FROM temperatura_interna").fetchall())
		tarde = list(cursor.execute("SELECT temp_tarde FROM temperatura_interna").fetchall())
		noite = list(cursor.execute("SELECT temp_noite FROM temperatura_interna").fetchall())

		data = {
				"codigo_cliente": Config.COD_CLIENTE,
				"codigo_estacao": Config.COD_ESTACAO,
				"temp_manha": manha[-1][0],
				"temp_tarde": tarde[-1][0],
				"temp_noite": noite[-1][0],
				"situacao_teste": "",
				"mensagem":""
		}

		if manha[-1][0] and tarde[-1][0] and noite[-1][0]:
			data["situacao_teste"] = "SUCESSO"

		registrar("LEITURA_TEMPERATURA_INTERNA", data)
		salvar_json_mauricio("LEITURA_TEMPERATURA_INTERNA", data)
		enviar("LEITURA_TEMPERATURA_INTERNA")

		cursor.close()
		conn.close()
	return
schedule.every().day.at("07:00").do(temperatura_interna)
schedule.every().day.at("14:35").do(temperatura_interna)
schedule.every().day.at("20:00").do(temperatura_interna)

def variacao_umidade():
	try:
		conn = sqlite3.connect('/home/pi/Crabit/instance/banco/vilatec.db')
		cursor = conn.cursor()

		cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS variacao_umidade (
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
				data DATE NOT NULL,
				var_manha NUMERIC(10,4),
				var_tarde NUMERIC(10,4),
				var_noite NUMERIC(10,4)
			)
			"""
		)
		conn.commit()


		check = list(cursor.execute("SELECT * FROM variacao_umidade").fetchall())
		conn.commit()

		manha = list(cursor.execute("SELECT var_manha FROM variacao_umidade").fetchall())
		tarde = list(cursor.execute("SELECT var_tarde FROM variacao_umidade").fetchall())
		noite = list(cursor.execute("SELECT var_noite FROM variacao_umidade").fetchall())
		conn.commit()


		if len(check) == 0 or (manha[-1][0] and tarde[-1][0] and noite[-1][0]):
			cursor.execute("INSERT INTO variacao_umidade (data, var_manha) VALUES (CURRENT_TIMESTAMP, ?)", (mosquitto.dispositivosMqtt["ARDUINO"]["umidade"],))
			conn.commit()

		else:
			try:
				if tarde[-1][0]:
					logging.info("Umidade da tarde " + str(tarde[-1][0]) + " do dia " + str(datetime.date.today()) + " ja inserido")
				else:
					cursor.execute("UPDATE variacao_umidade set var_tarde = ?", (mosquitto.dispositivosMqtt["ARDUINO"]["umidade"],))
					conn.commit()
					return
				if noite[-1][0]:
					logging.info("Umidade da noite ", noite[-1][0], " do dia ", datetime.date.today(), "ja inserido")
				else:
					cursor.execute("UPDATE variacao_umidade set var_noite = ?", (mosquitto.dispositivosMqtt["ARDUINO"]["umidade"],))
					conn.commit()

			except Exception as e:
				print("Erro unidde", str(e))

			manha = list(cursor.execute("SELECT var_manha FROM variacao_umidade").fetchall())
			tarde = list(cursor.execute("SELECT var_tarde FROM variacao_umidade").fetchall())
			noite = list(cursor.execute("SELECT var_noite FROM variacao_umidade").fetchall())

			data = {
					"codigo_cliente": Config.COD_CLIENTE,
					"codigo_estacao": Config.COD_ESTACAO,
					"var_manha": manha[-1][0],
					"var_tarde": tarde[-1][0],
					"var_noite": noite[-1][0],
					"situacao_teste": "",
					"mensagem":""
			}

			if manha[-1][0] and tarde[-1][0] and noite[-1][0]:
				data["situacao_teste"] = "SUCESSO"



			registrar("LEITURA_VARIACAO_UMIDADE", data)
			salvar_json_mauricio("LEITURA_VARIACAO_UMIDADE", data)
			enviar("LEITURA_VARIACAO_UMIDADE")

			cursor.close()
			conn.close()
		return
	except:
		printException()

schedule.every().day.at("07:00").do(variacao_umidade)
schedule.every().day.at("14:35").do(variacao_umidade)
schedule.every().day.at("20:00").do(variacao_umidade)




def grava_consumo_diario():
	conn = sqlite3.connect('/home/pi/Crabit/instance/banco/vilatec.db')
	cursor = conn.cursor()

	#checando se existem dados mais antigos que 90 dias para serem deletados
	deleta_antigos = list(cursor.execute("SELECT * FROM leitura_consumo").fetchall())
	conn.commit()

	for linha in range(len(deleta_antigos)):
		data_delete = datetime.datetime.strptime(deleta_antigos[linha][1], "%Y-%m-%d").date()
		data_hoje = datetime.datetime.now().date()

		if len(deleta_antigos) > 1 and (data_hoje - data_delete).days > 90:

			logging.info("Deletando registro antigo - id: " + str(deleta_antigos[linha][0]) + "/" + str(data_delete))

			cursor.execute("DELETE FROM leitura_consumo WHERE id = ?", (deleta_antigos[linha][0],))
			conn.commit()


	lista_leitura_acumulada = list(cursor.execute("SELECT leitura_acumulada FROM leitura_consumo").fetchall())
	conn.commit()

	lista_tarifa = list(cursor.execute("SELECT tarifa FROM leitura_consumo").fetchall())
	conn.commit()

	ultimo_registro_kwh = lista_leitura_acumulada[-1][0]
	ultima_tarifa = lista_tarifa[-1][0]
	consumo_diario = (pzem.values['consumo']/1000) - ultimo_registro_kwh
	preco = consumo_diario*ultima_tarifa

	consumo_diario = float(format(consumo_diario, ".4f"))
	preco = float(format(preco, ".4f"))


	lista_data_leitura = list(cursor.execute("SELECT * FROM leitura_consumo").fetchall())
	conn.commit()

	ultima_data_leitura = lista_data_leitura[-1][1]
	ultimo_mes_leitura = ultima_data_leitura[5] + ultima_data_leitura[6] # extrai mes considerando o formato iso 1234-56-78

	ultima_data_leitura = datetime.datetime.strptime(ultima_data_leitura, "%Y-%m-%d")
	data_leitura_atual = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")


	leitura_diaria = consumo_diario
	leitura_acumulada = leitura_diaria


	tabela_valor_inicial = list(cursor.execute("SELECT * FROM leitura_consumo WHERE id = 2").fetchall())
	conn.commit()

	# continua com a inserção apenas se não houver sido feita uma inserção no dia / mês atual
	if ultima_data_leitura.strftime("%Y%m%d") < data_leitura_atual.strftime("%Y%m%d") or tabela_valor_inicial:

		if tabela_valor_inicial:
			cursor.execute(
			"DELETE FROM leitura_consumo WHERE id = 2")
			conn.commit()

		leitura_mensal = leitura_diaria

		consumo_diario_dados = list(cursor.execute("SELECT * FROM leitura_consumo").fetchall())
		conn.commit()

		for x in range(len(consumo_diario_dados)):
			data = consumo_diario_dados[x][1]
			mes_consumo = data[5] + data[6]

			if mes_consumo == datetime.datetime.now().strftime("%m"):
				leitura_mensal += consumo_diario_dados[x][5]


		leitura_acumulada = pzem.values['consumo']/1000


		cursor.execute(""" INSERT INTO leitura_consumo (data, tarifa, valor, leitura_acumulada, leitura_dia, leitura_mes)
		VALUES (?, ?, ?, ?, ?, ?)
		""", (datetime.datetime.now().strftime("%Y-%m-%d"), ultima_tarifa, preco, leitura_acumulada, leitura_diaria, leitura_mensal))

		conn.commit()
		logging.info(
			"Leitura atualizada:\n"+
			'Data' " : " + str(datetime.datetime.now().strftime("%Y-%m-%d")) + ",\n"
			'Ultima tarifa' " : " + str(ultima_tarifa)+ ",\n"
			'Valor' " : " + str(preco)+ ",\n"
			'Leitura acumulada' " : " + str(leitura_acumulada)+ ",\n"
			'Leitura diaria' " : " + str(leitura_diaria)+ ",\n"
			'Leitura mensal' " : " + str(leitura_mensal)
		)

		leitura_consumo()

	else:
		logging.info("Leitura do dia " + str(datetime.datetime.now().strftime("%Y-%m-%d")) + " já realizada!")
		return

	conn.commit()
	cursor.close()
	conn.close()

schedule.every().day.at("00:05").do(grava_consumo_diario) # Rotina para gravar o consumo elétrico
#schedule.every().hour.do(grava_consumo_diario) # Rotina para gravar o consumo elétrico

def leitura_consumo():
	conn = sqlite3.connect('/home/pi/Crabit/instance/banco/vilatec.db')
	cursor = conn.cursor()
	lista_consumo = list(cursor.execute("SELECT * FROM leitura_consumo").fetchall())
	conn.commit()
	data_leitura = lista_consumo[-1][1]
	consumo = lista_consumo[-1][5]
	valor_consumo = lista_consumo[-1][3]


	data = {
			"codigo_cliente": Config.COD_CLIENTE,
			"codigo_estacao": Config.COD_ESTACAO,
			"data_leitura": data_leitura,
			"consumo_eletrico": consumo,
			"valor_consumo": valor_consumo,
			"situacao_teste": "",
			"mensagem":""
	}

	if consumo > 0 and valor_consumo > 0:
		data["situacao_teste"] = 'SUCESSO'

	cursor.close()
	conn.close()

	try:
		registrar("LEITURA_CONSUMO_ELETRICO", data)
		salvar_json_mauricio("LEITURA_CONSUMO_ELETRICO", data)
		enviar("LEITURA_CONSUMO_ELETRICO")
	except Exception as e:
		print("Erro cons. eletrico", str(e))

# if getTotalSepultados() < 16:
# 	if not "CORTEL" in Config.CEMITERIO:
# 		if not "BARBARA" in Config.CEMITERIO:
# 			Config.PRESSAO_SCT = 50 + (getTotalSepultados() * 10)

# 		if "IGUATU" in Config.CEMITERIO:
# 			Config.PRESSAO_SCT = 50 + (getTotalSepultados() * 10)

mosquittoServer.realiza_teste_estanqueidade = teste_estanqueidade
ser = None
ser2 = None
lista_porta=[]
portas_abertas=[]
ports = serial.tools.list_ports.comports()
for port, desc, hwid in sorted(ports):
		if "USB" in port:
			lista_porta.append(port)

for portas in lista_porta:
	'''
	Abre todas as portas
	'''
	try:
		portas_abertas.append(serial.Serial(portas, 9600, timeout=0))
	except:
		print(portas, "Acesso negado")
inicio = time.time()
try:
	while ser == None and time.time() - inicio < 20:
		for channel in portas_abertas:
			if ser == None:
				string = channel.readline().decode("utf-8", "ignore")

				if "<" in string or ">" in string:
					print("Porta nano", lista_porta[portas_abertas.index(channel)])
					print(pzem)
					print(lista_porta)
					ser=channel
					if len(lista_porta) > 1:
						lista_porta.remove(lista_porta[portas_abertas.index(channel)])
						porta_pzem004 = lista_porta[0]
						pzem.serial_port(porta_pzem004)
					else:
						print("Pzem nao detectado")
					break

	if time.time() - inicio < 19:
		ser.write(b'STOP\n')
		if getTotalSepultados() > 0:
			ser.write(b'TURBINA,50\n')
	if ser is not None:
		mosquitto.serial_port = ser
		mosquittoServer.serial_port_server = ser


except Exception as e:
	print(e)
	print("Porta Serial não aberta")
	if telegram_bot is not None:
		telegram_bot.envia_telegram_all( "Porta serial não detectada!")

def find_between_r( s, first, last ):
	try:
		start = s.rindex( first ) + len( first )
		end = s.rindex( last, start )
		return s[start:end]
	except ValueError:
		return ""

def is_x11():
    try:
        session_type = os.environ.get("XDG_SESSION_TYPE")
        if not session_type:
            # tenta descobrir via loginctl (caso esteja em script headless)
            output = subprocess.check_output(["loginctl", "show-session", os.environ["XDG_SESSION_ID"], "-p", "Type"])
            session_type = output.decode().strip().split('=')[-1]
        return session_type.lower() == "x11"
    except Exception as e:
        print("Não foi possível determinar o servidor gráfico:", e)
        return False

def liga_tela():
	if is_x11():
		print("Ambiente X11 detectado, executando xset...")
		os.system("DISPLAY=:0 xset force on")
	else:
		os.system("wlr-randr --output DP-1 --on")
		print("Ambiente da tela não é x11")



import requests
# def envia_ngrok(dados):
# 	try:
# 		if Config.COD_CLIENTE == "ARN_001":
# 			url = "https://webhook.vps.evo-eden.site/webhook/184468ca-3d2f-421f-9493-fb835259ac0b"
# 			#url = "https://fd66-170-79-168-234.ngrok-free.app/webhook/489f0030-a167-4083-955f-93cf192b6ca2"
# 			resposta = requests.post(url, json=dados)
# 			print("Sincronismo ngrok:", resposta)
# 	except:
# 		printException()



# Salvar JSON no banco
def salvar_json_mauricio(evento, dados):
	with app.app_context():
		registro = Registro(dados=json.dumps({evento: dados}))
		db.session.add(registro)
		db.session.commit()

# Enviar JSONs pendentes ao webhook
def enviar_pendentes():
	try:
		# if Config.COD_CLIENTE == "ARN_001":
			with app.app_context():
				registros = Registro.query.filter_by(enviado=False).all()
				for registro in registros:
					dados = json.loads(registro.dados)
					url = "https://webhook.vps.evo-eden.site/webhook/184468ca-3d2f-421f-9493-fb835259ac0b"  # Ajuste conforme necessário
					resposta = requests.post(url, json=dados, timeout=10)
					
					if resposta.status_code == 200:  # Confirmação de envio
						db.session.delete(registro)
				
				db.session.commit()
	except:
		print('Falha ao enviar dados ao webkook')
		printException()



