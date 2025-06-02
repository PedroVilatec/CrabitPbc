import os
import json
class Devices():
        nivel_tanque = '{"STATUS_IP":"NÃƒO INICIADO","STATUS_VALVULA_SOLENOIDE":"NÃƒO CONECTADO","STATUS_NIVEL":"NÃƒO CONECTADO","STATUS_NIVEL_SIFAO": "","DESLIGA_ENCHE_TANQUE":"DESLIGA_ENCHE_TANQUE","ENCHE_TANQUE":"ENCHE_TANQUE"}'
        arduino = '{"STATUS FREQUENCIA":0, "STATUS PRESSAO":0, "STATUS_INVERSOR":"NÃƒO CONECTADO", "STATUS H2S":"", "STATUS RESET INV":"", "STATUS RESET 12V": "", "STATUS BOMBA":"", "STATUS ANALOG VALUE":0, "ENVIAR SERIAL":"", "STOP TROCA":"", "STOP TESTE":""}'
        bomba = '{"ZERA_OPERACOES": "", "STATUS_TEMP": "", "BOMBA": "", "STATUS_REGRESSIVA": "","STATUS_REGRESSIVA": "", "STATUS_HORA_OPERACAO": "", "NOME": ""}'
        acesso_eten = '{"NOME":"","STATUS_PORTA": "NÃƒO CONECTADO","STATUS_PWM": "NÃƒO CONECTADO","STATUS_TAG": "NÃƒO CONECTADO","STATUS_IP": "NÃƒO CONECTADO","STATUS_MAC": "","TESTE": "TESTE","STATUS_TEMPO_OPERACAO": "","LISTA_TAGS": "LISTA_TAGS","ABRE": "FECHA","FECHA": "FECHA","PARA": "PARA","RESET": "RESET","GRAVA_TAG": "GRAVA_TAG"}'
        valvula_simples = '{"STATUS_SINAL_WIFI":"", "STATUS_TEMPO_OPERACAO":0,"STATUS_MAC":"", "STATUS_VALVULA":"", "STATUS_IP":"", "STATUS_CONTA_MOV":"", "OPERACOES":"OPERACOES", "LOOP":"", "ZERA_OPERACOES":"ZERA_OPERACOES", "STATUS_TEMPO_OPERACAO":0, "STATUS_VALVULA":"NÃƒO CONECTADO", "STATUS_IP":"NÃƒO CONECTADO", "NOME":"", "ABRE":"ABRE", "FECHA":"FECHA", "RESET":"RESET"}'
        valvula_cabine = '{"LOOP":"", "ZERA_OPERACOES":"ZERA_OPERACOES", "NOME":"", "ABRE":"ABRE", "FECHA":"FECHA", "RESET":"RESET","ZERA_M3":"ZERA_M3", "DEBUG":"DEBUG"}'
        evaporadora = '{"LOOP": "", "S_IP": "", "S_D_RES": "", "S_RES": "", "S_TEMP": "", "S_COL": "", "S_EVAP": "", "S_WIFI": "", "S_MAC": "", "S_FEED": false, "S_C_MOV": "", "S_T_OP": "NAO INICIADO", "S_VAL": "NÃƒO CONECTADO", "ABRE": "ABRE", "ZERA_OPERACOES": "", "FECHA": "FECHA", "RESET": "", "LIGA_RESISTENCIA": "", "DESLIGA_RESISTENCIA": "", "NOME": ""}'
        evaporadora_sem_valvula = '{"STATUS_NIVEL_EVAPORADOR":"NÃƒO CONECTADO","STATUS_RESISTENCIA":"DESLIGADO","STATUS_DURACAO_RESISTENCIA": "0","STATUS_VALVULA": "0","STATUS_IP": "0","LIGA_RESISTENCIA":"LIGA_RESISTENCIA","ABRE_VALVULA":"ABRE_VALVULA","FECHA_VALVULA":"FECHA_VALVULA","DESLIGA_RESISTENCIA":"DESLIGA_RESISTENCIA"}'
        coletora = '{"STATUS_NIVEL":"NÃƒO CONECTADO","STATUS_BOMBA":"DESLIGADO","STATUS_DURACAO_BOMBA": "0","STATUS_CORRENTE_BOMBA": "0","STATUS_IP":"NÃƒO CONECTADO","LIGA_BOMBA":"LIGA_BOMBA","DESLIGA_BOMBA":"DESLIGA_BOMBA"}'
        CONTROLADORES = {
            "ARDUINO":json.loads(arduino),
            "NIVEL_TANQUE_CABINE_1E":json.loads(nivel_tanque),

            "EVAPORADOR_CABINE":json.loads(evaporadora_sem_valvula),
            "VALVULA_CABINE_1":json.loads(valvula_cabine),
            "VALVULA_CABINE_2":json.loads(valvula_cabine),
            "VALVULA_CABINE_3":json.loads(valvula_cabine),
            "VALVULA_CABINE_4":json.loads(valvula_cabine),
            "VALVULA_CABINE_5":json.loads(valvula_cabine),
            "VALVULA_CABINE_6":json.loads(valvula_cabine),
            "VALVULA_CABINE_7":json.loads(valvula_cabine),
            "ACESSO_ETEN":json.loads(acesso_eten),
            "ACESSO_ETEN_1":json.loads(acesso_eten),
            "BOMBA":json.loads(bomba),
            "VALVULA_AM_1EA":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_001", "COD_SUB_BLOCO":"SUB_PAR"}},
            "VALVULA_AM_1EB":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_001", "COD_SUB_BLOCO":"SUB_IMPAR"}},
            "VALVULA_AM_1EC":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_002", "COD_SUB_BLOCO":"SUB_PAR"}},
            "VALVULA_AM_1ED":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_002", "COD_SUB_BLOCO":"SUB_IMPAR"}},
            "VALVULA_AM_1EE":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_003", "COD_SUB_BLOCO":"SUB_PAR"}},
            "VALVULA_AM_1EF":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_003", "COD_SUB_BLOCO":"SUB_IMPAR"}},
            "VALVULA_AM_1EG":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_007", "COD_SUB_BLOCO":"SUB_PAR"}},
            "VALVULA_AM_1EH":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_007", "COD_SUB_BLOCO":"SUB_IMPAR"}},
            "VALVULA_AM_1EI":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_008", "COD_SUB_BLOCO":"SUB_PAR"}},
            "VALVULA_AM_1EJ":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_008", "COD_SUB_BLOCO":"SUB_IMPAR"}},
            "VALVULA_AM_1EK":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_009", "COD_SUB_BLOCO":"SUB_PAR"}},
            "VALVULA_AM_1EL":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_009", "COD_SUB_BLOCO":"SUB_IMPAR"}},
            "VALVULA_AM_1EM":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_010", "COD_SUB_BLOCO":"SUB_PAR"}},
            "VALVULA_AM_1EN":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_010", "COD_SUB_BLOCO":"SUB_IMPAR"}},
            "VALVULA_AM_BY":json.loads(valvula_simples),

            "VALVULA_AZ_1EA":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_001", "COD_SUB_BLOCO":"SUB_PAR"}},
            "VALVULA_AZ_1EB":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_001", "COD_SUB_BLOCO":"SUB_IMPAR"}},
            "VALVULA_AZ_1EC":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_002", "COD_SUB_BLOCO":"SUB_PAR"}},
            "VALVULA_AZ_1ED":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_002", "COD_SUB_BLOCO":"SUB_IMPAR"}},
            "VALVULA_AZ_1EE":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_003", "COD_SUB_BLOCO":"SUB_PAR"}},
            "VALVULA_AZ_1EF":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_003", "COD_SUB_BLOCO":"SUB_IMPAR"}},
            "VALVULA_AZ_1EG":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_007", "COD_SUB_BLOCO":"SUB_PAR"}},
            "VALVULA_AZ_1EH":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_007", "COD_SUB_BLOCO":"SUB_IMPAR"}},
            "VALVULA_AZ_1EI":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_008", "COD_SUB_BLOCO":"SUB_PAR"}},
            "VALVULA_AZ_1EJ":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_008", "COD_SUB_BLOCO":"SUB_IMPAR"}},
            "VALVULA_AZ_1EK":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_009", "COD_SUB_BLOCO":"SUB_PAR"}},
            "VALVULA_AZ_1EL":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_009", "COD_SUB_BLOCO":"SUB_IMPAR"}},
            "VALVULA_AZ_1EM":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_010", "COD_SUB_BLOCO":"SUB_PAR"}},
            "VALVULA_AZ_1EN":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_010", "COD_SUB_BLOCO":"SUB_IMPAR"}},
            "VALVULA_AZ_BY":json.loads(valvula_simples),


            "EVAPORADOR_1EAB":json.loads(evaporadora),
            "EVAPORADOR_1ECD":json.loads(evaporadora),
            "EVAPORADOR_1EEF":json.loads(evaporadora),
            "EVAPORADOR_1EIJ":json.loads(evaporadora),
            "EVAPORADOR_1EKL":json.loads(evaporadora),
            "EVAPORADOR_1EGH":json.loads(evaporadora),
            "EVAPORADOR_1EMN":json.loads(evaporadora)
        }
