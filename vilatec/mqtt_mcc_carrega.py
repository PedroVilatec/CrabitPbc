# -*- coding: utf-8 -*-
import linecache
import sys, os, repackage
import names
repackage.up()
from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork
from PyQt5.QtWidgets import QApplication, QStyle
from PyQt5.QtGui import QIcon
import PyQt5
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.Qt import *
import datetime
import time
from instance.devices import Devices
from operations import dict_disp
from instance.config import Config
import json
import paho.mqtt.client as mqtt
import threading
global serial_data
import datetime
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
_excepthook = sys.excepthook
sys.stdout.write("\x1b]2;%s\x07" % 'MQTT')
def exception_hook(exctype, value, traceback):
	 _excepthook(exctype, value, traceback)
	 sys.exit(1)
sys.excepthook = exception_hook

def printException():
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


def update_code():
	pattern = "*.py"
	lista_de_arquivos = []
	for path, subdirs, files in os.walk(ROOT_DIR):
		for name in files:
			if fnmatch(name, pattern):
				if not ".git" in path:
					full_path = os.path.join(path, name)
					cmd_turned = os.popen("date -r " + full_path).read().rstrip()
					lista_de_arquivos.append ([full_path, cmd_turned])
thread = threading.Thread(target=update_code)
thread.start()

