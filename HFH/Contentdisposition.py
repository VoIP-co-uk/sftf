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
from HeaderFieldHandler import HeaderFieldHandler
from SCException import SCNotImplemented, HFHException

class Contentdisposition (HeaderFieldHandler):

	def __init__(self, value=None):
		HeaderFieldHandler.__init__(self)
		self.type = None
		self.params = []
		if value is not None:
			self.parse(value)

	def __str__(self):
		return '[type:\'' + str(self.type) + '\', ' \
				+ 'params:\'' + str(self.params) + '\']'

	def parse(self, value):
		v = value.replace("\r", "").replace("\t", "").strip()
		sep = v.find(";")
		if (sep != -1):
			self.type = v[:sep].strip()
			pm = v[sep+1:]
			self.params = pm.split(";")
		else:
			self.type = v

	def create(self):
		ret = ''
		if self.type is not None:
			ret = str(self.type)
		for i in self.params:
			ret = ret + ';' + i
		return ret + '\r\n'

	def verify(self):
		raise SCNotImplemented("ContentDisposition", "verify", "not implemented")
