import subprocess
import sys

# Executa o comando hostname -I para obter a lista de IPs
try:
    result = subprocess.run(["hostname", "-I"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    ip_list = result.stdout.strip().split()
except Exception as e:
    print("Erro ao executar o comando: {}".format(e))
    # sys.exit(1)

# Variável para armazenar o IP que inicia com "10.8.0."
target_ip = None

# Loop para verificar cada IP da lista
for ip in ip_list:
    if ip.startswith("10.8.0."):
        target_ip = ip
        break  # Encerra o loop se encontrar o IP desejado

# Se não encontrou IP que inicie com "10.8.0.*", atribui o primeiro IP da lista à variável
if not target_ip and ip_list:
    target_ip = ip_list[0]

# Imprime o IP encontrado ou o primeiro IP da lista
print("IP selecionado:", target_ip)
