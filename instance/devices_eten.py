class Devices():
    comando = {"REINIAR APP":"",
    "TESTE":"",
     "TROCA GASOSA":"",
      "ENVIAR SERIAL":"",
      "COMANDO SHELL":"",
      "GET INSTANCE":'''sudo sshpass -p nbr5410! rsync -avu --delete --exclude="*.pyc" --exclude="__init__.py" --exclude="__pycache__" /home/pi/Crabit/instance/ 'pi@10.10.0.1:INSTANCE_ETENS/{}' ''',
      "PUT INSTANCE":'''sudo chown pi:pi -R /home/pi/Crabit && sudo sshpass -p nbr5410! rsync -avu --delete --exclude="*.pyc" --exclude="__init__.py" --exclude="__pycache__" 'pi@10.10.0.1:INSTANCE_ETENS/{}/ ' /home/pi/Crabit/instance/ ''',

     "UPDATE":'''sudo sshpass -p nbr5410! rsync -avu --delete --exclude="*.pyc" --exclude="__init__.py" --exclude="__pycache__" pi@10.10.0.1:Crabit/Eten_vilatec/vilatec /home/pi/Crabit/ && sudo chown pi:pi -R /home/pi/Crabit && sudo /home/pi/Crabit/vilatec/update_app.sh'''}

    CONTROLADORES = {
"CAMPO SANTO": comando,
"ALAMEDA DAS IRMANDADES": comando,
"SANTA BARBARA": comando,
"DESCANSO ETERNO": comando,
"CEMITERIO VIDA": comando,
"MORADA 2": comando,
"CORTEL_1E": comando,
"MCC_CORTEL_2E": comando,
"ESAB_ALAGOINHAS": comando,
"ETEN SAO PEDRO":comando,
"MCC SAO GONCALO": comando,
"MCC PETROLINA": comando,
"MCC IGUATU": comando,
"MCC GUARABIRA": comando,
"PARQUE DAS FLORES 1": comando,
"SANTO AMARO EMLURB": comando,
"NOVO HAMBURGO 1":comando,
"MCC LAB": comando
}

