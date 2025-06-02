andar = int(input("QUAL O NUMERO DO ANDAR ? "))
bloco = int(input("QUAL O NUMERO DO BLOCO ? "))
colunas = int(input("TOTAL DE COLUNAS ? "))
for a in range(2, colunas, 2):
	for b in range(1, 5):
		print("{}.0{}.{}.{}".format(andar, bloco, b, a))

for a in range(1, colunas, 2):
	for b in range(1, 5):
		print("{}.0{}.{}.{}".format(andar, bloco, b, a))