LOCAL_IP=$(ip route | grep src | awk -F 'dev eth0 proto kernel scope link' '{print $NF; exit}' | awk '{print $3}')
attrib="/24"
sudo nmap -sP $LOCAL_IP$attrib | awk '/Nmap scan report for/{printf $5;}/MAC Address:/{print "-"$3;}' | while read line;
do
IFS=- read var1 var2 <<< $line;
#~ echo -n -e "\nEscaneando $var1 mac $var2\r";

if [ "$var2" == "$1" ]; then
    if [ !  -z  $2 ]; then
      port=$2
    else
        port="1883"
    fi
    server=$HOSTNAME
    cmd="/mqtt?server=$server&port=$port";
    echo "Server = $server Porta = $port"
    echo $var1
    curl  -m 5 -sb -H "$var1$cmd";
    #curl  -m 5 -sb -H 192.168.1.101/mqtt?server=MCC.local&porta=1883

    break
fi

done

if [ !  -z  $cmd ]; then
  echo "MAC encontrado - $var2"
else
    echo -e "Mac nao encontrado - $LOCAL_IP$attrib"
fi

