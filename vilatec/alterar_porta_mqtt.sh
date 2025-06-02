if [ -z  $1 ]; then
    echo "Informe a porta mqtt"
    echo "Ex. $0 1889"
    done
else
    touch /etc/mosquitto/conf.d/mosquitto.conf
    sudo chown pi:pi -R /etc/mosquitto/conf.d/mosquitto.conf
    echo "allow_anonymous true" >> /etc/mosquitto/conf.d/mosquitto.conf
    echo "listener $1" >> /etc/mosquitto/conf.d/mosquitto.conf
    echo "Porta = $1"
fi
done


