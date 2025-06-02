#!/bin/bash

# Solicita o nome da unidade ETEN ao usuário
read -p "Digite o nome da unidade ETEN (ex: itapevi_eten 2): " INPUT

# Formata: adiciona "evo-" no início e substitui espaço/underline por hífen
FORMATTED_NAME="evo-$(echo "$INPUT" | tr '[:upper:]' '[:lower:]' | sed -E 's/[ _]+/-/g')"

echo "Nome formatado: $FORMATTED_NAME"

# Executa o script remoto via SSH e baixa o .ovpn via SCP
ssh pi@170.79.168.234 "bash /home/pi/cria_credenciais_vpn_2.sh $FORMATTED_NAME" && \
sudo scp pi@170.79.168.234:/home/pi/openvpn-clients/${FORMATTED_NAME}.ovpn /etc/openvpn/${FORMATTED_NAME}.conf

echo "Arquivo ${FORMATTED_NAME}.conf baixado com sucesso."



