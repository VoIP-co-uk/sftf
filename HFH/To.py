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
# $Id: To.py,v 1.13 2004/03/19 18:38:44 lando Exp $
#
from HeaderFieldHandler import HeaderFieldHandler
from SCException import SCNotImplemented
import name_addr, sip_uri

class To (HeaderFieldHandler):

	def __init__(self, value=None):
		HeaderFieldHandler.__init__(self)
		self.displayname = None
		self.uri = sip_uri.sip_uri()
		self.tag = None
		self.params = []
		if value is not None:
			self.parse(value)

	def __str__(self):
		return '[displayname:\'' + str(self.displayname) + '\', ' \
				+ 'uri:\'' + str(self.uri) + '\', ' \
				+ 'tag:\'' + str(self.tag) + '\', ' \
				+ 'params:\'' + str(self.params) + '\']'

	def parse(self, value):
		v = value.replace("\r", "").replace("\t", "").strip()
		self.displayname, uristr, self.params, brackets = name_addr.parse(v)
		self.uri.parse(uristr)
		if (not brackets) and (len(self.uri.params) > 0) and (len(self.uri.headers) == 0) and (len(self.params) == 0):
			self.params = self.uri.params
			self.uri.params = []
		paramslen = range(0, len(self.params))
		paramslen.reverse()
		for i in paramslen:
			if (self.params[i].lower().startswith("tag=")):
				self.tag = self.params[i][4:]
				self.params[i:i+1] = []

	def create(self):
		ret = ""
		if self.displayname is not None:
			ret = "\"" + str(self.displayname) + "\" "
		if self.uri is not None:
			ret = ret + "<" + self.uri.create() + ">"
		if self.tag is not None:
			ret = ret + ";tag=" + str(self.tag)
		p = ""
		for i in self.params:
			p = p + ";" + i
		if len(p) > 0:
			ret = ret + p
		return ret + "\r\n"

	def verify(self):
		raise SCNotImplemented("To", "verify", "not implemented")
