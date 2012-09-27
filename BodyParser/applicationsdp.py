#
# Copyright (C) 2004 SIPfoundry Inc.
# Licensed by SIPfoundry under the GPL license.
#
# This file is part of SIP Forum Test Framework.
#
# SIP Forum Test Framework is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# SIP Forum Test Framework is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SIP Forum Test Framework; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$
#

class _MediaDescription:
	def __init__(self, mLine):
		self.m = mLine
		self.i = None
		self.c = None
		self.b = None
		self.k = None
		self.a = []

	def generate(self):
		desc = [ 'm='+' '.join(self.m) ]
		if self.i:
			desc.append('i='+self.i)
		if self.c:
			desc.append('c='+' '.join(self.c))
		if self.b:
			desc.append('b='+':'.join(self.b))
		if self.k:
			desc.append('k='+self.k)
		for attr in self.a:
			desc.append('a='+attr)
		return desc

	def __str__(self):
		return '[' + ','.join(self.generate()) + ']'


class applicationsdp:

	def __init__(self):
		self.version = None
		self.origin = None
		self.sessionname = None
		self.information = None
		self.uri = None
		self.emails = []
		self.phones = []
		self.connection = None
		self.bandwidth = None
		self.time = None
		self.key = None
		self.attributes = []
		self.media = []


	def generate(self):
		sdp = []
		sdp.append('v='+str(self.version))
		sdp.append('o='+' '.join(self.origin))
		sdp.append('s='+self.sessionname)
		if self.information is not None:
			sdp.append('i='+self.information)
		if self.uri is not None:
			sdp.append('u='+self.uri)
		sdp.extend( ['e='+e for e in self.emails] )
		sdp.extend( ['p='+p for p in self.phones] )
		if self.connection is not None:
			sdp.append('c='+' '.join(self.connection))
		if self.bandwidth is not None:
			sdp.append('b='+':'.join(self.bandwidth))
		if self.time is not None:
			sdp.append('t='+self.time)
		if self.key is not None:
			sdp.append('k='+self.key)
		sdp.extend( ['a='+a for a in self.attributes] )
		for m in self.media:
			sdp.extend(m.generate())
		return '\r\n'.join(sdp)+'\r\n'
		

	def __str__(self):
		return '[version:\'' + str(self.version) + '\', ' \
				+ 'origin:\'' + str(self.origin) + '\', ' \
				+ 'sessionname:\'' + str(self.sessionname) + '\', ' \
				+ 'information:\'' + str(self.information) + '\', ' \
				+ 'uri:\'' + str(self.uri) + '\', ' \
				+ 'emails:\'' + str(self.emails) + '\', ' \
				+ 'phones:\'' + str(self.phones) + '\', ' \
				+ 'connection:\'' + str(self.connection) + '\', ' \
				+ 'bandwidth:\'' + str(self.bandwidth) + '\', ' \
				+ 'time:\'' + str(self.time) + '\', ' \
				+ 'key:\'' + str(self.key) + '\', ' \
				+ 'attributes:\'' + str(self.attributes) + '\', ' \
				+ 'media:\'' + str(self.media) + '\']'

	def parse(self, body):
		mediaDescription = None
		for line in body:
			c = line[0].lower()
			if not mediaDescription:
				if c == 'v':
					self.version = int(line[2:].strip())
				elif c == 'o':
					self.origin = line[2:].strip().split()
				elif c == 's':
					self.sessionname = line[2:].strip()
				elif c == 'i':
					self.information = line[2:].strip()
				elif c == 'u':
					self.uri = line[2:].strip()
				elif c == 'e':
					self.emails.append(line[2:].strip())
				elif c == 'p':
					self.phones.append(line[2:].strip())
				elif c == 'c':
					self.connection = line[2:].strip().split()
				elif c == 'b':
					self.bandwidth = line[2:].strip().split(':')
				elif c == 't':
					self.time = line[2:].strip()
				elif c == 'k':
					self.key = line[2:].strip()
				elif c == 'a':
					self.attributes.append(line[2:].strip())
				elif c == 'm':
					mediaDescription = _MediaDescription(line[2:].strip().split())
			else:
				if c == 'i':
					mediaDescription.i = line[2:].strip()
				elif c == 'c':
					mediaDescription.c = line[2:].strip().split()
				elif c == 'b':
					mediaDescription.b = line[2:].strip().split(':')
				elif c == 'k':
					mediaDescription.k = line[2:].strip()
				elif c == 'a':
					mediaDescription.a.append(line[2:].strip())
				elif c == 'm':
					self.media.append(mediaDescription)
					mediaDescription = _MediaDescription(line[2:].strip().split())

		if mediaDescription:
			self.media.append(mediaDescription)