class MyApp(QWidget):
	def __init__(self):
		super(MyApp, self).__init__()
		self.desktop = QApplication.desktop()
		self.screenRect = self.desktop.screenGeometry()
		self.height = self.screenRect.height()
		self.width = self.screenRect.width()
		sys._excepthook = sys.excepthook
        self.Devices = Devices(**dict_disp.dispositivos)
		self.btn = []
		self.altura_qlineedit = 15
		self.newCampo = None
		self.setContentsMargins(0,0,0,0)
		self.indice_qlineedit = []
		self.setGeometry(0, 50, 280, 350)
		self.buttons = []
		self.online = {}
		self.counter = 0
		self.comando_valvulas = ["ALL", "AM", "AZ"]
		self.index_comando_valvulas = 0
		self.memory_qcombo = []
		self.qcomboEncontrado = False
		self.counter_change_ico = 0 #utilizada para postergar o tempo de operações
		self.initUI()

	def contextMenuEvent(self, event):
		try:
			contextMenu = QMenu(self)
			action = None
			for k in self.dispositivosMqtt.keys():
				if self.qcombo.currentText().split("?")[0].rstrip() == k:
					for k2, v2 in self.dispositivosMqtt[k].items():
						exclude = ["COD_BLOCO", "COD_SUB_BLOCO", "S_", "S ", "NOME", "VERSAO"]
						if not any(string in k2 for string in exclude):
							item = contextMenu.addAction(k2)
					item = contextMenu.addAction("Update")
					# sub = QMenu(item)
					# sub.setTitle('Ip')
					# sub.addAction(ActionFont(self, "IP"))
					# sub.addAction(ActionFont(self, "HostName"))
					item = contextMenu.addAction("readMsg")
					break
			action = contextMenu.exec_(self.mapToGlobal(event.pos()))
			if action:
				dispositivo = self.qcombo.currentText().split("?")[0].rstrip()
				if action.text() == "Update":
					url = ""
					for k, v in self.dispositivosMqtt[dispositivo].items():
						if "IP" in k:
							print("IP", v)
							url = "http://{}/update".format(v)
							break
					if url == "":
						url = "http://{}.local/update".format(dispositivo.lower())
					self.w = UpdateWidget(url)
					self.w.show()
				elif action.text() == "readMsg":
					url = ""
					for k, v in self.dispositivosMqtt[dispositivo].items():
						if "IP" in k:
							print("IP", v)
							url = "http://{}/readMsg".format(v)
							break
					if url == "":
						url = "http://{}.local/readMsg".format(dispositivo.lower())
					req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
					self.nam = QtNetwork.QNetworkAccessManager()
					self.nam.finished.connect(self.handleResponse)
					self.nam.get(req)
				else:
					topico = dispositivo
					payload = action.text()
					print("Topico = ", topico, "Payload = ", payload)
					infot = self.mqttc.publish(topico, payload, qos=0)
		except:
			printException()

	@QtCore.pyqtSlot(QtNetwork.QNetworkReply)
	def handleResponse(self, reply):
		if reply.error() == QtNetwork.QNetworkReply.NoError:
			QtWidgets.QMessageBox.information(self, "ReadMsg",str(reply.readAll().data(), 'utf-8'))
		else:
			errorMessage = "Erro ocorrido: {}".format(reply.errorString())
			QtWidgets.QMessageBox.critical(self, "Erro", errorMessage)
		reply.deleteLater()

	def acrescenta_group_mqtt(self, device, Label, value): # device = json retornado pelo dispositivo
		try:
			label = QLabel(Label.replace("STATUS","S"))
			label.setAlignment(Qt.AlignLeft)
			#~ label.setStyleSheet('QLabel {color: red;}')
			label.setFont(PyQt5.QtGui.QFont('Piboto Condensed', 7))
			a = QLineEdit()
			a.setFixedHeight(self.altura_qlineedit)
			a.setFont(PyQt5.QtGui.QFont('Piboto Condensed', 7))
			a.setAlignment(Qt.AlignRight)
			a.setText(str(value))
			a.setReadOnly(False)
			name = device+ "/"+Label
			self.indice_qlineedit.append(name)# iteração para poder atualizar a label específica pela ordem de criação
			a.setObjectName(name)
			data_btn = [a,False]
			self.btn.append(data_btn)
			groupBox = self.findChild(QtWidgets.QGroupBox, device)
			qform = self.findChild(QtWidgets.QFormLayout, device)
			if qform:
				self.findChild(QtWidgets.QFormLayout, device).addRow(label, a)
			else:
				layout_groupbox = QFormLayout(groupBox)
				layout_groupbox.setObjectName(device)
				layout_groupbox.addRow(label, a)


		except:
			printException()
		self.newCampo = None
	def mouseDoubleClickEvent(self, event):
		print("BUSCANDO IP")
		try:
			mac = None
			instance = None
			instance = self.findChild(QtWidgets.QLineEdit, self.qcombo.currentText()+"/STATUS_MAC")

			if instance:
				mac = instance.text()
				cmd = '''sudo nmap -sP 192.168.0.0/24 | awk '/Nmap scan report for/{printf $5;}/MAC Address:/{print " "$3;}' | sort | grep '''+mac
				store = os.popen(cmd)
				ip = store.read()
				if len(ip)  > 10:
					ip = ip.split()[0]
					cmd_2 = "curl -sb -H {}/mqtt?server={}'&'port={}".format(ip, os.uname()[1], Config.PORTA_MQTT_LOCAL)
					result = os.popen(cmd_2)
					print(result.read())
			else:
				instance =  self.findChild(QtWidgets.QLineEdit, self.qcombo.currentText()+"/S_MAC")
				if instance:
					mac = instance.text()
					cmd = '''sudo nmap -sP 192.168.0.0/24 | awk '/Nmap scan report for/{printf $5;}/MAC Address:/{print " "$3;}' | sort | grep '''+mac
					store = os.popen(cmd)
					ip = store.read()
					if len(ip ) > 10:
						ip = ip.split()[0]
						cmd_2 = "curl -sb -H {}/mqtt?server={}'&'port={}".format(ip, os.uname()[1], Config.PORTA_MQTT_LOCAL)
						result = os.popen(cmd_2)
						print(result.read())
			if mac is None:
				print("MAC NÃO ENCONTRADO")
		except:
			printException()

	def createLayout_group_mqtt(self, device): # device = json retornado pelo dispositivo
		try:
			existe = False
			join = ""
			if device["DISPOSITIVO"] in self.Devices.CONTROLADORES.keys():
				existe = True
				join = ""
			else:
				join = " ?"
			device["DISPOSITIVO"] = device["DISPOSITIVO"] + join
			AllItems = [self.qcombo.itemText(i) for i in range(self.qcombo.count())]
			if device["DISPOSITIVO"] not in AllItems:
				self.qcombo.addItem(self.style().standardIcon(getattr(QStyle, 'SP_TitleBarCloseButton')), device["DISPOSITIVO"])

			self.groupBox = QtWidgets.QGroupBox("{}".format(device["DISPOSITIVO"]), self.scrollAreaWidgetContents)
			sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
			sizePolicy.setHorizontalStretch(0)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
			self.groupBox.setSizePolicy(sizePolicy)
			self.groupBox.setObjectName("groupBox")


			self.groupBox.setContentsMargins(1,1,1,1)
			#~ self.groupBox.setCheckable(True)
			self.groupBox.setFont(PyQt5.QtGui.QFont('Piboto Condensed', 7))
			self.groupBox.setObjectName(device["DISPOSITIVO"])
			layout_groupbox = QFormLayout(self.groupBox)
			layout_groupbox.setObjectName(device["DISPOSITIVO"])
			self.groupBox.setStyleSheet("QGroupBox { background-color: rgb(51, 212,\
					194);  solid rgb(0, 0, 0); }")
			if self.counter > 0:
				self.groupBox.hide()
			else:
				index = self.qcombo.findText(device["DISPOSITIVO"], QtCore.Qt.MatchFixedString)
				if index >= 0:
					 self.qcombo.setCurrentIndex(index)
			self.counter = 1

			self.buttons = []
			if not "ARDUINO" in device["DISPOSITIVO"]:
				for a, b in device["STATUS"].items():
					include = ["S_", "S "]
					if any(string in a for string in include):
						c = a
						try:
							label = QLabel(a.replace("STATUS","S"))
							label.setAlignment(Qt.AlignLeft)
							#~ label.setStyleSheet('QLabel {color: red;}')
							label.setFont(PyQt5.QtGui.QFont('Piboto Condensed', 7))
							a = QLineEdit()
							a.setFixedHeight(self.altura_qlineedit)
							a.setFont(PyQt5.QtGui.QFont('Piboto Condensed', 7))
							a.setAlignment(Qt.AlignRight)
							a.setText(str(b))
							a.setReadOnly(False)
							name = device["DISPOSITIVO"].split("?")[0].rstrip()+ "/"+c
							self.indice_qlineedit.append(name)# iteração para poder atualizar a label específica pela ordem de criação
							a.setObjectName(name)
							data_btn = [a,False]
							self.btn.append(data_btn)
							layout_groupbox.addRow(label, a)
						except Exception as e:
							printException()
					encontrado = False
			try:
				if device["DISPOSITIVO"] in self.Devices.CONTROLADORES.keys():
					for k2, v2 in self.Devices.CONTROLADORES[device["DISPOSITIVO"]].items():
						exclude = ["COD_BLOCO", "COD_SUB_BLOCO", "S_", "S "]
						if not any(string in k2 for string in exclude):

							if device == "COMANDOS":
								button = QPushButton(k2)
								#~ button.setFont(PyQt5.QtGui.QFont('SansSerif', 7))
								command = device["DISPOSITIVO"].split("?")[0].rstrip()+"/"+k2
								button.clicked.connect(lambda checked, text= command: self.on_button_comando(text))
								self.buttons.append(button)
							if "ENVIAR SERIAL" in k2 or "NOME" in k2 or "BOMBA" in k2:
								label = QLabel(k2)
								label.setAlignment(Qt.AlignLeft)
								label.setFont(PyQt5.QtGui.QFont('Piboto Condensed', 7))
								command = device["DISPOSITIVO"].split("?")[0].rstrip()+"/"+k2
								self.inData = QLineEdit(k2)
								self.inData.setFixedHeight(self.altura_qlineedit)
								self.inData.setFont(PyQt5.QtGui.QFont('Piboto Condensed', 7))
								self.inData.returnPressed.connect(self.qlineEdit)
								self.inData.setObjectName(command)
								layout_groupbox.addRow(label, self.inData)
				else:
					cmd = None
					if "NIVEL" in  device["DISPOSITIVO"]:
						cmd = dict_disp.dispositivos['nivel_tanque']
					elif "VCAB" in  device["DISPOSITIVO"]:
						cmd = dict_disp.dispositivos['valvula_cabine']
					elif "VSIMP" in device["DISPOSITIVO"]:
						cmd = dict_disp.dispositivos['valvula_simples']
					elif "VALVULA" in device["DISPOSITIVO"]:
						cmd = dict_disp.dispositivos['valvula_simples']
					elif "EVAP" in device["DISPOSITIVO"]:
						cmd = dict_disp.dispositivos['evaporadora']
					elif "COLETORA" in device["DISPOSITIVO"]:
						cmd = dict_disp.dispositivos['coletora']
					elif "BOMBA" in device["DISPOSITIVO"]:
						cmd = dict_disp.dispositivos['bomba']
					if cmd:
						try:
							self.dispositivosMqtt[device["DISPOSITIVO"].split("?")[0].rstrip()].update(cmd)
						except:
							print("EXCEPT MQTT CREATE")
						for k2, v2 in self.dispositivosMqtt[device["DISPOSITIVO"].split("?")[0].rstrip()].items():
							exclude = ["COD_BLOCO", "COD_SUB_BLOCO", "S_", "S "]
							if not any(string in k2 for string in exclude):

								if device == "COMANDOS":
									button = QPushButton(k2)
									#~ button.setFont(PyQt5.QtGui.QFont('SansSerif', 7))
									command = device["DISPOSITIVO"].split("?")[0].rstrip()+"/"+k2
									button.clicked.connect(lambda checked, text= command: self.on_button_comando(text))
									self.buttons.append(button)
								if "ENVIAR SERIAL" in k2 or "NOME" in k2 or "BOMBA" in k2:
									label = QLabel(k2)
									label.setAlignment(Qt.AlignLeft)
									#~ label.setStyleSheet('QLabel {color: red;}')
									label.setFont(PyQt5.QtGui.QFont('Piboto Condensed', 7))
									command = device["DISPOSITIVO"].split("?")[0].rstrip()+"/"+k2
									#~ button.clicked.connect(lambda checked, text= command: self.on_button(text))

									self.inData = QLineEdit(k2)
									self.inData.setFixedHeight(self.altura_qlineedit)
									self.inData.setFont(PyQt5.QtGui.QFont('Piboto Condensed', 7))
									self.inData.returnPressed.connect(self.qlineEdit)
									self.inData.setObjectName(command)
									#~ layout_groupbox.addWidget(button)
									layout_groupbox.addRow(label, self.inData)
					else:
						label = QLabel("NOME")
						label.setAlignment(Qt.AlignLeft)
						#~ label.setStyleSheet('QLabel {color: red;}')
						label.setFont(PyQt5.QtGui.QFont('Piboto Condensed', 7))
						#~ button.clicked.connect(lambda checked, text= command: self.on_button(text))
						command = device["DISPOSITIVO"].split("?")[0].rstrip()+"/"+"NOME"
						self.inData = QLineEdit()
						self.inData.setFixedHeight(self.altura_qlineedit)
						self.inData.setFont(PyQt5.QtGui.QFont('Piboto Condensed', 7))
						self.inData.returnPressed.connect(self.qlineEdit)

						self.inData.setObjectName(command)
						layout_groupbox.addRow(label, self.inData)

			except Exception as e:
				printException()


			return self.groupBox
		except Exception as e:
			printException()
	def generate_context_menu(self, location):
		print(location)
		print(self.sender()*100)
		#~ menu = self.my_textbox.createStandardContextMenu()
		#~ # add extra items to the menu

		#~ # show the menu
		#~ menu.popup(self.mapToGlobal(location))
	def qlineEdit(self):
		topico, payload = self.sender().objectName().split("/")
		topico = topico.split("?")[0].rstrip()

		if "ENVIAR SERIAL" in payload:
			payload = payload +"/"+ self.sender().text()+"\n"
		if "NOME" in payload:
			payload = payload +","+ self.sender().text()

		if "BOMBA" in payload:
			payload = payload +","+ self.sender().text()
		print("Topico = ", topico, "Payload = ", payload)

		infot = self.mqttc.publish(topico, payload, qos=0)

	def loop_mqtt(self):
		self.mqttc.loop_forever()

	def on_combobox_changed(self, value):
		...
		#~ print("combobox changed")


	def filter_combo_box_key_pressed(self, event):
		text = self.label_search.text()
		if event.key() == Qt.Key_F1:
			self.index_comando_valvulas += 1
			if self.index_comando_valvulas > 2:
				self.index_comando_valvulas = 0
			print("VALVULAS SELECIONADAS", self.comando_valvulas[self.index_comando_valvulas])

		elif event.key() == Qt.Key_Escape:
				self.label_search.hide()
				self.label_search.setText("")

		elif event.key() == Qt.Key_F2:
			if self.qcombo.count() != len(self.memory_qcombo):
				self.qcombo.clear()
				self.qcombo.addItems(self.memory_qcombo)
				self.label_search.setText("")
				self.label_search.hide()
				text = ""

		elif event.key() == 16777219:
			text = text[:-1]
			self.label_search.setText(text)

		else:
			self.label_search.show()
			try:
				text = text+chr(event.key())
				self.label_search.setText(text)
			except:
				...
		if text != "":
			self.qcombo.clear()
			for a in self.memory_qcombo:
				if text in a:
					self.qcombo.addItem(a)



	def keyPressEvent(self, e):
		print("event", e.key(), Qt.Key_F)
		if e.key() == Qt.Key_F1:
			self.index_comando_valvulas += 1
			if self.index_comando_valvulas > 2:
				self.index_comando_valvulas = 0
			print("VALVULAS SELECIONADAS", self.comando_valvulas[self.index_comando_valvulas])

		if e.key()  == Qt.Key_F:
			self.abre_fecha_todas("FECHA", self.comando_valvulas[self.index_comando_valvulas])
		if e.key()  == Qt.Key_A:
			self.abre_fecha_todas("ABRE", self.comando_valvulas[self.index_comando_valvulas])

		elif e.key() == Qt.Key_F2:
			if self.qcombo.count() != len(self.memory_qcombo):
				self.qcombo.clear()
				self.qcombo.addItems(self.memory_qcombo)
				self.label_search.setText("")
				self.label_search.hide()



	def cmbChanged(self,index):
		try:
			AllItems = [self.qcombo.itemText(i) for i in range(self.qcombo.count())]
			for a in sorted(AllItems):

				if a == self.qcombo.currentText():
					for children in self.findChildren(QtWidgets.QWidget):
						if isinstance(children, QtWidgets.QGroupBox):
							children.hide()
					self.view = self.findChild(QtWidgets.QGroupBox, self.qcombo.currentText())
					self.view.show()
		except:
			pass

	def on_button_comando(self, n):
		topico = str(n.split("/")[0])
		payload = str(n.split("/")[1])
		for children in self.findChildren(QtWidgets.QWidget):
			if isinstance(children, QtWidgets.QLineEdit):
				if children.objectName() == n:
					print(children.text())
					# ~ self.abre_fecha_todas(payload.split())

	def abre_fecha_todas(self, acao, cor):#(ABRE OU FECHA, ABERTA OU FECHADA)
		print("ABRE FECHA")
		'''
		abre todas as válvulas menos da cabine
		'''
		tempo_passado=time.time()
		antes = ""
		status_key = ""
		antes = ""
		comando = ""
		meta = ""
		break_while = False
		if acao == "ABRE":
			meta = "ABERTA"

		if acao == "FECHA":
			meta = "FECHADA"
		_dispositivosMqtt = self.dispositivosMqtt
		erro = []
		try:
			for k, v in sorted(_dispositivosMqtt.items()):
				if cor == "ALL":
					cor = "A"
				if "VALVULA" in k and cor in k:
					dispositivo = k
					status_key = ""
					for k2, v2 in sorted(v.items()):
						try:
							if acao in k2:
								if True: #_dispositivosMqtt[k]["S_CONEXAO"] == "ONLINE":
									comando = k2
									for k2, v2 in sorted(v.items()):
										if "STATUS_VALVULA" in k2 and not "FUNCIONAMENTO" in k2:
											antes = self.dispositivosMqtt[dispositivo][k2]
											status_key = k2
											break

									tentativas = 1
									tempoLimite = time.time()+ 60
									if antes != meta:
										self.mqttc.publish(dispositivo, comando, qos=2)
										print("Enviando comando para válvula {} tentativa {}".format(k, tentativas))
										#~ if meta == "ABERTA":
											#~ print("Abrindo a válvula {}".format(k))
										#~ else:
											#~ print("Fechando a válvula {}".format(k))
										tempo_passado = time.time() + 10

										break_while = False
										while tempoLimite > time.time() and not break_while:
											if self.online[k] +10  > time.time():
												if tempo_passado < time.time():
													tentativas = tentativas+1
													tempo_passado = time.time() + 10
													self.mqttc.publish(dispositivo, comando, qos=2)
													print("Reenviando comando para válvula {}, tentativa {}".format(k, tentativas))
											else:
												print("Válvula {} offline".format(k))
												break
											if self.dispositivosMqtt[dispositivo][status_key] == meta:
												print("Válvula {} {}".format(k, meta.lower()))
												time.sleep(1)
												break_while = True
												break
											time.sleep(.2)
										if self.dispositivosMqtt[dispositivo][status_key] == antes:
											print("Válvula {} não {}\n".format(k, meta.lower()))
								else:
									print("{} offline".format(k))
									time.sleep(5)
						except Exception as e:
							printException()
		except Exception as e:
			printException()
		print(erro)
		print("FIM DO COMANDO ABRE_FECHA_TODAS")

	def on_button(self, n):

		topico, payload = str(n.split("/")[0]), str(n.split("/")[1])
		if "ENVIAR SERIAL" in n:
			for children in self.findChildren(QtWidgets.QWidget):
				if isinstance(children, QtWidgets.QLineEdit):
					if children.objectName() == n:
						# ~ print(children.text(), n)
						payload = payload +"/"+ children.text()+"\n"
		if "NOME" in n:
			for children in self.findChildren(QtWidgets.QWidget):
				if isinstance(children, QtWidgets.QLineEdit):
					if children.objectName() == n:
						# ~ print(children.text(), n)
						payload = payload +","+ children.text()

		if "BOMBA" in n:
			for children in self.findChildren(QtWidgets.QWidget):
				if isinstance(children, QtWidgets.QLineEdit):
					# ~ print(children.objectName())
					if children.objectName() == n:
						# ~ print(children.text(), n, "pedro")
						payload = payload +","+ children.text()
		print("Topico = ", topico, "Payload = ", payload)

		infot = self.mqttc.publish(topico, payload, qos=0)




	def devices_connected(mosq, obj, msg):
		# This callback will only be called for messages with topics that match
		# $SYS/broker/bytes/#
		print("BYTES: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))



	def on_message(self, mosq, obj, msg):
		# This callback will only be called for messages with topics that match
		# $SYS/broker/messages/#
		#~ print("EVAPORADOR: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
		try:
				turned = msg.payload.decode()
				#~ print(turned)
				#~ print()
		except:
			return

		try:
			data = dict(json.loads(turned))
			#~ print(data)
			data["DISPOSITIVO"] = data["DISPOSITIVO"].rstrip()
			dispositivo = data["DISPOSITIVO"]
			statusDict = data["STATUS"]
			self.online.update({dispositivo:time.time()})
			self.lastState.update({dispositivo:"ONLINE"})
			try:

				self.dispositivosMqtt[dispositivo].update(statusDict)

			except:
				self.dispositivosMqtt[dispositivo]=statusDict
				pass


			exist = False
			#~ for i in range(self.qcombo.count())]
				#~ self.qcombo.itemText(i)
			if dispositivo not in self.memory_qcombo:
				print(dispositivo)
				self.memory_qcombo.append(dispositivo)
				if self.newDevice == None:
					self.newDevice = data
					return
			else:
				try:
					# if self.newDevice == None:# and dispositivo ==
						if dispositivo == self.qcombo.currentText().split("?")[0].rstrip():
							if self.checkBox.isChecked():
								print(json.dumps(data["STATUS"], indent=4, sort_keys=True))
						versao = False
						for k, v in data["STATUS"].items():
							if "VERSAO" in k and "VALVULA" in dispositivo:
								versao = True


							nameLabel = dispositivo + "/" +k # retorna o nome das qlinedit
							encontrado = False
							for i in range(len(self.indice_qlineedit)):
								if self.indice_qlineedit[i] == nameLabel:
									self.btn[i][0].setText(str(v))
									encontrado = True
									break

							if not encontrado:
								self.newCampo = [dispositivo, k, v]
								#~ print(k, v)
						if not versao and "VALVULA" in dispositivo:
							print(dispositivo, "Desatualizado")
						if self.findChild(QtWidgets.QGroupBox, dispositivo):
							self.findChild(QtWidgets.QGroupBox, dispositivo).setTitle(dispositivo +" - "+ str(time.strftime("%H:%M:%S")))
						elif self.findChild(QtWidgets.QGroupBox, dispositivo +" ?"):
							self.findChild(QtWidgets.QGroupBox, dispositivo +" ?").setTitle(dispositivo +" - "+ str(time.strftime("%H:%M:%S")))
							#~ print(dispositivo)
				except:
					printException()


			msgFromMcc = msg.topic.split("\\")[0]
		except:
			...
			#~ printException()


	def on_connect(self, mqttc, obj, flags, rc):
		self.mqttc.subscribe("#", 0)
		print("Conectado rc: " + str(rc))

	def on_disconnect(self, client, userdata,  rc):
		print("Mqtt desconectado")


	def on_message_msgs(mqttc, obj, msg):
		#print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
		print(msg.topic + str(msg.payload.decode()))


	def on_publish(self, mqttc, obj, mid):
		print("mid: " + str(mid))


	def on_subscribe(self, mqttc, obj, mid, granted_qos):
		print("Subscribed: " + str(mid) + " " + str(granted_qos))


	def on_log(self, mqttc, obj, level, string):
		print(string)

	''' FIM DAS FUNÇÕES DO MQTT'''

	def recurring_timer(self):
		DISPOSITIVOS_MQTT = self.dispositivosMqtt
		try:
			if self.newCampo is not None:
				self.acrescenta_group_mqtt(self.newCampo[0], self.newCampo[1], self.newCampo[2])
			if self.newDevice is not None:
				self.gridLayout_2.addWidget(self.createLayout_group_mqtt(self.newDevice))
				self.newDevice = None
			disp_online = 0
			AllItems = [self.qcombo.itemText(i) for i in range(self.qcombo.count())]
			for a in AllItems:
				try:
					a = a.split(" ?")[0].rstrip()
				except:
					...
					pass
				if self.online[a] + 20  > time.time():
					disp_online += 1
					for index in range(self.qcombo.count()):
						if a == self.qcombo.itemText(index).split(" ?")[0].rstrip():

							if "COLETORA" in a:
								for k, v in DISPOSITIVOS_MQTT[a].items():
									if "STATUS_NIVEL" in k:
										if v == "CHEIO":
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_DialogNoButton')))
										if v == "VAZIO":
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_DialogYesButton')))
										if v == "MEIO":
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_FileDialogInfoView')))
										break
							elif "EVAP" in a  and not "CABINE" in a:
								for k, v in DISPOSITIVOS_MQTT[a].items():
									if "S_COL" in k or "S_EVAP" in k:
										if v == "CHEIO":
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxWarning')))
											break
									if "S_VAL" in k:
										if v == "ABERTA":
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_DialogYesButton')))

										elif v == "FECHADA":
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_DialogNoButton')))

										elif v == "ENTREABERTA":
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_FileDialogInfoView')))
										elif "ERRO" in v:
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxWarning')))
										break
									if "S_NIVEL" in k:
										if v == "CHEIO":
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxWarning')))
										elif v == "VAZIO":
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_DialogYesButton')))
										elif v == "MEIO":
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_FileDialogInfoView')))
											break

							elif "VALVULA" in a:
								for k, v in DISPOSITIVOS_MQTT[a].items():
									if "STATUS" in k and  "VALVULA" in k and not "FUNCIONAMENTO" in k:
										if v == "ABERTA":
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_DialogYesButton')))

										elif v == "FECHADA":
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_DialogNoButton')))

										elif v == "ENTREABERTA":
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_FileDialogInfoView')))
										elif "ERRO" in v :
											self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxWarning')))
										break
							else:
								self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_DialogApplyButton')))
								break
							print(self.lastState[a])
							if self.lastState[a] == "OFFLINE":
								self.lastState[a] = "ONLINE"

				else:
					if self.lastState[a] == "ONLINE":
						print(a, "offline")
						self.lastState[a] = "OFFLINE"
					for index in range(self.qcombo.count()):
						if a in self.qcombo.itemText(index):
							self.qcombo.setItemIcon(index, self.style().standardIcon(getattr(QStyle, 'SP_TitleBarCloseButton')))
							break
			total = str(len(self.Devices.CONTROLADORES.keys()))
			self.setWindowTitle(str(total)+"/"+str(disp_online))
		except Exception as e:
			printException()
			pass

	def initUI(self):
		self.setContentsMargins(1,1,1,1)
		self.label_search = QLabel(self)
		self.label_search.setContentsMargins(1,1,1,1)
		self.label_search.hide()
		# self.qcombo = QComboBox(self)
##########################################################################################################
		self.verticalLayout_2 = QtWidgets.QVBoxLayout(self)
		self.verticalLayout_2.setObjectName("verticalLayout_2")
		self.verticalLayout_2.setContentsMargins(1, 1, 1, 1)
		self.horizontalLayout = QtWidgets.QHBoxLayout()
		self.horizontalLayout.setObjectName("horizontalLayout")
		self.horizontalLayout.setContentsMargins(1,1,1,1)
		self.qcombo = QtWidgets.QComboBox(self)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.qcombo.sizePolicy().hasHeightForWidth())
		self.qcombo.setSizePolicy(sizePolicy)
		self.qcombo.setObjectName("comboBox")
		self.qcombo.setContentsMargins(1,1,1,1)
		self.horizontalLayout.addWidget(self.qcombo)
		self.checkBox = QtWidgets.QCheckBox(self)

		self.checkBox.setContentsMargins(1,1,1,1)
		self.checkBox.setText("")
		self.checkBox.setObjectName("checkBox")
		self.horizontalLayout.addWidget(self.checkBox)
		self.verticalLayout_2.addLayout(self.horizontalLayout)
		self.scrollArea = QtWidgets.QScrollArea(self)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
		self.scrollArea.setSizePolicy(sizePolicy)
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setObjectName("scrollArea")
		self.scrollArea.setContentsMargins(1,1,1,1)
		self.scrollAreaWidgetContents = QtWidgets.QWidget()
		self.scrollAreaWidgetContents.setContentsMargins(1,1,1,1)
		self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 350, 350))
		self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
		self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
		self.gridLayout_2.setContentsMargins(1,1,1,1)
		self.gridLayout_2.setObjectName("gridLayout_2")
		# self.groupBox = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
		# sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		# sizePolicy.setHorizontalStretch(0)
		# sizePolicy.setVerticalStretch(0)
		# sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
		# self.groupBox.setSizePolicy(sizePolicy)
		# self.groupBox.setObjectName("groupBox")
		# self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
		# self.gridLayout.setObjectName("gridLayout")
		# self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
		self.scrollArea.setWidget(self.scrollAreaWidgetContents)
		self.verticalLayout_2.addWidget(self.scrollArea)
