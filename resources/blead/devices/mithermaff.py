from bluepy import btle
import time
import logging
import globals
import struct
from multiconnect import Connector
from notification import Notification

class Mithermaff():
	def __init__(self):
		self.name = 'mithermaff'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf=''):
		validname = ['Flower mate','Flower care']
		if name in validname:
			return True
	def parse(self,data,mac,name):
		action={}
		action['present'] = 1
		return action

	def read(self,mac):
		result={}
		try:
			conn = Connector(mac)
			conn.connect()
			if not conn.isconnected:
				conn.connect()
				if not conn.isconnected:
					return
					
			logging.debug('read batteryFirm')
			batteryFirm = bytearray(conn.readCharacteristic('0x18'))
			battery = batteryFirm[0]
			firmware = "".join(map(chr, batteryFirm[2:]))
			notification = Notification(conn,Mithermaff)
			logging.debug('write 0x10 0100 to get sensor values')
			conn.writeCharacteristic('0x10','0100',response=True)
			notification.subscribe(2)
			result['battery'] = battery
			result['firmware'] = firmware
			result['id'] = mac
			logging.debug(str(result))
			return result
		except Exception,e:
			logging.error(str(e))
		return result
	
	def handlenotification(self,conn,handle,data,action={}):
		result={}
		logging.debug('handlenotification')
		if hex(handle) == '0xe':
			received = bytearray(data)
			temperature = float(received[2:6])
			humidity = float(received[9:13])
			result['humidity'] = humidity
			result['temperature'] = temperature
			result['id'] = conn.mac
			result['source'] = globals.daemonname
			globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)

globals.COMPATIBILITY.append(Mithermaff)
