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
# $Id: Cseq.py,v 1.4 2004/03/19 18:38:44 lando Exp $
#
from HeaderFieldHandler import HeaderFieldHandler
import Log
from SCException import SCNotImplemented, HFHException

class Cseq (HeaderFieldHandler):

	def __init__(self, value=None):
		HeaderFieldHandler.__init__(self)
		self.number = None
		self.method = None
		if value is not None:
			self.parse(value)

	def __str__(self):
		return '[number:\'' + str(self.number) + '\', ' \
				+ 'method:\'' + str(self.method) + '\']'

	def __cmp__(self, other):
		ret = 0
		if other is None:
			return -1
		if self.number != other.number:
			ret = ret + 1
		if self.method != other.method:
			ret = ret + 1
		return ret

	def parse(self, value):
		v = value.replace("\t", "").replace("\r", "").strip()
		# FIXME should be LWS
		sep = v.find(" ")
		if (sep != -1):
			if v[:sep].rstrip().isdigit():
				self.number = long(v[:sep].rstrip())
			else:
				self.number = v[:sep].rstrip()
			self.method = v[sep+1:].lstrip()
		else:
			Log.logDebug("CSeq.parse(): seperator between number and method missing", 1)
			if v.isdigit():
				self.number = v
				Log.logDebug("CSeq.parse(): guessing: number only", 1)
			else:
				self.method = v
				Log.logDebug("CSeq.parse(): falied to parse, using method only", 1)
				#raise HFHException("CSeq", "parse", "failed to parse because number/method seperator missing")

	def create(self):
		if self.number is None:
			num = ''
		else:
			num = str(self.number)
		if self.method is None:
			meth = ''
		else:
			meth = str(self.method)
		return num + ' ' + meth + '\r\n'

	def verify(self):
		raise SCNotImplemented("CSeq", "verify", "not implemented")
