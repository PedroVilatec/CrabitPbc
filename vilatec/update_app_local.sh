
USUARIO="pi"
ENDERECO_SERVIDOR="172.17.2.91"

# Verifique se a chave pública existe no servidor remoto
chave_existe=$(ssh-keygen -l -f ~/.ssh/id_rsa.pub 2>/dev/null | awk '{print $2}')
#echo "Chave pública: $chave_existe"

if ! sudo -u pi bash -c 'test -f ~/.ssh/id_ed25519'; then
    # Gera uma chave SSH Ed25519 com nome de usuário como comentário
    # echo -e "\n" | sudo -u pi bash -c "ssh-keygen -t ed25519 -C 'raspberry@exemplo.com'"
    echo -e "\n" | sudo -u pi bash -c "ssh-keygen -t ed25519 -N '' -C 'raspberry@exemplo.com'"
    # Verifica se a chave foi criada com sucesso
    if [ $? -eq 0 ]; then
        echo "Chave SSH Ed25519 gerada com sucesso em /home/pi/.ssh/id_ed25519"
    else
        echo "Falha ao gerar a chave SSH Ed25519"
        exit 1
    fi
fi
# Verifique se a chave pública existe no servidor remoto
pubkey=$(cat /home/pi/.ssh/id_ed25519.pub)

if ! sudo -u pi ssh pi@$ENDERECO_SERVIDOR "grep '$pubkey' /home/pi/.ssh/authorized_keys" > /dev/null; then
    echo "Chave ssh não existe, copiando..."
    sudo -u pi ssh-copy-id pi@b8950bd6c40e.sn.mynetname.net

fi

sudo -u pi bash -c "ssh -T pi@$ENDERECO_SERVIDOR 'cd /home/pi/Crabit/vilatec && git pull'"
sudo -u pi rsync -avu --delete --exclude="*frp*" --exclude="*libraries*" --exclude="*.pyc" --exclude="__init__.py" --exclude="__pycache__" pi@$ENDERECO_SERVIDOR:Crabit/vilatec /home/pi/Crabit/
sudo cp /home/pi/Crabit/vilatec/update_app.sh /bin/update_app
grep -q -e 'PORTA_MQTT_SERVER' /home/pi/Crabit/instance/config.py || sed -i.bak '/class Config():/a \ \ \ \ PORTA_MQTT_SERVER = 1883' /home/pi/Crabit/instance/config.py
grep -q -e 'PORTA_MQTT_LOCAL' /home/pi/Crabit/instance/config.py || sed -i.bak '/class Config():/a \ \ \ \ PORTA_MQTT_LOCAL = 1883' /home/pi/Crabit/instance/config.py
grep -q -e 'TIME_OUT_SERIAL_PORT' /home/pi/Crabit/instance/config.py || sed -i.bak '/class Config():/a \ \ \ \ TIME_OUT_SERIAL_PORT = 1' /home/pi/Crabit/instance/config.py
grep -q -e 'PRESSAO_SCT' /home/pi/Crabit/instance/config.py || sed -i.bak '/class Config():/a \ \ \ \ PRESSAO_SCT = 200' /home/pi/Crabit/instance/config.py
grep -q -e 'DATA_MANU' /home/pi/Crabit/instance/config.py || sed -i.bak '/class Config():/a \ \ \ \ DATA_MANU = "08/09/2020"' /home/pi/Crabit/instance/config.py
grep -q -e 'PRAZO_MANU' /home/pi/Crabit/instance/config.py || sed -i.bak '/class Config():/a \ \ \ \ PRAZO_MANU = 8' /home/pi/Crabit/instance/config.py
grep -q -e 'DESABILITADO' /home/pi/Crabit/instance/config.py || sed -i.bak '/class Config():/a \ \ \ \ DESABILITADO = [] # ex:  ["VALVULA_CABINE", "VALVULA_AM_1"]' /home/pi/Crabit/instance/config.py
sed -i '/nivel_tanque =/d;/arduino =/d;/bomba =/d;/valvula_cabine =/d;/acesso_eten =/d;/valvula_simples =/d;/evaporadora =/d;/evaporadora_sem_valvula =/d;/coletora =/d' /home/pi/Crabit/instance/devices.py
grep -q -e 'import atributos' /home/pi/Crabit/instance/devices.py || sed -i.bak '/import json/a import atributos' /home/pi/Crabit/instance/devices.py
grep -q -e 'locals().update(atributos.disp)' /home/pi/Crabit/instance/devices.py || sed -i.bak '/import atributos/a locals().update(atributos.disp)' /home/pi/Crabit/instance/devices.py

config_file="/etc/openvpn/client.conf"










#grep -q -e 'def __init__' /home/pi/Crabit/instance/devices.py || sed -i.bak '/class Devices():/a \ \ \ \ def __init__(self, atributos):' /home/pi/Crabit/instance/devices.py
# sudo grep -q -e 'vncserver' /etc/rc.local || sudo sed -i.bak '/fi/a vncserver -geometry 1600x1200 -randr 1600x1200,1440x900,1024x768' /etc/rc.local

# sudo grep -q -e 'python3 /home/pi/Crabit/vilatec/util/MONITOR_SERIAL.py' /bin/start_monitor || sudo echo -e 'python3 /home/pi/Crabit/vilatec/util/MONITOR_SERIAL.py'> /bin/start_monitor
# sudo grep -q -e 'sudo killall gunicorn\nsudo gunicorn --worker-class eventlet -w 1 --reload --chdir /home/pi/Crabit/vilatec app:app' /bin/start_app || sudo echo -e 'sudo killall gunicorn\nsudo gunicorn --worker-class eventlet -w 1 --reload --chdir /home/pi/Crabit/vilatec app:app'> /bin/start_app
# sudo grep -q -e 'python3 /home/pi/Crabit/vilatec/mqtt_mcc.py' /bin/start_mqtt || sudo echo -e 'python3 /home/pi/Crabit/vilatec/mqtt_mcc.py'> /bin/start_mqtt
# sudo grep -q -e 'python3 /home/pi/Crabit/vilatec/webView.py' /bin/start_webview || sudo echo 'python3 /home/pi/Crabit/vilatec/webView.py'> /bin/start_webview
# sudo chmod +x /bin/start_webview
sudo cp /home/pi/Crabit/vilatec/remove_backup.sh /bin/remove_backup
sudo chmod +x /bin/remove_backup
sudo chmod +x /home/pi/Crabit/vilatec/update_app_local.sh
# sudo cp /home/pi/Crabit/vilatec/read_esp.sh /bin/read_esp
# sudo cp /home/pi/Crabit/vilatec/conf_esp.sh /bin/conf_esp
# sudo cp /home/pi/Crabit/vilatec/ip_esp.sh /bin/ip_esp
# sudo chmod +x /bin/start_monitor /bin/start_app /bin/start_mqtt /bin/update_app /bin/conf_esp /bin/read_esp /bin/ip_esp
sudo chown pi:pi -R /home/pi/Crabit/instance

#service frps start #sistema de acesso remoto
exit 0
