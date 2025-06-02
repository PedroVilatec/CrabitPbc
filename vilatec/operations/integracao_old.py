#versao nova
import sys
import linecache
import json, requests
import sqlite3
from datetime import datetime
import threading
URL_BASE = "https://evolution-api.azurewebsites.net"
URL_DATABASE = "/home/pi/Crabit/instance/banco/vilatec.db"


USUARIO = "integracao@evolution.tech"
PASSWORD = "123456"

INTEGRACOES = {
	"LEITURA_TROCA_GASOSA": {
		"ROTA": "/gas_change",
		"ID_RETORNO": "id_leitura_troca_gasosa",
		"STATEMENT_CREATE": """CREATE TABLE IF NOT EXISTS LEITURA_TROCA_GASOSA (
					_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
					codigo_cliente VARCHAR(20) NOT NULL,
					codigo_estacao VARCHAR(20) NOT NULL,
					codigo_bloco VARCHAR(20),
					codigo_sub_bloco VARCHAR(20),
					data_leitura DATETIME,
					fluxo_de_ar NUMERIC(10,4),
					pressao NUMERIC(10,4),
					frequencia NUMERIC(10,4),
					quantidade_sepultados INTEGER,
					temperatura_media NUMERIC(10,4),
					umidade NUMERIC(10,4),
					situacao_teste VARCHAR(50),
					mensagem VARCHAR(4000),
					duracao TIME,
					ativo INTEGER DEFAULT 1,
					excluido INTEGER DEFAULT 0,
					data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP,
					id_integracao INT
					);""",
		"STATEMENT_SELECT": "SELECT _id, codigo_cliente, codigo_estacao, codigo_bloco, codigo_sub_bloco, data_leitura, fluxo_de_ar, pressao, frequencia, quantidade_sepultados, temperatura_media, umidade, situacao_teste, mensagem, duracao FROM LEITURA_TROCA_GASOSA WHERE id_integracao IS NULL",
		"STATEMENT_UPDATE": "UPDATE LEITURA_TROCA_GASOSA SET id_integracao = ? WHERE _id = ?",
		"STATEMENT_INSERT": "INSERT INTO LEITURA_TROCA_GASOSA (codigo_cliente, codigo_estacao, codigo_bloco, codigo_sub_bloco, data_leitura, fluxo_de_ar, pressao, frequencia, quantidade_sepultados, temperatura_media, umidade, situacao_teste, mensagem, duracao) VALUES ('val_codigo_cliente', 'val_codigo_estacao', 'val_codigo_bloco', 'val_codigo_sub_bloco', 'val_data_leitura', val_fluxo_de_ar, val_pressao, val_frequencia, val_quantidade_sepultados, val_temperatura_media, val_umidade, 'val_situacao_teste', 'val_mensagem', 'val_duracao')",
		"STATEMENT_DELETE": "DELETE FROM LEITURA_TROCA_GASOSA WHERE data_leitura < date('now','start of month') AND id_integracao IS NOT NULL",
		"DATA": {
			"codigo_cliente": "",
			"codigo_estacao": "",
			"codigo_bloco": "",
			"codigo_sub_bloco": "",
			"data_leitura": "",
			"fluxo_de_ar": "",
			"pressao": "",
			"frequencia": "",
			"quantidade_sepultados": "",
			"temperatura_media": "",
			"umidade": "",
			"situacao_teste": "",
			"mensagem":"",
			"duracao": ""
		}
	},
	"LEITURA_ESTANQUEIDADE":{
		"ROTA": "/tightness",
		"ID_RETORNO": "id_leitura_estanqueidade",
		"STATEMENT_CREATE": """CREATE TABLE IF NOT EXISTS LEITURA_ESTANQUEIDADE (
					_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
					codigo_cliente VARCHAR(20) NOT NULL,
					codigo_estacao VARCHAR(20) NOT NULL,
					codigo_bloco VARCHAR(20),
					codigo_sub_bloco VARCHAR(20),
					data_leitura DATETIME,
					duracao TIME,
					data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP,
					situacao_teste VARCHAR(50),
					mensagem VARCHAR(4000),
					pressao_ideal NUMERIC(10,4),
					pressao_obtida NUMERIC(10,4),
					valor_analogo NUMERIC(10,4),
					ativo INTEGER DEFAULT 1,
					excluido INTEGER DEFAULT 0,
					id_integracao INT
					);""",
		"STATEMENT_SELECT": "SELECT _id, codigo_cliente, codigo_estacao, codigo_bloco, codigo_sub_bloco, data_leitura, duracao, situacao_teste, mensagem, pressao_ideal, pressao_obtida, valor_analogo FROM leitura_estanqueidade WHERE id_integracao IS NULL",
		"STATEMENT_UPDATE": "UPDATE leitura_estanqueidade SET id_integracao = ? WHERE _id = ?",
		"STATEMENT_INSERT": "INSERT INTO leitura_estanqueidade (codigo_cliente, codigo_estacao, codigo_bloco, codigo_sub_bloco, data_leitura, duracao, situacao_teste, mensagem, pressao_ideal, pressao_obtida, valor_analogo) VALUES ('val_codigo_cliente', 'val_codigo_estacao', 'val_codigo_bloco', 'val_codigo_sub_bloco', 'val_data_leitura', 'val_duracao', 'val_situacao_teste', 'val_mensagem', 'val_pressao_ideal', 'val_pressao_obtida', 'val_valor_analogo') ",
		"STATEMENT_DELETE": "DELETE FROM leitura_estanqueidade WHERE data_leitura < date('now','start of month') AND id_integracao IS NOT NULL",
		"DATA": {
			"codigo_cliente": "",
			"codigo_estacao": "",
			"codigo_bloco": "",
			"codigo_sub_bloco": "",
			"data_leitura": "",
			"duracao": "",
			"situacao_teste": "",
			"mensagem":"",
			"pressao_ideal": "",
			"pressao_obtida": "",
			"valor_analogo": ""
		}
	},
	"LEITURA_EQUIPAMENTO":{
		"ROTA": "/hardware",
		"ID_RETORNO": "id_leitura_equipamento",
		"STATEMENT_CREATE": """CREATE TABLE IF NOT EXISTS LEITURA_EQUIPAMENTO (
					_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
					codigo_cliente VARCHAR(20) NOT NULL,
					codigo_estacao VARCHAR(20) NOT NULL,
					codigo_bloco VARCHAR(20),
					codigo_sub_bloco VARCHAR(20),
					codigo_equipamento VARCHAR(20),
					data_leitura DATETIME,
					duracao TIME,
					data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP,
					situacao_teste VARCHAR(50),
					mensagem VARCHAR(4000),
					valor NUMERIC(10,4),
					indicacao VARCHAR(20),
					id_integracao INT
					);""",
		"STATEMENT_SELECT": "SELECT _id, codigo_cliente, codigo_estacao, codigo_bloco, codigo_sub_bloco, codigo_equipamento, data_leitura, duracao,  situacao_teste, mensagem, valor, indicacao FROM leitura_equipamento WHERE id_integracao IS NULL AND codigo_sub_bloco IS NOT NULL",
		"STATEMENT_UPDATE": "UPDATE LEITURA_EQUIPAMENTO SET id_integracao = ? WHERE _id = ?",
		"STATEMENT_INSERT": "INSERT INTO LEITURA_EQUIPAMENTO (codigo_cliente, codigo_estacao, codigo_bloco, codigo_sub_bloco, codigo_equipamento, data_leitura, duracao, situacao_teste, mensagem, valor, indicacao) VALUES ('val_codigo_cliente', 'val_codigo_estacao', 'val_codigo_bloco', 'val_codigo_sub_bloco', 'val_codigo_equipamento', 'val_data_leitura', 'val_duracao', 'val_situacao_teste', 'val_mensagem', 'val_valor', 'val_indicacao') ",
		"STATEMENT_DELETE": "DELETE FROM LEITURA_EQUIPAMENTO WHERE data_leitura < date('now','start of month') AND id_integracao IS NOT NULL",
		"DATA": {
			"codigo_cliente": "",
			"codigo_estacao": "",
			"codigo_bloco": "",
			"codigo_sub_bloco": "",
			"codigo_equipamento": "",
			"data_leitura": "",
			"duracao": "",
			"situacao_teste": "",
			"mensagem":"",
			"valor": "",
			"indicacao": ""
		}
	},
	"LEITURA_EQUIPAMENTO_ESTACAO":{
		"ROTA": "/hardware_estation",
		"ID_RETORNO": "id_leitura_equipamento",
		"STATEMENT_CREATE": """CREATE TABLE IF NOT EXISTS LEITURA_EQUIPAMENTO_ESTACAO (
					_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
					codigo_cliente VARCHAR(20) NOT NULL,
					codigo_estacao VARCHAR(20) NOT NULL,
					codigo_equipamento VARCHAR(20),
					data_leitura DATETIME,
					duracao TIME,
					data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP,
					situacao_teste VARCHAR(50),
					mensagem VARCHAR(4000),
					valor NUMERIC(10,4),
					indicacao VARCHAR(20),
					id_integracao INT
					);""",
		"STATEMENT_SELECT": "SELECT _id, codigo_cliente, codigo_estacao, codigo_equipamento, data_leitura, duracao,  situacao_teste, mensagem, valor, indicacao FROM leitura_equipamento WHERE id_integracao IS NULL AND codigo_sub_bloco IS NULL",
		"STATEMENT_UPDATE": "UPDATE leitura_equipamento SET id_integracao = ? WHERE _id = ?",
		"STATEMENT_INSERT": "INSERT INTO leitura_equipamento (codigo_cliente, codigo_estacao, codigo_equipamento, data_leitura, duracao, situacao_teste, valor, indicacao) VALUES ('val_codigo_cliente', 'val_codigo_estacao', 'val_codigo_equipamento', 'val_data_leitura', 'val_duracao', 'val_situacao_teste', 'val_valor', 'val_indicacao') ",
		"STATEMENT_DELETE": "DELETE FROM leitura_equipamento WHERE data_leitura < date('now','start of month') AND id_integracao IS NOT NULL",
		"DATA": {
			"codigo_cliente": "",
			"codigo_estacao": "",
			"codigo_equipamento": "",
			"data_leitura": "",
			"duracao": "",
			"situacao_teste": "",
			"valor": "",
			"indicacao": ""
		}
	},
	"LER_CONFIG":{
		"ROTA": "/config",
		"PARAMS": {
			"codigo_cliente": "",
			"codigo_estacao_tratamento": ""
		}
	},
	"LEITURA_OPERACAO_EQUIPAMENTO":{
		"ROTA": "/statics",
		"ID_RETORNO": "id_leitura_operacao_equipamento",
		"STATEMENT_CREATE": """CREATE TABLE IF NOT EXISTS LEITURA_OPERACAO_EQUIPAMENTO (
					_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
					codigo_cliente VARCHAR(20) NOT NULL,
					codigo_estacao VARCHAR(20) NOT NULL,
					codigo_equipamento VARCHAR(20),
					data_leitura DATETIME,
					data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP,
					situacao_teste VARCHAR(50),
					mensagem VARCHAR(4000),
					quantidade NUMERIC(4,1),
					id_integracao INT
					);""",
		"STATEMENT_SELECT": "SELECT _id, codigo_cliente, codigo_estacao, codigo_equipamento, data_leitura, situacao_teste, mensagem, quantidade FROM LEITURA_OPERACAO_EQUIPAMENTO WHERE id_integracao IS NULL",
		"STATEMENT_UPDATE": "UPDATE LEITURA_OPERACAO_EQUIPAMENTO SET id_integracao = ? WHERE _id = ?",
		"STATEMENT_INSERT": "INSERT INTO LEITURA_OPERACAO_EQUIPAMENTO (codigo_cliente, codigo_estacao, codigo_equipamento, data_leitura, situacao_teste, mensagem, quantidade) VALUES ('val_codigo_cliente', 'val_codigo_estacao', 'val_codigo_equipamento', 'val_data_leitura', 'val_situacao_teste', 'val_mensagem', 'val_quantidade') ",
		"STATEMENT_DELETE": "DELETE FROM LEITURA_OPERACAO_EQUIPAMENTO WHERE data_leitura < date('now','start of month') AND id_integracao IS NOT NULL",
		"DATA": {
			"codigo_cliente": "",
			"codigo_estacao": "",
			"codigo_equipamento": "",
			"data_leitura": "",
			"situacao_teste": "",
			"mensagem": "",
			"quantidade": "",
		}
	},
	"LEITURA_CONSUMO_ELETRICO": {
		"ROTA": "/electric_consumption",
		"ID_RETORNO": "id_leitura_consumo_eletrico",
		"STATEMENT_CREATE": """CREATE TABLE IF NOT EXISTS LEITURA_CONSUMO_ELETRICO (
					_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
					codigo_cliente VARCHAR(20) NOT NULL,
					codigo_estacao VARCHAR(20) NOT NULL,
					data_leitura DATETIME,
					consumo_eletrico NUMERIC(10,4),
					valor_consumo NUMERIC(10,4),
					data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP,
					situacao_teste VARCHAR(50),
					mensagem VARCHAR(4000),
					id_integracao INT
					);""",
		"STATEMENT_SELECT": "SELECT _id, codigo_cliente, codigo_estacao, data_leitura, consumo_eletrico, valor_consumo, mensagem, situacao_teste FROM LEITURA_CONSUMO_ELETRICO WHERE id_integracao IS NULL",
		"STATEMENT_UPDATE": "UPDATE LEITURA_CONSUMO_ELETRICO SET id_integracao = ? WHERE _id = ?",
		"STATEMENT_INSERT": "INSERT INTO LEITURA_CONSUMO_ELETRICO (codigo_cliente, codigo_estacao, data_leitura, consumo_eletrico, valor_consumo, situacao_teste, mensagem) VALUES ('val_codigo_cliente', 'val_codigo_estacao', 'val_data_leitura', val_consumo_eletrico, val_valor_consumo, 'val_situacao_teste', 'val_mensagem')",
		"STATEMENT_DELETE": "DELETE FROM LEITURA_CONSUMO_ELETRICO WHERE data_leitura < datetime('now','start of month') AND id_integracao IS NOT NULL",
		"DATA": {
			"codigo_cliente": "",
			"codigo_estacao": "",
			"data_leitura": "",
			"consumo_eletrico": "",
			"valor_consumo": "",
			"situacao_teste": "",
			"mensagem": ""
		}
	},
	"LEITURA_EFICIENCIA_ETEN": {
		"ROTA": "/eten_eficiency",
		"ID_RETORNO": "id_leitura_eficiencia_eten",
		"STATEMENT_CREATE": """CREATE TABLE IF NOT EXISTS LEITURA_EFICIENCIA_ETEN (
					_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
					codigo_cliente VARCHAR(20) NOT NULL,
					codigo_estacao VARCHAR(20) NOT NULL,
					data_leitura DATETIME,
					h2s_antes NUMERIC(4,1),
					h2s_depois NUMERIC(4,1),
					eficiencia NUMERIC(4,1),
					meta NUMERIC(4,1),
					data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP,
					situacao_teste VARCHAR(50),
					mensagem VARCHAR(4000),
					id_integracao INT
					);""",
		"STATEMENT_SELECT": "SELECT _id, codigo_cliente, codigo_estacao, data_leitura, h2s_antes, h2s_depois, eficiencia, meta, mensagem, situacao_teste FROM LEITURA_EFICIENCIA_ETEN WHERE id_integracao IS NULL",
		"STATEMENT_UPDATE": "UPDATE LEITURA_EFICIENCIA_ETEN SET id_integracao = ? WHERE _id = ?",
		"STATEMENT_INSERT": "INSERT INTO LEITURA_EFICIENCIA_ETEN (codigo_cliente, codigo_estacao, data_leitura, h2s_antes, h2s_depois, eficiencia, meta, situacao_teste, mensagem) VALUES ('val_codigo_cliente', 'val_codigo_estacao', 'val_data_leitura', 'val_h2s_antes', 'val_h2s_depois', 'val_eficiencia', 'val_meta', 'val_situacao_teste','val_mensagem')",
		"STATEMENT_DELETE": "DELETE FROM LEITURA_EFICIENCIA_ETEN WHERE data_leitura < date('now','start of month') AND id_integracao IS NOT NULL",
		"DATA": {
			"codigo_cliente": "",
			"codigo_estacao": "",
			"data_leitura": "",
			"h2s_antes": "",
			"h2s_depois": "",
			"eficiencia": "",
			"meta": "",
			"situacao_teste": "",
			"mensagem":""
		}
	},
	"LEITURA_TEMPERATURA_INTERNA": {
		"ROTA": "/internal_temperature",
		"ID_RETORNO": "id_leitura_temperatura_interna",
		"STATEMENT_CREATE": """CREATE TABLE IF NOT EXISTS LEITURA_TEMPERATURA_INTERNA (
					_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
					codigo_cliente VARCHAR(20) NOT NULL,
					codigo_estacao VARCHAR(20) NOT NULL,
					data_leitura DATETIME,
					data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP,
					temp_manha NUMERIC(4,1),
					temp_tarde NUMERIC(4,1),
					temp_noite NUMERIC(4,1),
					situacao_teste VARCHAR(50),
					mensagem VARCHAR(4000),
					id_integracao INT
					);""",
		"STATEMENT_SELECT": "SELECT _id, codigo_cliente, codigo_estacao, data_leitura, temp_manha, temp_tarde, temp_noite, mensagem, situacao_teste FROM LEITURA_TEMPERATURA_INTERNA WHERE id_integracao IS NULL",
		"STATEMENT_UPDATE": "UPDATE LEITURA_TEMPERATURA_INTERNA SET id_integracao = ? WHERE _id = ?",
		"STATEMENT_INSERT": "INSERT INTO LEITURA_TEMPERATURA_INTERNA (codigo_cliente, codigo_estacao, data_leitura, temp_manha, temp_tarde, temp_noite, situacao_teste, mensagem) VALUES ('val_codigo_cliente', 'val_codigo_estacao', 'val_data_leitura', val_temp_manha, val_temp_tarde, val_temp_noite, 'val_situacao_teste','val_mensagem')",
		"STATEMENT_DELETE": "DELETE FROM LEITURA_TEMPERATURA_INTERNA WHERE data_leitura < date('now','start of month') AND id_integracao IS NOT NULL",
		"DATA": {
			"codigo_cliente": "",
			"codigo_estacao": "",
			"data_leitura": "",
			"temp_manha": "",
			"temp_tarde": "",
			"temp_noite": "",
			"situacao_teste": "",
			"mensagem":""
		}
	},
	"LEITURA_VARIACAO_UMIDADE": {
		"ROTA": "/moisture_variation",
		"ID_RETORNO": "id_leitura_variacao_umidade",
		"STATEMENT_CREATE": """CREATE TABLE IF NOT EXISTS LEITURA_VARIACAO_UMIDADE (
					_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
					codigo_cliente VARCHAR(20) NOT NULL,
					codigo_estacao VARCHAR(20) NOT NULL,
					data_leitura DATETIME,
					data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP,
					var_manha NUMERIC(4,1),
					var_tarde NUMERIC(4,1),
					var_noite NUMERIC(4,1),
					situacao_teste VARCHAR(50),
					mensagem VARCHAR(4000),
					id_integracao INT
					);""",
		"STATEMENT_SELECT": "SELECT _id, codigo_cliente, codigo_estacao, data_leitura, var_manha, var_tarde, var_noite,mensagem,  situacao_teste FROM LEITURA_VARIACAO_UMIDADE WHERE id_integracao IS NULL",
		"STATEMENT_UPDATE": "UPDATE LEITURA_VARIACAO_UMIDADE SET id_integracao = ? WHERE _id = ?",
		"STATEMENT_INSERT": "INSERT INTO LEITURA_VARIACAO_UMIDADE (codigo_cliente, codigo_estacao, data_leitura, var_manha, var_tarde, var_noite, situacao_teste, mensagem) VALUES ('val_codigo_cliente', 'val_codigo_estacao', 'val_data_leitura', val_var_manha, val_var_tarde, val_var_noite, 'val_situacao_teste','val_mensagem')",
		"STATEMENT_DELETE": "DELETE FROM LEITURA_VARIACAO_UMIDADE WHERE data_leitura < date('now','start of month') AND id_integracao IS NOT NULL",
		"DATA": {
			"codigo_cliente": "",
			"codigo_estacao": "",
			"data_leitura": "",
			"var_manha": "",
			"var_tarde": "",
			"var_noite": "",
			"situacao_teste": "",
			"mensagem":""
		}
	},
	"LEITURA_VOL_CONDENSADO_EVAPORADO": {
		"ROTA": "/evaporated_condensed_vol",
		"ID_RETORNO": "id_leitura_vol_condensado_evaporado",
		"STATEMENT_CREATE": """CREATE TABLE IF NOT EXISTS LEITURA_VOL_CONDENSADO_EVAPORADO (
					_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
					codigo_cliente VARCHAR(20) NOT NULL,
					codigo_estacao VARCHAR(20) NOT NULL,
					data_leitura DATETIME,
					data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP,
					volume NUMERIC(10,4),
					situacao_teste VARCHAR(50),
					mensagem VARCHAR(4000),
					id_integracao INT
					);""",
		"STATEMENT_SELECT": "SELECT _id, codigo_cliente, codigo_estacao, data_leitura, volume, mensagem, situacao_teste FROM LEITURA_VOL_CONDENSADO_EVAPORADO WHERE id_integracao IS NULL",
		"STATEMENT_UPDATE": "UPDATE LEITURA_VOL_CONDENSADO_EVAPORADO SET id_integracao = ? WHERE _id = ?",
		"STATEMENT_INSERT": "INSERT INTO LEITURA_VOL_CONDENSADO_EVAPORADO (codigo_cliente, codigo_estacao, data_leitura, volume, situacao_teste, mensagem) VALUES ('val_codigo_cliente', 'val_codigo_estacao', 'val_data_leitura', 'val_volume', 'val_situacao_teste', 'val_mensagem')",
		"STATEMENT_DELETE": "DELETE FROM LEITURA_VOL_CONDENSADO_EVAPORADO WHERE data_leitura < date('now','start of month') AND id_integracao IS NOT NULL",
		"DATA": {
			"codigo_cliente": "",
			"codigo_estacao": "",
			"data_leitura": "",
			"volume": "",
			"situacao_teste": "",
			"mensagem":""
		}
	},
}

