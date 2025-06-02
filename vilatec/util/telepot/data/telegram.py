import os
import telepot
cemiterio = "CORTEL_1E"
user_file = "users_telepot.py"
bots = "bots.py"
bot_file = os.path.join(os.path.dirname(__file__), bots)
read_user = os.path.join(os.path.dirname(__file__), user_file)
with open(bot_file) as g:
	for line in g:
		line = line.rstrip()
		if cemiterio in line:                   
			if line.split("=",1)[1] != "":
				print(line.split("=",1)[1])
				endereco = line.split("=",1)[1]
				try:
					bot = telepot.Bot(endereco)
				except:
					pass

def bot_send(cemiterio, mensagem):
	with open(read_user) as f:
		for line in f:
			try:
				if not "#" in line:
					line = line.rstrip()
					print(line.split("=",1)[1])

					endereco = line.split("=",1)[1]
					bot.sendMessage(endereco,mensagem)
		
			except Exception as err:
				print(err)
				print("erroTelegram")
		
def recebendoMsg(msg):
	print("recebido")
	bot_send("ALAMEDA DAS IRMANDADES", msg['text'])

	
bot.message_loop(recebendoMsg)
bot_send("ALAMEDA DAS IRMANDADES", "TESTE")


	

