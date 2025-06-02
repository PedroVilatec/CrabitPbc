LOCAL_IP=$(ip route | grep src | awk -F 'dev eth0 proto kernel scope link' '{print $NF; exit}' | awk '{print $3}')
attrib="/24"
command_out=$(sudo nmap --help 2>&1 )
command_rc=$?
if [[ $command_rc -eq 0 ]]; then
	echo "Procurando esp com o mac $1"
    echo "Comando: sudo nmap -sP $LOCAL_IP$attrib"
else
    echo "Nmap não encontrado. Aguarde a instalação"
	sudo apt-get update -y
    sudo apt-get install nmap
    sudo apt autoremove
fi
sudo nmap -sP $LOCAL_IP$attrib | awk '/Nmap scan report for/{printf $5;}/MAC Address:/{print "-"$3;}' | while read line;

do
IFS=- read var1 var2 <<< $line;
echo"$var1 $var2"

if [ "$var2" == "$1" ]; then
    # server=$HOSTNAME
    # port=1883
    # cmd="/mqtt?server=$server&port=$port";
    # echo "Server = $server Porta = $port"
    # echo $var1
    # curl  -m 5 -sb -H "$var1$cmd";

    cmd="/readMsg";
    echo "IP = $var1 MAC = $var2";
    curl -m 5 -sb -H "$var1$cmd";
    echo ""
    break;
fi
done