def printException():
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def formataText(text):
	if text is None:
		return ''
	return str(text)


def integrar(integracao, access_token, obj):
	try:
		data = json.dumps(obj)
		headers = {
			'Content-Type': 'application/json',
			'Authorization': 'Bearer ' + access_token
		}
		rota = INTEGRACOES[integracao]["ROTA"]
		id_retorno = INTEGRACOES[integracao]["ID_RETORNO"]

		response = requests.post(URL_BASE + rota, headers=headers, data=data, timeout=(30, 200))

		if response.status_code != 200:
			raise Exception(response.content.decode('UTF-8'))

		data = json.loads(response.content.decode('UTF-8'))

		response = {
			'status': True,
			'data': data[id_retorno],
			'message': None
		}
	except Exception as e:
		response = {
			'status': False,
			'data': None,
			'message': e
		}

	return response

def consultar(integracao, access_token, params):
	try:
		headers = {
			'Content-Type': 'application/json',
			'Authorization': 'Bearer ' + access_token
		}
		headers.update(params)

		rota = INTEGRACOES[integracao]["ROTA"]

		response = requests.get(URL_BASE + rota, headers=headers)

		if response.status_code != 200:
			raise Exception(response.content.decode('UTF-8'))

		data = json.loads(response.content.decode('UTF-8'))

		response = {
			'status': True,
			'data': data,
			'message': None
		}
	except Exception as e:
		response = {
			'status': False,
			'data': None,
			'message': e
		}

	return response

