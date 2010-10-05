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
# $Id: Via.py,v 1.15 2004/03/19 18:38:44 lando Exp $
#
from HeaderFieldHandler import HeaderFieldHandler
from SCException import SCNotImplemented, HFHException
from NetworkEventHandler import compareHostNames

class Via(HeaderFieldHandler):

	def __init__(self, value=None):
		HeaderFieldHandler.__init__(self)
		self.protocol = None
		self.version = None
		self.transport = None
		self.host = None
		self.port = None
		self.ttl = None
		self.maddr = None
		self.received = None
		self.rport = None
		self.branch = None
		self.params = []
		self.next = None
		if value is not None:
			self.parse(value)

	def __str__(self):
		return '[protocol:\'' + str(self.protocol) + '\', ' \
				+ 'version:\'' + str(self.version) + '\', ' \
				+ 'transport:\'' + str(self.transport) + '\', ' \
				+ 'host:\'' + str(self.host) + '\', ' \
				+ 'port:\'' + str(self.port) + '\', ' \
				+ 'ttl:\'' + str(self.ttl) + '\', ' \
				+ 'maddr:\'' + str(self.maddr) + '\', ' \
				+ 'received:\'' + str(self.received) + '\', ' \
				+ 'rport:\'' + str(self.rport) + '\', ' \
				+ 'branch:\'' + str(self.branch) + '\', ' \
				+ 'params:\'' + str(self.params) + '\', ' \
				+ 'next:\'' + str(self.next) + '\']'

	#Note: implementation of __cmp__ is a little bit risky/strange because
	# the comparements with None will also call the same method. So you end
	# up with a really long spiral...
	# Thus __cmp__ only compares one instance. Call cmp() below if you
	# want to compare a complete list.
	def __cmp__(self, other):
		if not isinstance(other, Via):
			return -1
		ret = 0
		if self.protocol != other.protocol:
			ret += 1
		if self.version != other.version:
			ret += 1
		if self.transport != other.transport:
			ret += 1
		if not compareHostNames(self.host, other.host):
			ret += 1
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
				ret += 1
		if self.ttl != other.ttl:
			ret += 1
		if self.maddr != other.maddr:
			ret += 1
		#Note: we can not compare received and rport because the values
		# are supposed to be change by the UAS
		if self.branch != other.branch:
			ret += 1
		for i in self.params:
			if (i not in other.params) and (i.strip() not in other.params):
				eq = i.find("=")
				if eq == -1:
					ret += 1
				else:
					j = i[:eq].strip() + "=" + i[eq+1:].strip()
					if j not in other.params:
						ret += 1
		return ret
	
	def cmp(self, other):
		ret = 0
		cur = self
		cur_o = other
		while ((cur is not None) and (cur_o is not None) and (ret == 0)):
			ret = ret + cur.__cmp__(cur_o)
			cur = cur.next
		if ((cur is not None) and (cur_o is None)) or ((cur is None) and (cur_o is not None)):
			return False
		return ret == 0

	def parse(self, value):
		v = value.replace("\t", " ").replace("\r", "").lstrip()
		sep = v.find("/")
		if (sep != -1):
			self.protocol = v[:sep]
			v = v[sep+1:]
		else:
			raise HFHException("Via", "parse", "failed to parse because protocol/verion seperator '/' missing")
		sep = v.find("/")
		if (sep != -1):
			self.version = v[:sep]
			v = v[sep+1:]
		else:
			raise HFHException("Via", "parse", "failed to parse because version/transport seperator '/' missing")
		sep = v.find(" ")
		if (sep != -1):
			self.transport = v[:sep].rstrip()
			v = v[sep+1:].lstrip()
		else:
			raise HFHException("Via", "parse", "failed to parse because LWS missing in front of uri")
		sep = v.find(",")
		if (sep != -1):
			nvia = v[sep+1:].lstrip()
			v = v[:sep].rstrip()
			self.next = Via()
			self.next.parse(nvia)
		sep = v.find(";")
		pms = None
		if (sep != -1):
			pms = v[sep+1:]
			hp = v[:sep]
		else:
			hp = v.rstrip()
		sep = hp.find(":")
		if (sep != -1):
			self.host = hp[:sep]
			if hp[sep+1:].isdigit():
				self.port = int(hp[sep+1:])
			else:
				self.port = hp[sep+1:]
		else:
			self.host = hp.rstrip()
		if (pms is not None):
			plist = pms.split(";")
			for i in plist:
				s = i.replace("\t", "").strip()
				eq = s.find("=")
				if (eq != -1):
					name = s[:eq]
					value = s[eq+1:]
				else:
					name = s
					value = ""
				name.lower()
				if (name == "ttl"):
					self.ttl = value
				elif (name == "maddr"):
					self.maddr = value
				elif (name == "received"):
					self.received = value
				elif (name == "branch"):
					self.branch = value
				elif (name == "rport"):
					if value == '':
						self.rport = "empty"
					else:
						self.rport = value
				else:
					if value == '':
						self.params.append(i.strip())
					else:
						self.params.append(name.strip() + "=" + value.strip())

	def sub_create(self):
		lead = ''
		hp = ''
		p = ''
		if self.protocol is not None:
			lead = str(self.protocol)
			if self.version is not None:
				lead = lead + '/' + str(self.version)
			if self.transport is not None:
				lead = lead + '/' + str(self.transport)
		if self.host is not None:
			if self.port is not None:
				hp = str(self.host) + ':' + str(self.port)
			else:
				hp = str(self.host)
		if self.branch is not None:
			p = p + ';branch=' + str(self.branch)
		if self.received is not None:
			p = p + ';received=' + str(self.received)
		if self.rport is not None:
			if self.rport == "empty":
				p = p + ';rport'
			else:
				p = p + ';rport=' + str(self.rport)
		if self.ttl is not None:
			p = p + ';ttl=' + str(self.ttl)
		if self.maddr is not None:
			p = p + ';maddr=' + str(self.maddr)
		for i in self.params:
			p = p + ';' + i
		return lead + ' ' + hp + p

	def create(self):
		ret = self.sub_create()
		cur = self.next
		while cur is not None:
			ret = ret + ', ' + cur.sub_create()
			cur = cur.next
		return ret + '\r\n'

	def verify(self):
		raise SCNotImplemented("Via", "verify", "not implemented")
