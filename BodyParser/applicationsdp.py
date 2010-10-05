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
class applicationsdp:

	audio_state = ['sendrecv',
					'sendonly',
					'recvonly',
					'inactive']

	def __init__(self):
		self.version = None
		self.origin = None
		self.sessionname = None
		self.information = None
		self.uri = None
		self.emails = None
		self.phones = None
		self.connection = None
		self.bandwidth = None
		self.time = None
		self.key = None
		self.attributes = None
		self.addrtype = None
		self.ip = None
		self.port = None
		self.fmts = None
		self.rtpmap = None
		self.state = None
		

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
				+ 'media:\'' + str(self.media) + '\', ' \
				+ 'attributes:\'' + str(self.attributes) + '\', ' \
				+ 'addrtype:\'' + str(self.addrtype) + '\', ' \
				+ 'ip:\'' + str(self.ip) + '\', ' \
				+ 'port:\'' + str(self.port) + '\', ' \
				+ 'fmts:\'' + str(self.fmts) + '\', ' \
				+ 'rtpmap:\'' + str(self.rtpmap) + '\', ' \
				+ 'state:\'' + str(self.state) + '\']'

	def parse(self, body):
		for line in body:
			c = line[0].lower()
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
				if self.emails is None:
					self.emails = []
				self.emails.append(line[2:].strip())
			elif c == 'p':
				if self.phones is None:
					self.phones = []
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
				if self.attributes is None:
					self.attributes = []
				self.attributes.append(line[2:].strip())
			elif c == 'm':
				self.media = line[2:].strip().split()
		if not self.connection is None:
			self.addrtype = self.connection[1]
			self.ip = self.connection[2]
		if not self.media is None:
			self.port = self.media[1]
			self.fmts = self.media[3:]
		if not self.attributes is None:
			for at in self.attributes:
				if at.lower().startswith("rtpmap:"):
					if self.rtpmap is None:
						self.rtpmap = {}
					map = at[7:].split()
					self.rtpmap[map[0]] = map[1]
				elif at.lower() in applicationsdp.audio_state:
					self.state = at.lower()
