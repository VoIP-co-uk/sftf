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
# $Id: Callid.py,v 1.3 2004/03/19 18:38:44 lando Exp $
#
from HeaderFieldHandler import HeaderFieldHandler
from SCException import SCNotImplemented

class Callid (HeaderFieldHandler):

	def __init__(self, value=None):
		HeaderFieldHandler.__init__(self)
		self.str = None
		self.host = None
		if value is not None:
			self.parse(value)

	def __str__(self):
		return '[str:\'' + str(self.str) + '\', ' \
				+ 'host:\'' + str(self.host) + '\']'

	def __cmp__(self, other):
		ret = 0
		if other is None:
			return -1
		if self.str != other.str:
			ret = ret + 1
		if self.host != other.host:
			ret = ret + 1
		return ret

	def parse(self, value):
		v = value.replace("\t","").replace("\r", "").strip()
		sep = v.find("@")
		if (sep != -1):
			self.str = v[:sep]
			self.host = v[sep+1:]
		else:
			self.str = v

	def create(self):
		if self.host is not None:
			return str(self.str) + "@" + str(self.host) + "\r\n"
		else:
			return str(self.str) + "\r\n"


	def verify(self):
		raise SCNotImplemented("CallID", "verify", "not implemented")
