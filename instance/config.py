import os

class Config():
    BOMBEAMENTO_FORCADO = False
    PRESSAO_SCT = 200
    TIME_OUT_SERIAL_PORT = 0
    PORTA_MQTT_LOCAL = 1883
    PORTA_MQTT_SERVER = 1883
    DURACAO_BOMBA_DAGUA = 20
    DURACAO_TROCA_GASOSA = 45
    PRESSAO_IDEAL = -101.
    ANALOG_VALUE = "61"
    CEMITERIO = "MCC LAB"
    REGRESSIVA = 2
    # Credencial para acessar API da Google
    SHEET_AUTH = "MccSheet 26-10-2018-8fe11ab3fb42.json"

    # Titulo da planilha em que o sistema vai usar como modelo
    SHEET_MODEL = "mcc-sheet-model"
    SHEET = "ETEN MCC LAB"
    CELL_TITLE = "A1"

    # Titulos das abas da planilha
    WORKSHEET_TAB1 = "controle"
    WORKSHEET_TAB2 = "dados"
    WORKSHEET_TAB3 = "corpos"

    # Email de compartilhamento da planilha
    EMAIL = "pedrosilva@vilatec.com.br"

    # Numero de referencia da linha para acrecentar novos dados na planilha
    INSERT_ROW = 2

    # Extensao do arquivo local
    FILE_EXTENSION = ".csv"
    FILE_DIVIDER = ";"

    DATE_DIVIDER = "/"
    CLOCK_DIVIDER = ":"

    GMAIL_SCOPES = 'https://www.googleapis.com/auth/gmail.compose'
    GMAIL_SERVICE_AUTH = 'gmail-service-auth.json'
    GMAIL_USER_AUTH = 'gmail-auth-user.json'

    PROJECT_DIR = os.getcwd()
    STATIC_DIR = os.path.join(PROJECT_DIR, "static")
    CREDENTIALS_DIR = os.path.join(PROJECT_DIR, "credentials")
    OPERATIONS_DIR = os.path.join(PROJECT_DIR, "operations")
    OUTPUT_DIR = os.path.join(OPERATIONS_DIR, "output")
    DB_DIR = os.path.join(PROJECT_DIR, "banco")
    # COD_CLIENTE = 'ARN_001'
    COD_CLIENTE = 'ITS_001'
    # COD_CLIENTE = 'CPS_001'
    # COD_CLIENTE = 'BCR_001'
    # COD_CLIENTE = 'STB_001'
    COD_ESTACAO = 'ETEN_001'