##########################################################################################################
		self.qcombo.setStyleSheet("QListView::item {height:15px;}")
		size = QSize(12, 12)
		self.qcombo.setIconSize(size)
		self.qcombo.setContentsMargins(0,0,0,0)
		self.qcombo.setFont(PyQt5.QtGui.QFont('Piboto Condensed', 7))
		self.qcombo.setDuplicatesEnabled(False)
		self.qcombo.adjustSize()
		self.qcombo.keyPressEvent = self.filter_combo_box_key_pressed
		self.qcombo.currentIndexChanged.connect(self.on_combobox_changed)
		self.qcombo.currentIndexChanged.connect(self.cmbChanged)
		self.lastState = {}
		self.dispositivosMqtt = {}
		self.dispositivosMqtt.update(self.Devices.CONTROLADORES)
		for k, v in sorted(self.dispositivosMqtt.items()):
			self.qcombo.addItem(k)
			self.gridLayout_2.addWidget(self.createLayout_group_mqtt({**{"DISPOSITIVO":k},**{"STATUS":v}}))
			self.online.update({k:time.time()-10})
			self.lastState.update({k:"OFFLINE"})
			self.memory_qcombo.append(k)
		self.timer = QTimer()
		self.timer.setInterval(1000)
		self.timer.timeout.connect(self.recurring_timer)
		self.timer.start()
		self.newDevice = None
		self.mqttc = mqtt.Client(names.get_first_name(gender='male'))
		self.mqttc.on_message = self.on_message
		self.mqttc.on_connect = self.on_connect
		self.mqttc.on_disconnect = self.on_disconnect
		#~ self.mqttc.on_publish = self.on_publish
		self.mqttc.on_subscribe = self.on_subscribe
		# Uncomment to enable debug messages
		# mqttc.on_log = on_log
		self.mqttc.message_callback_add("MCC\#", self.on_message)
		print(sys.platform)
		if "win" in sys.platform:
			try:
				self.mqttc.connect("170.79.168.234", 1883, 60)
			except:
				self.mqttc.connect("172.17.1.228", 1883, 60)
		else:
			self.mqttc.connect("localhost", Config.PORTA_MQTT_LOCAL, 60)
		#mqttc.subscribe("mcc/#", 0)
		#~ mqttc.subscribe("esp32/output", 0)
		a = threading.Thread(target=self.loop_mqtt)
		a.start()
		self.show()


