#!/usr/bin/env python2.7
# vim:ts=4:sw=4:

from time import time

from snmppass.passthrough import Passthrough, Handler
from tellcore.telldus import TelldusCore, Sensor

base='.1.3.6.1.4.1.8072.9999.9999.1'

Sensors={
	'sensors':	'{}.1'.format(base),
	'index':	'{}.1.1'.format(base),
	'type':		'{}.1.2'.format(base),
	'value':	'{}.1.3'.format(base),
	'updated':	'{}.1.4'.format(base),
	'id':		'{}.1.5'.format(base)
}

Devices={
	'devices':	'{}.2'.format(base),
	'index':	'{}.2.1'.format(base),
	'protocol':	'{}.2.2'.format(base),
	'model':	'{}.2.3'.format(base),
	'value':	'{}.2.4'.format(base),
	'name':		'{}.2.5'.format(base)
}

class TellDevices(Handler):
	cachetime=60

	def __init__(self, tellcore):
		self.tellcore=tellcore
		self.oids=Devices.values()

		self.scan()

	def scan(self):
		self.lastscan=time()
		self.devices=[]

		index=1

		for device in self.tellcore.devices():
			self.devices.append(device)
			self.oids.append('.'.join([ Devices['index'], str(index) ]))
			self.oids.append('.'.join([ Devices['protocol'], str(index) ]))
			self.oids.append('.'.join([ Devices['model'], str(index) ]))
			self.oids.append('.'.join([ Devices['value'], str(index) ]))
			self.oids.append('.'.join([ Devices['name'], str(index) ]))

			index+=1

	def get(self, oid):
		if self.lastscan + self.cachetime < time():
			self.scan()

		index=int(oid.split('.')[-1])

		if oid.startswith(Devices['index']):
			if index > 0 and index <= len(self.devices):
				return '\n'.join([ oid, "integer", str(index) ])

		elif oid.startswith(Devices['protocol']):
			try:
				return '\n'.join([ oid, "string", self.devices[index-1].protocol ])
			except IndexError:
				pass

		elif oid.startswith(Devices['model']):
			try:
				return '\n'.join([ oid, "string", self.devices[index-1].model ])
			except IndexError:
				pass

		elif oid.startswith(Devices['value']):
			return '\n'.join([ oid, "integer", str(self.devices[index-1].last_sent_value()) ])

		elif oid.startswith(Devices['name']):
			return '\n'.join([ oid, "string", self.devices[index-1].name ])

		return 'NONE'

	def getnext(self, oid):
		if self.lastscan + self.cachetime < time():
			self.scan()

		next=None

		if oid==Devices['devices']:
			return self.get('.'.join([ Devices['index'], '1' ]))
		elif oid==Devices['protocol']:
			return self.get('.'.join([ Devices['protocol'], '1' ]))
		elif oid==Devices['model']:
			return self.get('.'.join([ Devices['model'], '1']))
		elif oid==Devices['value']:
			return self.get('.'.join([ Devices['value'], '1']))
		elif oid==Devices['name']:
			return self.get('.'.join([ Devices['name'], '1']))

		index=int(oid.split('.')[-1])

		if oid.startswith(Devices['index']):
			next='.'.join([ Devices['index'], str(index+1) ])
			if not next in self.oids:
				next='.'.join([ Devices['protocol'], str(1) ])

		elif oid.startswith(Devices['protocol']):
			next='.'.join([ Devices['protocol'], str(index+1) ])
			if not next in self.oids:
				next='.'.join([ Devices['model'], str(1) ])

		elif oid.startswith(Devices['model']):
			next='.'.join([ Devices['model'], str(index+1) ])
			if not next in self.oids:
				next='.'.join([ Devices['value'], str(1) ])

		elif oid.startswith(Devices['value']):
			next='.'.join([ Devices['value'], str(index+1) ])
			if not next in self.oids:
				next='.'.join([ Devices['name'], str(1) ])

		elif oid.startswith(Devices['name']):
			next='.'.join([ Devices['name'], str(index+1) ])

		if next and next in self.oids:
			try:
				return self.get(next)
			except IndexError:
				pass

		return 'NONE'

	def set(self, oid, type, value):
		if self.lastscan + self.cachetime < time():
			self.scan()

		index=int(oid.split('.')[-1])

		result='not-writable'

		if oid.startswith(Devices['value']):
			if type != 'gauge':
				result='wrong-type'
			else:
				if value==0:
					self.devices[index-1].turn_off()
					result=0
				else:
					# XXX if the name contains 'dim', then it probably is a dimmer
					if self.devices[index-1].model.find("dim") > 0:
						self.devices[index-1].dim(value)
						result=value
					else:
						self.devices[index-1].turn_on()
						result=1

		return result

