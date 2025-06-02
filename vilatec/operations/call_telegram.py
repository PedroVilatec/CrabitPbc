from telegram import Bot
import time

telegram_bot = Bot("ALAMEDA DAS IRMANDADES")
try:
	telegram_bot.envia_telegram_pressao()
except Exception as e:
	print(e)
def mensagemFromBot(mensagem):
	print("MENSAGEM ",mensagem)
telegram_bot.ret_telepot(mensagemFromBot)
while True:

	time.sleep(5)
	#print("Loop")