def enviar(integracao):
	envio = threading.Thread(target=enviar_thread, args=(integracao,))
	envio.start()

def enviar_thread(integracao):
	try:
		print("Enviando integração")
		data = {"username": USUARIO, "password": PASSWORD}
		headers = {'Content-Type': 'application/json'}

		response = requests.post(URL_BASE + "/login", headers=headers, data=json.dumps(data), timeout=(30, 200))

		if response.status_code != 200:
			raise Exception(response.content)

		access_token = json.loads(response.content.decode('UTF-8'))
		access_token = access_token["access_token"]

		statement_select = INTEGRACOES[integracao]["STATEMENT_SELECT"]
		statement_update = INTEGRACOES[integracao]["STATEMENT_UPDATE"]
		statement_delete = INTEGRACOES[integracao]["STATEMENT_DELETE"]

		data = INTEGRACOES[integracao]["DATA"]

		conn = sqlite3.connect(URL_DATABASE)
		cursor = conn.cursor()
		cursor.execute(statement_select)
		columns = cursor.description
		result = []
		for value in cursor.fetchall():
			tmp = {}
			for (index, column) in enumerate(value):
				tmp[columns[index][0]] = column
			result.append(tmp)
		cursor.close()

		if result:
			for item in result:
				id_leitura = item['_id']

				for i, key in enumerate(data.keys()):

					if key == 'data_leitura':
						if(isinstance(item['data_leitura'], datetime)):
							data[key] = str(item['data_leitura'])
						else:
							data[key] = str(item['data_leitura'][0:19])
					else:
						data[key] = str(item[key])

				response = integrar(integracao, access_token, data)

				if response["status"]:
					id_integracao = response["data"]

					cursor = conn.cursor()
					cursor.execute(statement_update, (id_integracao, id_leitura))
					conn.commit()
					cursor.close()
				#~ else:
					#~ print("Falha na Integracao: " + str(response["message"]) + str(item["_id"]))

			cursor = conn.cursor()
			cursor.execute(statement_delete)
			conn.commit()
			cursor.close()


		conn.close()
	except Exception as e:
		printException()
		print('CustomErrorEnviar: ' + str(e) + " in " + integracao)


