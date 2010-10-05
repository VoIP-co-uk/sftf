#
# Copyright (C) 2004 SIPfoundry Inc.
# Licensed by SIPfoundry under the GPL license.
#
# Copyright (C) 2004 SIP Forum
# Licensed to SIPfoundry under a Contributor Agreement.
#
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
# $Id: sip_uri.py,v 1.18 2004/03/19 18:38:44 lando Exp $
#
from HeaderFieldHandler import HeaderFieldHandler
from SCException import SCNotImplemented
from NetworkEventHandler import compareHostNames
import urllib

class sip_uri (HeaderFieldHandler):

	def __init__(self, value=None):
		HeaderFieldHandler.__init__(self)
		self.protocol = None
		self.username = None
		self.password = None
		self.host = None
		self.ipv6 = False
		self.port = None
		self.params = []
		self.headers = []
		if value is not None:
			self.parse(value)

	def __str__(self):
		return '[protocol:\'' + str(self.protocol) + '\', ' \
				+ 'username:\'' + str(self.username) + '\', ' \
				+ 'password:\'' + str(self.password) + '\', ' \
				+ 'host:\'' + str(self.host) + '\', ' \
				+ 'ipv6:\'' + str(self.ipv6) + '\', ' \
				+ 'port:\'' + str(self.port) + '\', ' \
				+ 'params:\'' + str(self.params) + '\', ' \
				+ 'headers:\'' + str(self.headers) + '\']'

	def __cmp__(self, other):
		ret = 0
		if not isinstance(other, sip_uri):
			return -1
		if self.protocol != other.protocol:
			ret = ret + 1
		if self.username != other.username:
			ret = ret + 1
		if self.password != other.password:
			ret = ret + 1
		if not compareHostNames(self.host, other.host):
			ret = ret + 1
		if self.ipv6 != other.ipv6:
			ret = ret + 1
		if self.port != other.port:
			if self.port is None:
				sp = int(5060)
			elif hasattr(self.port, "isdigit") and self.port.isdigit():
				sp = int(self.port)
			else:
				sp = self.port
			if other.port is None:
				op = int(5060)
			elif hasattr(other.port, "isdigit") and other.port.isdigit():
				op = int(other.port)
			else:
				op = other.port
			if sp != op:
				ret = ret + 1
		#FIXME params from other are not checked against self
		#FIXME params with default values could be omitted
		for i in self.params:
			if i not in other.params:
				ret = ret + 1
		for j in self.headers:
			if j not in other.headers:
				ret = ret + 1
		return ret

	def parse(self, value):
		if (value is None) or (len(value) == 0):
			return
		# first seperate the protocol at the begining
		colsep = value.find(":")
		if colsep != -1:
			self.protocol = value[:colsep]
			uri = value[colsep+1:]
		else:
			uri = value
		# look for a username and password
		atsep = uri.find("@")
		if atsep > 0:
			unpw = uri[:atsep]
			hopo = uri[atsep+1:]
			pwsep = unpw.find(":")
			if pwsep > 0:
				self.username = unpw[:pwsep]
				self.password = unpw[pwsep+1:]
			else:
				self.username = unpw
		else:
			hopo = uri
		# serach for header fields
		hedsep = hopo.find("?")
		if hedsep > 0:
			self.headers = hopo[hedsep+1:].split("&")
			hopo = hopo[:hedsep]
		# search for uri parameters
		pasep = hopo.find(";")
		if pasep > 0:
			self.params = hopo[pasep+1:].split(";")
			hopo = hopo[:pasep]
		# check if it is an IPv6 address
		lb = hopo.find("[")
		if lb >= 0:
			rb = hopo.find("]")
			if rb > 0:
				self.host = hopo[lb+1:rb]
				self.ipv6 = True
				hopo = hopo[rb+1:]
		# search for a port
		posep = hopo.find(":")
		if posep == 0:
			if hopo[posep+1:].isdigit():
				self.port = int(hopo[posep+1:])
			else:
				self.port = hopo[posep+1:]
		elif posep > 0:
			if self.host is None:
				self.host = hopo[:posep]
			if hopo[posep+1:].isdigit():
				self.port = int(hopo[posep+1:])
			else:
				self.port = hopo[posep+1:]
		elif (len(hopo) > 0) and (self.host is None):
			self.host = hopo
		# unescape
		# Note: port cant contain escapes
		#       host arent allowed to be unescaped
		if self.username:
			self.username = urllib.unquote(self.username)
		if self.password:
			self.password = urllib.unquote(self.password)
		# FIXME: should we unescape params and headers too?

	def create(self):
		po = ''
		up = ''
		hp = ''
		ps = ''
		hs = ''
		if self.protocol is not None:
			po = self.protocol + ':'
		if self.username is not None:
			if self.password is not None:
				up = self.username + ':' + self.password + '@'
			else:
				up = self.username + '@'
		if self.host is not None:
			if self.port is not None:
				if self.ipv6:
					hp = "[" + self.host + ']:' + str(self.port)
				else:
					hp = self.host + ':' + str(self.port)
			elif self.ipv6:
				hp = "[" + self.host + "]"
			else:
				hp = self.host
		for i in self.params:
			ps = ps + ';' + i
		for i in self.headers:
			hs = hs + '&' + i
		if hs != '':
			hs = hs.replace('&', '?', 1)
		return po + up + hp + ps + hs

	def verify(self):
		raise SCNotImplemented("sip_uri","verify", "not implemented")
