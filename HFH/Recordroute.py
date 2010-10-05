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
# $Id: Recordroute.py,v 1.6 2004/03/19 18:38:44 lando Exp $
#
from HeaderFieldHandler import HeaderFieldHandler
from SCException import SCNotImplemented
import name_addr, sip_uri

class Recordroute (HeaderFieldHandler):

	def __init__(self, value=None):
		HeaderFieldHandler.__init__(self)
		self.displayname = None
		self.uri = sip_uri.sip_uri()
		self.looseRouter = False
		self.params = []
		self.next = None
		if value is not None:
			self.parse(value)

	def __str__(self):
		return '[displayname:\'' + str(self.displayname) + '\', ' \
				+ 'uri:\'' + str(self.uri) + '\', ' \
				+ 'looseRouter:\'' + str(self.looseRouter) + '\', ' \
				+ 'params:\'' + str(self.params) + '\', ' \
				+ 'next:\'' + str(self.next) + '\']'

	# NOTE: is does only compare the self part, not the
	# complete list of RR headers
	def __cmp__(self, other):
		ret = 0
		if not isinstance(other, Recordroute):
			return -1
		if self.displayname != other.displayname:
			ret = ret + 1
		if self.uri != other.uri:
			ret = ret + 1
		if self.looseRouter != other.looseRouter:
			ret = ret + 1
		for i in self.params:
			if i not in other.params:
				ret = ret + 1
		return ret

	def cmp(self, other):
		ret = 0
		cur = self
		cur_o = other
		while ((cur is not None) and (cur_o is not None) and (ret == 0)):
			ret = ret + cur.__cmp__(cur_o)
			cur = cur.next
			cur_o = cur_o.next
		if ((cur is not None) and (cur_o is None)) or ((cur is None) and (cur_o is not None)):
			return False
		return ret == 0

	def sub_parse(self, sub_value):
		self.displayname, uristr, self.params, brackets = name_addr.parse(sub_value)
		self.uri.parse(uristr)
		if (not brackets) and (len(self.uri.params) > 0) and (len(self.uri.headers) == 0) and (len(self.params) == 0):
			self.params = self.uri.params
			self.uri.params = []
		for i in self.uri.params:
			if i in ('lr', 'LR', 'Lr', 'lR'):
				self.looseRouter = True
			elif i.lower().startswith('lr='):
				self.looseRouter = True

	def parse(self, value):
		v = value.replace("\r", "").replace("\t", "").strip()
		# FIXME seperator can appear in quotes too
		vlist = v.split(",")
		self.sub_parse(vlist[0])
		vllen = range (1, len(vlist))
		current = self
		for i in vllen:
			current.next = Recordroute()
			current = current.next
			current.sub_parse(vlist[i])
	
	def sub_create(self):
		sub_ret = ""
		if self.displayname is not None:
			sub_ret = "\"" + str(self.displayname) + "\" "
		if self.uri is not None:
			sub_ret = sub_ret + "<" + self.uri.create() + ">"
		params = ""
		for i in self.params:
			params = params + ";" + i
		if len(params) > 0:
			sub_ret = sub_ret + params
		return sub_ret

	def create(self):
		ret = self.sub_create()
		nrr = self.next
		while nrr is not None:
			ret = ret + ", " + nrr.sub_create()
			nrr = nrr.next
		return ret + "\r\n"
