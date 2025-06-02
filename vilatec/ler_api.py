import repackage
repackage.up()
from vilatec.operations.integracao import registrar, enviar, ler
import time

from instance.config import Config
try:
    inicio = time.time()
    dict = {"codigo_cliente": Config.COD_CLIENTE, "codigo_estacao_tratamento": Config.COD_ESTACAO}
    lido = ler("LER_CONFIG", dict)
    print("RETORNO API", lido)
except Exception as e:
    print(e)