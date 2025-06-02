# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import serial.tools.list_ports

def upload_hex_to_arduino(avrdude_path, mcu, programmer, port, baudrate, hex_file):
    avrdude_command = [
        avrdude_path,
        '-v',
        '-p', mcu,
        '-c', programmer,
        '-P', port,
        '-b', baudrate,
        '-D',
        '-U', f'flash:w:{hex_file}:i'
    ]
    try:
        process = subprocess.Popen(avrdude_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while process.poll() is None:
            output = process.stdout.read(1)
            print(output.decode(errors='ignore'), end='')
    except subprocess.CalledProcessError as e:
        print(e.stderr.decode())
        print("Erro ao enviar o arquivo binário.")

def listar_portas_seriais():
    portas = list(serial.tools.list_ports.comports())
    if not portas:
        print("Nenhuma porta serial encontrada.")
        sys.exit(1)
    return portas

def escolher_opcao(lista, titulo):
    print(f"\nEscolha {titulo}:")
    for i, item in enumerate(lista):
        print(f"{i + 1}: {item}")
    while True:
        try:
            escolha = int(input("Digite o número correspondente: "))
            if 1 <= escolha <= len(lista):
                return lista[escolha - 1]
            else:
                print("Número inválido.")
        except ValueError:
            print("Digite um número.")

def main():
    hex_file_path = os.path.expanduser('/home/pi/Crabit/vilatec/MCC_MQTT_RESET_CALIBRA_FACIL/build/arduino.avr.nano/MCC_MQTT_RESET_CALIBRA_FACIL.ino.hex')
    avrdude_path = 'avrdude'
    mcu = 'atmega328p'
    programmer = 'arduino'

    # Selecionar porta serial
    portas = listar_portas_seriais()
    porta = escolher_opcao([p.device for p in portas], "a porta serial")

    # Selecionar bootloader
    bootloaders = {
        "Bootloader Antigo (57600)": "57600",
        "Bootloader Novo (115200)": "115200"
    }
    bootloader_nome = escolher_opcao(list(bootloaders.keys()), "o tipo de bootloader")
    baudrate = bootloaders[bootloader_nome]

    upload_hex_to_arduino(avrdude_path, mcu, programmer, porta, baudrate, hex_file_path)

if __name__ == "__main__":
    main()