class TellSensors(Handler):
	cachetime=60

	def __init__(self, tellcore):
		self.tellcore=tellcore
		self.oids=Sensors.values()

		self.scan()

	def scan(self):
		self.lastscan=time()

		# these share an index
		self.types=[]
		self.sensors=[]

		# enumerate sensors

		index=1

		for sensor in self.tellcore.sensors():
			for type,id in Sensor.DATATYPES.items():
				if sensor.has_value(id):
					self.types.append(type)
					self.sensors.append({'id': id, 'sensor': sensor})

					self.oids.append('.'.join([ Sensors['index'], str(index) ]))
					self.oids.append('.'.join([ Sensors['type'], str(index) ]))
					self.oids.append('.'.join([ Sensors['value'], str(index) ]))
					self.oids.append('.'.join([ Sensors['updated'], str(index) ]))
					self.oids.append('.'.join([ Sensors['id'], str(index) ]))

					index+=1

	def get(self, oid):
		if self.lastscan+self.cachetime > time():
			self.scan()

		index=int(oid.split('.')[-1])

		if oid.startswith(Sensors['index']):
			if index > 0 and index <= len(self.types):
				return '\n'.join([ oid, "integer", str(index) ])

		elif oid.startswith(Sensors['type']):
			try:
				return '\n'.join([ oid, "string", self.types[index-1] ])
			except IndexError:
				pass

		elif oid.startswith(Sensors['value']):
			try:
				return '\n'.join([ oid, "integer", self.float(self.sensors[index-1]['sensor'].value(self.sensors[index-1]['id']).value) ])
			except IndexError:
				pass

		elif oid.startswith(Sensors['updated']):
			try:
				return '\n'.join([ oid, "unsigned32", str(self.sensors[index-1]['sensor'].value(self.sensors[index-1]['id']).timestamp) ])
			except IndexError:
				pass

		elif oid.startswith(Sensors['id']):
			try:
				return '\n'.join([ oid, "unsigned32", str(self.sensors[index-1]['sensor'].id) ])
			except IndexError:
				pass
			
		return 'NONE'

	def getnext(self, oid):
		if self.lastscan+self.cachetime > time():
			self.scan()

		next=None

		if oid==Sensors['sensors']:
			return self.get('.'.join([ Sensors['index'], '1' ]))
		elif oid==Sensors['type']:
			return self.get('.'.join([ Sensors['type'], '1' ]))
		elif oid==Sensors['value']:
			return self.get('.'.join([ Sensors['value'], '1']))
		elif oid==Sensors['updated']:
			return self.get('.'.join([ Sensors['updated'], '1']))
		elif oid==Sensors['id']:
			return self.get('.'.join([ Sensors['id'], '1']))

		index=int(oid.split('.')[-1])

		if oid.startswith(Sensors['index']):
			next='.'.join([ Sensors['index'], str(index+1) ])
			if not next in self.oids:
				next='.'.join([ Sensors['type'], str(1) ])

		elif oid.startswith(Sensors['type']):
			next='.'.join([ Sensors['type'], str(index+1) ])
			if not next in self.oids:
				next='.'.join([ Sensors['value'], str(1) ])

		elif oid.startswith(Sensors['value']):
			next='.'.join([ Sensors['value'], str(index+1) ])
			if not next in self.oids:
				next='.'.join([ Sensors['updated'], str(1) ])

		elif oid.startswith(Sensors['updated']):
			next='.'.join([ Sensors['updated'], str(index+1) ])
			if not next in self.oids:
				next='.'.join([ Sensors['id'], str(1) ])

		elif oid.startswith(Sensors['id']):
			next='.'.join([ Sensors['id'], str(index+1) ])

		if next and next in self.oids:
			try:
				return self.get(next)
			except IndexError:
				pass

		return 'NONE'

if __name__ == "__main__":
	pt=Passthrough()
	tc=TelldusCore()
	pt.addhandler(TellSensors(tc))
	pt.addhandler(TellDevices(tc))
	pt.run()
