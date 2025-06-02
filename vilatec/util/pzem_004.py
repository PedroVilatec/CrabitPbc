#!/usr/bin/env python3
#coding=utf-8

import serial
import serial.tools.list_ports
import time
import struct
import threading

class BTPOWER:

	setAddrBytes 		=	[0xB4,0xC0,0xA8,0x01,0x01,0x00,0x1E]
	readVoltageBytes 	= 	[0xB0,0xC0,0xA8,0x01,0x01,0x00,0x1A]
	readCurrentBytes 	= 	[0XB1,0xC0,0xA8,0x01,0x01,0x00,0x1B]
	readPowerBytes 		= 	[0XB2,0xC0,0xA8,0x01,0x01,0x00,0x1C]
	readRegPowerBytes 	= 	[0XB3,0xC0,0xA8,0x01,0x01,0x00,0x1D]

	def __init__(self):
		self.values={"voltagem":None, "corrente":None, "potencia":None, "consumo":None}
		self.counter_wrong_checksum = 0

	def checkChecksum(self, _tuple):
		_list = list(_tuple)
		_checksum = _list[-1]
		_list.pop()
		_sum = sum(_list)
		if _checksum == _sum%256:
			self.counter_wrong_checksum = 0
			return True
		else:
			self.counter_wrong_checksum += 1
			if self.counter_wrong_checksum > 10:
				self.counter_wrong_checksum = 0
				print("Wrong checksum")

	def find_serial_port(self, short_name):
		ports = serial.tools.list_ports.comports()
		for port in ports:
			if short_name in port.device:
				return port.device
		return None

	def serial_port(self, comPort):
		full_port_name = self.find_serial_port(comPort)
		if full_port_name:
			self.ser = serial.Serial(
				port=full_port_name,
				baudrate=9600,
				parity=serial.PARITY_NONE,
				stopbits=serial.STOPBITS_ONE,
				bytesize=serial.EIGHTBITS,
				timeout = 10
			)
			if self.ser.is_open:
				self.ser.close()
			self.ser.open()
			read = threading.Thread(target = self.readThread)
			read.start()
		else:
			print("Porta serial não identificada")

	def isReady(self):
		if self.ser.is_open:
			self.ser.write(serial.to_bytes(self.setAddrBytes))
			rcv = self.ser.read(7)
			if len(rcv) == 7:
				unpacked = struct.unpack("!7B", rcv)
				if(self.checkChecksum(unpacked)):
					return True

			print("Timeout setting address Pzem")
			return False
		else:
			return False

	def readVoltage(self):
		if self.ser.is_open:
			self.ser.write(serial.to_bytes(self.readVoltageBytes))
			rcv = self.ser.read(7)
			# print("RVC vcc", rcv)
			if len(rcv) == 7:
				unpacked = struct.unpack("!7B", rcv)
				if(self.checkChecksum(unpacked)):
					tension = unpacked[2]+unpacked[3]/10.0
					return tension

		print("Timeout reading tension")
		return None

	def readCurrent(self):
		if self.ser.is_open:
			self.ser.write(serial.to_bytes(self.readCurrentBytes))
			rcv = self.ser.read(7)
			# print("RVC current", rcv)
			if len(rcv) == 7:
				unpacked = struct.unpack("!7B", rcv)
				if(self.checkChecksum(unpacked)):
					current = unpacked[2]+unpacked[3]/100.0
					return current

		print("Timeout reading current")
		return None

	def readPower(self):
		if self.ser.is_open:
			self.ser.write(serial.to_bytes(self.readPowerBytes))
			rcv = self.ser.read(7)
			# print("RVC power", rcv)
			if len(rcv) == 7:
				unpacked = struct.unpack("!7B", rcv)
				if(self.checkChecksum(unpacked)):
					power = unpacked[1]*256+unpacked[2]
					return power

		print("Timeout reading power")
		return None

	def readRegPower(self):
		if self.ser.is_open:
			self.ser.write(serial.to_bytes(self.readRegPowerBytes))
			rcv = self.ser.read(7)
			# print("RVC consumo", rcv)
			if len(rcv) == 7:
				unpacked = struct.unpack("!7B", rcv)
				if(self.checkChecksum(unpacked)):
					regPower = unpacked[1]*256*256+unpacked[2]*256+unpacked[3]
					return regPower

		print("Timeout reading registered power")
		return None

	def readAll(self):
		if(self.isReady()):
			# ~ print("ready")
			volts = self.readVoltage()
			# ~ print("v", volts)
			corrente = self.readCurrent()
			# ~ print("c", corrente)
			potencia = self.readPower()
			# ~ print("p", potencia)
			consumo = self.readRegPower()
			# ~ print("cons", consumo)
			if volts is not None: self.values["voltagem"] = volts
			else: self.values["voltagem"] = None
			if corrente is not None: self.values["corrente"] = corrente
			else: self.values["corrente"] = None
			if potencia is not None: self.values["potencia"] = potencia
			else: self.values["potencia"] = None
			if consumo is not None: self.values["consumo"] = consumo
			else: self.values["consumo"] = None
			# print(time.time())


	def close(self):
		self.ser.close()

	def readThread(self):
		while True:
			self.readAll()
			time.sleep(2.5)
