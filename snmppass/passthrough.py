#!/usr/bin/env python2.7
# vim:ts=4:sw=4:

import sys

class Passthrough(object):
	def __init__(self):
		self.input=sys.stdin
		self.output=sys.stdout
		self.handlers=[]

	def addhandler(self, handler):
		self.handlers.append(handler)

	def read(self):
		return self.input.readline().rstrip()

	def reply(self, message):
		self.output.write("{}\n".format(message));
		self.output.flush()

	def run(self):
		done=False

		while not done:
			line=self.read()

			reply="NONE"

			if line=='PING':
				self.reply('PONG')
				continue

			elif line=='':
				done=True
				break

			elif line=='get':
				oid=self.read()

				for handler in self.handlers:
						reply=handler.get(oid)

						if reply != 'NONE':
							break

			elif line=='getnext':
				oid=self.read()

				for handler in self.handlers:
					reply=handler.getnext(oid)

					if reply != 'NONE':
						break

			elif line=='set':
				oid=self.read()
				type, value=self.read().split(' ')

				if type=='integer' or type=='gauge':
					value=int(value)

				reply="not-writable"

				for handler in self.handlers:
					reply=handler.set(oid, type, value)
					if reply != 'not-writable':
						break

			self.reply(reply)

class Handler(object):
	def float(self, value):
		return str(int(float(value)*100))

	# override these in subclasses

	def get(self, oid):
		return "NONE"

	def getnext(self, oid):
		return "NONE"

	def set(self, oid, type, value):
		return "not-writable"
