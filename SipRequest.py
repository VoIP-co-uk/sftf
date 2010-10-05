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
# $Id: SipRequest.py,v 1.7 2004/03/30 21:52:36 lando Exp $
#
from SipMessage import SipMessage
import Helper

class SipRequest (SipMessage):
	"""This class inherits all code from SipMessage and implementes all 
	additional function which are required to handle a SIP request.
	"""

	def __init__(self):
		SipMessage.__init__(self)
		self.isRequest = True
		self.method = None
		self.rUri = None

	def __str__(self):
		return '[' + SipMessage.__str__(self) \
				+ ', method:\'' + str(self.method) + '\', ' \
				+ 'rUri:\'' + str(self.rUri) + '\']'

	def parseFirstLine(self, fLine):
		"""Tries to parse the given first line of a message as a SIP request
		line. On succes returns True, otherwise False.
		"""
		try:
			index = fLine.index(' ')
			self.method = fLine[0:index]
			fLine = fLine[index+1:]
			index = fLine.index(' ')
			self.rUri = Helper.createClassInstance("sip_uri")
			self.rUri.parse(fLine[0:index])
			fLine = fLine[index+1:]
			index = fLine.index('/')
			self.protocol = fLine[0:index]
			if not self.protocol.lower().startswith("sip"):
				return False
			self.version = fLine[index+1:].replace("\n", "").replace("\r", "").rstrip()
			return True
		except:
			return False

	def createFirstLine(self):
		"""Creates and inserts the first line of the SIP request into the event.
		"""
		self.event.headers.insert(0, self.method + " " + self.rUri.create() + " " + self.protocol + "/" + self.version + "\r\n")
