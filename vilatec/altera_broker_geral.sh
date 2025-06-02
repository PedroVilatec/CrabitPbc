LOCAL_IP=$(ip route | grep src | awk -F 'dev eth0 proto kernel scope link' '{print $NF; exit}' | awk '{print $3}')
attrib="/24"
command_out=$(sudo nmap --help 2>&1 )
command_rc=$?
if [[ $command_rc -eq 0 ]]; then
	echo "Alterando servidor e porta dos dispositivos"
    # echo "Comando: sudo nmap -sP $LOCAL_IP$attrib"
else
    echo "Nmap não encontrado. Aguarde a instalação"
	sudo apt-get update -y
    sudo apt-get install nmap
    sudo apt autoremove
fi
sudo nmap -sP $LOCAL_IP$attrib | awk '/Nmap scan report for/{printf $5;}/MAC Address:/{print "-"$3;}' | while read line;

do
IFS=- read var1 var2 <<< $line;
# echo"$var1 $var2"

#if [ "$var2" == "$1" ]; then
    server=$HOSTNAME
    port=1884
    cmd="/mqtt?server=$1&port=$2";
    echo "Server = $1 Porta = $2"
    echo $var1
    curl  -m 5 -sb -H "$var1$cmd";

    # cmd="/readMsg";
    # echo "IP = $var1";
    # curl -m 5 -sb -H "$var1$cmd";
    # echo ""
    #break;
#fi
done


