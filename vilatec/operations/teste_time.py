import time
import datetime

def tempo_passado(tempo):
    segundos = round(time.time()) - tempo
    dias = round(segundos / 86400)
    minutos = round((segundos % 3600)) // 60
    hora = round(segundos // 3600) % 24
    segundos = round(segundos % 60)
    return "{}dias {:0>2}:{:0>2}:{:0>2}".format(dias, hora, minutos, segundos)

agora = time.time()
passado = agora - 126
print(agora)
print(passado)
print(tempo_passado(passado))

print(round(66 % 60))