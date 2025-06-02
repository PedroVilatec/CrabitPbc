#!/usr/bin/env python3
#coding=utf-8

import serial
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
		self.values={"voltagem":0, "corrente":0, "potencia":0, "consumo":0}
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

	def serial_port(self, comPort):
		self.ser = serial.Serial(
			port=comPort,
			baudrate=9600,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			bytesize=serial.EIGHTBITS,
			timeout = 10
		)
		if self.ser.isOpen():
			self.ser.close()
		self.ser.open()
		read = threading.Thread(target = self.readThread)
		read.start()

	def isReady(self):
		self.ser.write(serial.to_bytes(self.setAddrBytes))
		rcv = self.ser.read(7)
		if len(rcv) == 7:
			unpacked = struct.unpack("!7B", rcv)
			if(self.checkChecksum(unpacked)):
				return True
		else:
			print("Timeout setting address Pzem")

	def readVoltage(self):
		self.ser.write(serial.to_bytes(self.readVoltageBytes))
		rcv = self.ser.read(7)
		if len(rcv) == 7:
			unpacked = struct.unpack("!7B", rcv)
			if(self.checkChecksum(unpacked)):
				tension = unpacked[2]+unpacked[3]/10.0
				return tension
		else:
			print("Timeout reading tension")

	def readCurrent(self):
		self.ser.write(serial.to_bytes(self.readCurrentBytes))
		rcv = self.ser.read(7)
		if len(rcv) == 7:
			unpacked = struct.unpack("!7B", rcv)
			if(self.checkChecksum(unpacked)):
				current = unpacked[2]+unpacked[3]/100.0
				return current
		else:
			print("Timeout reading current")

	def readPower(self):
		self.ser.write(serial.to_bytes(self.readPowerBytes))
		rcv = self.ser.read(7)
		if len(rcv) == 7:
			unpacked = struct.unpack("!7B", rcv)
			if(self.checkChecksum(unpacked)):
				power = unpacked[1]*256+unpacked[2]
				return power
		else:
			print("Timeout reading power")

	def readRegPower(self):
		self.ser.write(serial.to_bytes(self.readRegPowerBytes))
		rcv = self.ser.read(7)
		if len(rcv) == 7:
			unpacked = struct.unpack("!7B", rcv)
			if(self.checkChecksum(unpacked)):
				regPower = unpacked[1]*256*256+unpacked[2]*256+unpacked[3]
				return regPower
		else:
			print("Timeout reading registered power")

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
			if corrente is not None: self.values["corrente"] = corrente
			if potencia is not None: self.values["potencia"] = potencia
			if consumo is not None: self.values["consumo"] = consumo
			# print(time.time())

	def close(self):
		self.ser.close()

	def readThread(self):
		while True:
			self.readAll()
			time.sleep(2.5)