class UpdateWidget(QtWidgets.QWidget):
	def __init__(self, url_, parent=None):
		super(UpdateWidget, self).__init__(parent)
		self.setGeometry(0, 0, 0, 0)
		self._manager = QtNetwork.QNetworkAccessManager()
		self._manager.finished.connect(self.handleResults)
		self.url_ = url_
		self.filename = None
		self.setWindowOpacity(0.)
		flags = QtCore.Qt.WindowFlags()
		flags |= QtCore.Qt.SplashScreen
		self.setWindowFlags(flags)
		self.init_ui()
		if self.filename:
			self.upload()

	def init_ui(self):
		self.select_file()

	def select_file(self):
		if "win" in sys.platform:
			self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(
				self,
				"Open Image",
				QtCore.QDir.currentPath(),
				"(*.bin)"
			)
		else:
			self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(
				self,
				"Escolha o arquivo binário",
				"/home/pi/Crabit/vilatec/util",
				"(*.bin)"
			)
	def upload(self):
		try:
			path = self.filename
			files = {"image": path}
			multi_part = self.construct_multipart(files)
			if multi_part:
				url = QtCore.QUrl(self.url_)
				request = QtNetwork.QNetworkRequest(url)
				reply = self._manager.post(request, multi_part)
				multi_part.setParent(reply)
		except:
			printException()

	@QtCore.pyqtSlot(QtNetwork.QNetworkReply)
	def handleResults(self, reply):
		if reply.error() == QtNetwork.QNetworkReply.NoError:
			# ~ QtWidgets.QMessageBox.information(self, "Update", "Atualização realizada com sucesso!")
			msgBox = QtWidgets.QMessageBox(self)
			msgBox.setWindowTitle("Update")
			msgBox.setText('''<h1><strong><span style="color: #0000ff;">\
			Atualização realizada com sucesso!</span></strong></h1>''')
			bt1   = QPushButton('Ok')
			bt1.setMinimumWidth(180)
			bt1.setMaximumWidth(180)
			bt1.setMinimumHeight(80)
			msgBox.addButton(bt1, QMessageBox.YesRole)
			flags = QtCore.Qt.WindowFlags()
			flags |= QtCore.Qt.SplashScreen
			msgBox.setWindowFlags(flags)
			msg = msgBox.exec_()
		else:
			errorMessage = "Erro: {}".format(reply.errorString())
			QtWidgets.QMessageBox.critical(self, "Erro", errorMessage)
		reply.deleteLater()
		# ~ self.mainPage.show()
		self.destroy()

	def construct_multipart(self, files):
		try:
			multi_part = QtNetwork.QHttpMultiPart(QtNetwork.QHttpMultiPart.FormDataType)
			for field, filepath in  files.items():
				file = QtCore.QFile(filepath)
				if not file.open(QtCore.QIODevice.ReadOnly):
					break
				post_part = QtNetwork.QHttpPart()
				post_part.setHeader(QtNetwork.QNetworkRequest.ContentDispositionHeader,
					"form-data; name=\"{}\"; filename=\"{}\"".format(field, file.fileName()))
				post_part.setBodyDevice(file)
				file.setParent(multi_part)
				multi_part.append(post_part)
			return  multi_part
		except:
			printException()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = MyApp()
	sys.exit(app.exec_())

#sudo mount -t cifs //170.79.171.66/share /mnt/server_share/ -o username=pi,password=nbr5410!
# ~ sudo tar -xf arduino-1.8.12-linuxarm.tar.xz && sudo mv arduino-1.8.12 /opt && sudo /opt/arduino-1.8.12/install.sh
