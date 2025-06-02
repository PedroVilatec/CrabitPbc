#!/bin/bash

# # Verifica se o arquivo de serviço já existe
if [ -f "/etc/systemd/system/frpc.service" ]; then
    echo "O arquivo de serviço frpc já existe. Não é necessário prosseguir."
    exit 0
fi

# # Define a versão desejada do frp
VERSION="v0.51.0"

# # URL para download do frp
URL="https://github.com/fatedier/frp/releases/download/$VERSION/frp_$VERSION\_linux_arm.tar.gz"

# # Nome do arquivo compactado
FILENAME="frp_$VERSION\_linux_arm.tar.gz"

# # Caminho para extrair os arquivos
EXTRACT_DIR="/etc/frp"

# # Caminho para o arquivo de configuração frpc.ini
CONFIG_FILE="/home/pi/Crabit/instance/frpc.ini"

# Baixa o frp
echo "Baixando o frp..."
wget "$URL" -O "$FILENAME"

# Extrai os arquivos
echo "Extraindo os arquivos..."
mkdir -p "$EXTRACT_DIR"
tar -xzf "$FILENAME" -C "$EXTRACT_DIR" --strip-components=1

# Remove o arquivo compactado
rm "$FILENAME"

# Criação do arquivo de serviço frpc
echo "Criando o arquivo de serviço frpc..."
cat << EOF | sudo tee /etc/systemd/system/frpc.service
[Unit]
Description=frpc service
After=network.target
Wants=network-online.target
After=network-online.target


[Service]
TimeoutStartSec=300
ExecStart=frpc -c $CONFIG_FILE

[Install]
WantedBy=default.target
EOF

# Recarrega a configuração do systemd
sudo systemctl daemon-reload

# Inicia e habilita o serviço frpc
sudo systemctl start frpc
sudo systemctl enable frpc.service


echo "A instalação do frpc foi concluída!"


# Verifica se o cliente MySQL está instalado
if ! command -v mysql &> /dev/null; then
    echo "Cliente MySQL não encontrado. Instalando o pacote mysql-client..."
    sudo apt-get update
    sudo apt-get install mysql-client -y
fi

#!/bin/bash

# Verifica se o cliente MySQL está instalado
if ! command -v mysql &> /dev/null; then
    echo "Cliente MySQL não encontrado. Instalando o pacote mysql-client..."
    sudo apt-get update
    sudo apt-get install mysql-client -y
fi

# Verifica se o cliente MySQL está instalado
if ! command -v mysql &> /dev/null; then
    echo "Cliente MySQL não encontrado. Instalando o pacote mysql-client..."
    sudo apt-get update
    sudo apt-get install mysql-client -y
fi

# Configurações do banco de dados
DB_HOST="191.234.200.55"
DB_PORT="3306"
DB_USER="evolution"
DB_PASSWORD="nbr5410!"
DB_NAME="frp_database"

# Consulta o último lançamento de nome e remote_port
QUERY="SELECT name, remote_port FROM port_mapping ORDER BY id DESC LIMIT 1"
LAST_ENTRY=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -D "$DB_NAME" -se "$QUERY")

echo "Último lançamento: $LAST_ENTRY"
