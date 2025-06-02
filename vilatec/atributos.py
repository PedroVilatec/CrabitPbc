import json
disp = {
        "nivel_tanque":
            {
                "S_IP":"",
                "S_VALVULA_SOLENOIDE":"",
                "S_NIVEL":"",
                "S_NIVEL_SIFAO": "",
                "DESLIGA_ENCHE_TANQUE":"DESLIGA_ENCHE_TANQUE",
                "ENCHE_TANQUE":"ENCHE_TANQUE",
                "RESET":"RESET"
            },

        "arduino":
            {
                "S_FREQUENCIA":0,
                "S_PRESSAO":0,
                "S_INVERSOR":"NÃƒO CONECTADO",
                "S_H2S":"",
                "S_RESET INV":"",
                "S_RESET 12V": "",
                "S_BOMBA":"",
                "S_ANALOG VALUE":0,
                "ENVIAR SERIAL":"",
                "STOP TROCA":"",
                "STOP TESTE":""
                },
        "bomba":
            {
                # "ZERA_OPERACOES": "",
                "S_TEMP": "",
                "BOMBA": "",
                "S_REGRESSIVA": "",
                "S_REGRESSIVA": "",
                "S_HORA_OPERACAO": "",
                "NOME": ""
            },
        "acesso_eten":
            {
                "NOME":"",
                "S_PORTA": "NÃƒO CONECTADO",
                "S_PWM": "NÃƒO CONECTADO",
                "S_TAG": "NÃƒO CONECTADO",
                "S_IP": "NÃƒO CONECTADO",
                "S_MAC": "",
                "TESTE": "TESTE",
                "S_TEMPO_OPERACAO": "",
                "LISTA_TAGS": "LISTA_TAGS",
                "ABRE": "FECHA",
                "FECHA": "FECHA",
                "PARA": "PARA",
                "RESET": "RESET",
                "GRAVA_TAG": "GRAVA_TAG"
            },
        "valvula_simples":
            {
                "S_SINAL_WIFI":"",
                "S_TEMPO_OPERACAO":0,
                "S_MAC":"",
                "S_VALVULA":"",
                "S_IP":"",
                "S_CONTA_MOV":"",
                "OPERACOES":"OPERACOES",
                "LOOP":"",
                # "ZERA_OPERACOES":"ZERA_OPERACOES",
                "S_TEMPO_OPERACAO":0,
                "S_VALVULA":"NÃƒO CONECTADO",
                "S_IP":"NÃƒO CONECTADO",
                "NOME":"",
                "ABRE":"ABRE",
                "FECHA":"FECHA",
                "RESET":"RESET"
            },
        "valvula_cabine":
            {
                "S_SINAL_WIFI":"",
                "S_TEMPO_OPERACAO":0,
                "S_MAC":"",
                "S_VALVULA":"",
                "S_IP":"",
                "S_CONTA_MOV":"",
                "LOOP":"",
                # "ZERA_OPERACOES":"ZERA_OPERACOES",
                "NOME":"",
                "ABRE":"ABRE",
                "FECHA":"FECHA",
                "RESET":"RESET",
                "ZERA_M3":"ZERA_M3",
                "DEBUG":"DEBUG"
            },
        "evaporadora":
            {
                "LOOP": "",
                "S_IP": "",
                "S_D_RES": "",
                "S_RES": "",
                "S_TEMP": "",
                "S_COL": "",
                "S_EVAP": "",
                "S_WIFI": "",
                "S_MAC": "",
                "S_FEED": False,
                "S_C_MOV": "",
                "S_T_OP": "NAO INICIADO",
                "S_VAL": "NÃƒO CONECTADO",
                "ABRE": "ABRE",
                "ZERA_OPERACOES": "",
                "FECHA": "FECHA",
                "RESET": "",
                "LIGA_RESISTENCIA": "",
                "DESLIGA_RESISTENCIA": "",
                "NOME": ""
            },
        "evaporadora_sem_valvula":
            {
                "S_NIVEL_EVAPORADOR":"NÃƒO CONECTADO",
                "S_RESISTENCIA":"DESLIGADO",
                "S_DURACAO_RESISTENCIA": "0",
                "S_NIVEL_TANQUE": "",
                "S_IP": "0",
                "RESET": "",
                "LIGA_RESISTENCIA":"LIGA_RESISTENCIA",
                "DESLIGA_RESISTENCIA":"DESLIGA_RESISTENCIA"
            },
        "coletora":
            {
                "S_NIVEL":"NÃƒO CONECTADO",
                "S_BOMBA":"DESLIGADO",
                "S_DURACAO_BOMBA": "0",
                "S_CORRENTE_BOMBA": "0",
                "S_IP":"NÃƒO CONECTADO",
                "LIGA_BOMBA":"LIGA_BOMBA",
                "DESLIGA_BOMBA":"DESLIGA_BOMBA"
            }
    }

for k, v in disp.items():
    disp[k] = json.dumps(v)

newCampo = []
for elements in newCampo:
    if not any(lista in [1, 6] for lista in elements):
        print("tem")