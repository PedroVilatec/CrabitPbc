# -*- coding: utf-8 -*-
versao = "1.0"
import sys, os, repackage
repackage.up()
#~ import pyautogui
import linecache
from infra.lib_sensors_db import get_sensors_id
from instance.config import Config
from instance.devices import Devices
from operations.mqtt import Mosquitto, MosquittoServer
from operations.pzem_004 import BTPOWER
from operations.sheet import Sheet
from operations.telegram import Bot
from operations import saveFile
from operations.op_facade import setTime, updateData, alertEmail, dailyEmail
from infra.raspserial import getSerial
from infra.check_internet import have_internet
import json
import serial
import serial.tools.list_ports
import sqlite3
import datetime
import schedule
import time

from operations import dict_disp


a = Devices(**dict_disp.dispositivos)
print(a.CONTROLADORES)