def registrar(integracao, item):
	registro = threading.Thread(target=registrar_thread, args=(integracao, item))
	registro.start()

def registrar_thread(integracao, item):
	try:
		conn = sqlite3.connect(URL_DATABASE)
		cursor = conn.cursor()
	except Exception as e:
		print('Erro de conexão: ' + str(e))

	try:
		statement_create = INTEGRACOES[integracao]["STATEMENT_CREATE"]
		cursor.execute(statement_create)

		statement_insert = INTEGRACOES[integracao]["STATEMENT_INSERT"]
		data = INTEGRACOES[integracao]["DATA"]

		for i, key in enumerate(data.keys()):
			# print(key)
			if key == 'data_leitura' and 'data_leitura' not in item:
				statement_insert = statement_insert.replace('val_data_leitura', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
			else:
				# print(str(item[key]))
				search = 'val_'+key
				if search in statement_insert:
					statement_insert = statement_insert.replace(search, str(item[key]))

		#print(statement_insert)
		cursor.execute(statement_insert)

		conn.commit()
		cursor.close()
		conn.close()
	except Exception as e:
		printException()
		print('CustomErrorRegistra: ' + str(e) + " in " + integracao)


def ler(integracao, _params):
	data = {"username": USUARIO, "password": PASSWORD}
	headers = {'Content-Type': 'application/json'}

	response = requests.post(URL_BASE + "/login", headers=headers, data=json.dumps(data))

	if response.status_code != 200:
		raise Exception(response.content.decode('UTF-8'))

	access_token = json.loads(response.content.decode('UTF-8'))
	print(access_token)
	access_token = access_token["access_token"]

	params = INTEGRACOES[integracao]["PARAMS"]

	data = []
	for (index, column) in enumerate(params):
		data.append((
			column, _params[column]
		))
	print(data)
	response = consultar(integracao, access_token, data)
	print(response)
	if response["status"]:
		result = response["data"]
	else:
		result = "ERRO AO CONSULTAR DADOS: " + str(response["message"])

	return result
