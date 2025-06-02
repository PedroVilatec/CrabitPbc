sudo nmap -sP 192.168.0.0/24 | awk '/Nmap scan report for/{printf $5;}/MAC Address:/{print "-"$3;}' | while read line;
do

IFS=- read var1 var2 <<< $line;
#~ echo -n -e "Escaneando $var1 mac $1\r";

if [ "$var2" == "$1" ]; then
    echo -e "IP $var1 MAC $var2";
    break
fi
done


