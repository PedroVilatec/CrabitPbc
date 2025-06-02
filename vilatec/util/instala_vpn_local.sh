#!/bin/bash

# sudo scp pi@172.17.2.91:Crabit/vilatec/util/instala_vpn.sh capela/ihm/util/
# Verifique se o script está sendo executado como root (ou com privilégios de superusuário)
if [[ $EUID -ne 0 ]]; then
    echo "Este script precisa ser executado como root."
    exit 1
fi
# Lista de pacotes a serem desinstalados
pacotes=("bluej" "greenfoot" "wolfram-engine" "nodered" "scratch" "scratch2" "scratch3" "sonic-pi" "libreoffice")

# Função para verificar se um pacote está instalado
pacote_instalado() {
  if dpkg -s "$1" &>/dev/null; then
    return 0  # Retorna 0 se o pacote estiver instalado
  else
    return 1  # Retorna 1 se o pacote não estiver instalado
  fi
}

# Loop para desinstalar os pacotes existentes
for pacote in "${pacotes[@]}"; do
  if pacote_instalado "$pacote"; then
    echo "Desinstalando $pacote..."
    sudo apt-get remove -y "$pacote"

  fi
done


# Executa o autoremove para remover dependências não utilizadas
sudo apt-get autoremove -y

sudo apt-get update #--allow-releaseinfo-change

sudo apt-get upgrade -y
# Verifica se o pacote openvpn está instalado
if ! dpkg -s openvpn &> /dev/null; then
    echo "Pacote openvpn não encontrado. Instalando..."
    # Comando para instalar o pacote
    sudo apt-get install -y openvpn
    echo "Pacote instalado com sucesso!"
fi
sudo apt-get autoremove
# Verifica se o pacote openvpn-systemd-resolved está instalado
if ! dpkg -s openvpn-systemd-resolved &> /dev/null; then
    echo "Pacote openvpn-systemd-resolved não encontrado. Instalando..."
    # Comando para instalar o pacote
    sudo apt-get install -y openvpn-systemd-resolved
    echo "Pacote instalado com sucesso!"
fi


# Verifica se a chave SSH já existe
if ! sudo -u pi bash -c 'test -f ~/.ssh/id_ed25519'; then
    # Gera uma chave SSH Ed25519 com nome de usuário como comentário
    # echo -e "\n" | sudo -u pi bash -c "ssh-keygen -t ed25519 -C 'raspberry@exemplo.com'"
    echo -e "\n" | sudo -u pi bash -c "ssh-keygen -t ed25519 -N '' -C 'raspberry@exemplo.com'"

fi

# Verifica se a chave foi criada com sucesso
if [ $? -eq 0 ]; then
    echo "Chave SSH Ed25519 gerada com sucesso em /home/pi/.ssh/id_ed25519"
else
    echo "Falha ao gerar a chave SSH Ed25519"
    exit 1
fi

echo "Copiando a chave pública para o servidor intermediário 172.17.2.91"
sudo -u pi bash -c 'ssh-copy-id pi@172.17.2.91'

# Solicita ao usuário para inserir o valor do campo
read -p "Digite o nome de acesso do cliente: " campo

# Comando remoto para o servidor intermediário 172.17.2.91, passando o valor de "campo"
cmd="./cria_credenciais.sh ${campo}"
sudo -u pi bash -c "ssh pi@172.17.2.91 'ssh -T pi@10.8.0.1 ${cmd}'"

# Comando remoto para o servidor intermediário 172.17.2.91, usando diretamente o valor de "campo"
sudo -u pi bash -c "ssh pi@172.17.2.91 'cd /home/pi/vpn && git pull'"


# Monta o comando scp com o campo fornecido pelo usuário
cd /etc/openvpn
comando_scp="scp -i /home/pi/.ssh/id_ed25519 pi@172.17.2.91:vpn/${campo}/*.* ."
$comando_scp
# comando_scp="scp -i /home/pi/.ssh/id_ed25519 pi@172.17.2.91:/home/pi/vpn/${campo}/*.* ."
# Executa o comando como root
#sudo bash -c "$comando_scp"


echo "Criando serviço de inicialização"
# Conteúdo do arquivo openvpn-client.service
SERVICE_CONTENT="[Unit]
Description=OpenVPN client
After=network.target

[Service]
Type=simple
ExecStart=/usr/sbin/openvpn --config /etc/openvpn/client.conf

[Install]
WantedBy=multi-user.target"

# Caminho para o arquivo de serviço
SERVICE_FILE="/etc/systemd/system/openvpn-client.service"

# Escreva o conteúdo no arquivo de serviço
echo "$SERVICE_CONTENT" > "$SERVICE_FILE"

# Dê permissões corretas para o arquivo
chmod 644 "$SERVICE_FILE"

# Recarregue os serviços do systemd
systemctl daemon-reload
#systemctl restart openvpn@client.service
echo "Arquivo /etc/systemd/system/openvpn-client.service criado com sucesso."

