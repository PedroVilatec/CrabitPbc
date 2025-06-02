import os
import json
class Devices():
	nivel_tanque = '{"STATUS_IP":"NÃO INICIADO","STATUS_VALVULA_SOLENOIDE":"NÃO CONECTADO","STATUS_NIVEL":"NÃO CONECTADO","STATUS_NIVEL_SIFAO": "","DESLIGA_ENCHE_TANQUE":"DESLIGA_ENCHE_TANQUE","ENCHE_TANQUE":"ENCHE_TANQUE"}'
	arduino = '{"STATUS FREQUENCIA":0, "STATUS PRESSAO":0, "STATUS_INVERSOR":"NÃO CONECTADO", "STATUS H2S":"", "STATUS RESET INV":"", "STATUS RESET 12V": "", "STATUS BOMBA":"", "STATUS ANALOG VALUE":0, "ENVIAR SERIAL":"", "STOP TROCA":"", "STOP TESTE":""}'
	bomba = '{"ZERA_OPERACOES": "", "STATUS_TEMP": "", "BOMBA": "", "STATUS_REGRESSIVA": "","STATUS_REGRESSIVA": "", "STATUS_HORA_OPERACAO": "", "NOME": ""}'
	acesso_eten = '{"STATUS_PORTA": "NÃO CONECTADO","STATUS_PWM": "NÃO CONECTADO","STATUS_TAG": "NÃO CONECTADO","STATUS_IP": "NÃO CONECTADO","STATUS_MAC": "","TESTE": "TESTE","STATUS_TEMPO_OPERACAO": "","GRAVA_TAG,66 27 73 C9": "GRAVA_TAG,66 27 73 C9","LISTA_TAGS": "LISTA_TAGS","ABRE": "FECHA","FECHA": "FECHA","PARA": "PARA"}'
	valvula_simples = '{"STATUS_SINAL_WIFI":"", "STATUS_TEMPO_OPERACAO":0,"STATUS_MAC":"", "STATUS_VALVULA":"", "STATUS_IP":"", "STATUS_CONTA_MOV":"", "OPERACOES":"OPERACOES", "LOOP":"", "ZERA_OPERACOES":"ZERA_OPERACOES", "STATUS_TEMPO_OPERACAO":0, "STATUS_VALVULA":"NÃO CONECTADO", "STATUS_IP":"NÃO CONECTADO", "NOME":"", "ABRE":"ABRE", "FECHA":"FECHA", "RESET":"RESET"}'
	valvula_cabine = '{"STATUS_FLUXO_DE_AR":0, "STATUS_SINAL_WIFI":"", "STATUS_TEMPO_OPERACAO":0, "STATUS_VALVULA":"NÃO CONECTADO", "STATUS_IP":"NÃO CONECTADO", "STATUS_CONTA_MOV":"", "OPERACOES":"OPERACOES", "LOOP":"", "ZERA_OPERACOES":"ZERA_OPERACOES", "STATUS_TEMPO_OPERACAO":"NÃO INICIADO", "STATUS_VALVULA":"NÃO CONECTADO", "STATUS_IP":"NÃO CONECTADO", "NOME":"", "ABRE":"ABRE", "FECHA":"FECHA", "RESET":"RESET", "CALIB_MAF":"CALIB_MAF", "ZERA_M3":"ZERA_M3", "DEBUG":"DEBUG", "CALIB_MAF":"CALIB_MAF", "HAB_BOT":"HAB_BOT"}'
	evaporadora = '{"LOOP": "", "S_IP": "", "S_D_RES": "", "S_RES": "", "S_TEMP": "", "S_COL": "", "S_EVAP": "", "S_WIFI": "", "S_MAC": "", "S_FEED": false, "S_C_MOV": "", "S_T_OP": "NAO INICIADO", "S_VAL": "NÃO CONECTADO", "ABRE": "ABRE", "ZERA_OPERACOES": "", "FECHA": "FECHA", "RESET": "", "LIGA_RESISTENCIA": "", "DESLIGA_RESISTENCIA": "", "NOME": ""}'
	evaporadora_sem_valvula = '{"STATUS_NIVEL_EVAPORADOR":"NÃO CONECTADO","STATUS_RESISTENCIA":"DESLIGADO","STATUS_DURACAO_RESISTENCIA": "0","STATUS_VALVULA": "0","STATUS_IP": "0","LIGA_RESISTENCIA":"LIGA_RESISTENCIA","ABRE_VALVULA":"ABRE_VALVULA","FECHA_VALVULA":"FECHA_VALVULA","DESLIGA_RESISTENCIA":"DESLIGA_RESISTENCIA"}'
	coletora = '{"STATUS_NIVEL":"NÃO CONECTADO","STATUS_BOMBA":"DESLIGADO","STATUS_DURACAO_BOMBA": "0","STATUS_CORRENTE_BOMBA": "0","STATUS_IP":"NÃO CONECTADO","LIGA_BOMBA":"LIGA_BOMBA","DESLIGA_BOMBA":"DESLIGA_BOMBA"}'
	CONTROLADORES = {
"ARDUINO":{"STATUS FREQUENCIA":"NÃO CONECTADO","STATUS PRESSAO":"","STATUS_INVERSOR":"NÃO CONECTADO","STATUS H2S":"","STATUS RESET INV":"","STATUS RESET 12V": "","STATUS BOMBA":"","STATUS ANALOG VALUE":"","ENVIAR SERIAL":"","STOP TROCA":"","STOP TESTE":""},    
"NIVEL_TANQUE_CABINE_1E":{"STATUS_IP":"NÃO INICIADO","STATUS_VALVULA_SOLENOIDE":"NÃO CONECTADO","STATUS_NIVEL":"NÃO CONECTADO","STATUS_NIVEL_SIFAO": "","DESLIGA_ENCHE_TANQUE":"DESLIGA_ENCHE_TANQUE","ENCHE_TANQUE":"ENCHE_TANQUE"},
"6D0F89EVAP_1EAB":json.loads(evaporadora),
"10C170EVAP_1ECD":json.loads(evaporadora),
"D15DB6EVAP_1EEF":json.loads(evaporadora),
"EVAPORADOR_CABINE_1E":json.loads(evaporadora_sem_valvula),
"EVAPORADORA_3_1EF":json.loads(evaporadora_sem_valvula),
"EVAPORADORA_1_1IJ":json.loads(evaporadora_sem_valvula),
"VALVULA_CABINE_1E":json.loads(valvula_cabine),
"ACESSO_ETEN_1E":json.loads(acesso_eten),
"BOMBA":json.loads(bomba),
"COLETORA_BLOCO_3_1EF":json.loads(coletora),
"COLETORA_BLOCO_2_1GH":json.loads(coletora),
"COLETORA_BLOCO_1_1IJ":json.loads(coletora),
"VALVULA_AM_1EA":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_001", "COD_SUB_BLOCO":"SUB_001"}},
"VALVULA_AM_1EB":json.loads(valvula_simples),
"VALVULA_AM_1EC":json.loads(valvula_simples),
"VALVULA_AM_1ED":json.loads(valvula_simples),
"VALVULA_AM_1EE":json.loads(valvula_simples),
"VALVULA_AM_1EF":json.loads(valvula_simples),
"VALVULA_AZ_1EA":json.loads(valvula_simples),
"VALVULA_AZ_1EB":json.loads(valvula_simples),
"VALVULA_AZ_1EC":json.loads(valvula_simples),
"VALVULA_AZ_1ED":json.loads(valvula_simples),
"VALVULA_AZ_1EE":json.loads(valvula_simples),
"VALVULA_AM_1EG":json.loads(valvula_simples),
"VALVULA_AZ_1EG":json.loads(valvula_simples),
"VALVULA_AM_1EH":json.loads(valvula_simples),
"VALVULA_AZ_1EH":json.loads(valvula_simples),
"VALVULA_AM_1EI":json.loads(valvula_simples),
"VALVULA_AZ_1EI":json.loads(valvula_simples),
"VALVULA_AM_1EJ":json.loads(valvula_simples),
"VALVULA_AZ_1EJ":json.loads(valvula_simples),
"VALVULA_AM_1EK":json.loads(valvula_simples),
"VALVULA_AZ_1EK":json.loads(valvula_simples),
"VALVULA_AM_1EL":json.loads(valvula_simples),
"VALVULA_AZ_1EL":json.loads(valvula_simples),
"VALVULA_AM_1EM":json.loads(valvula_simples),
"VALVULA_AZ_1EM":json.loads(valvula_simples),
"VALVULA_AM_1EN":json.loads(valvula_simples),
"VALVULA_AZ_1EN":json.loads(valvula_simples),
"VALVULA_AZ_BY":json.loads(valvula_simples),
"VALVULA_AM_BY":json.loads(valvula_simples),
"1592BAEVAP_1EIJ":json.loads(evaporadora),
"C75AC9EVAP_1EKL":json.loads(evaporadora),
"2AD757EVAP_1EGH":json.loads(evaporadora),
"C76798EVAP_1EMN":json.loads(evaporadora)

}
