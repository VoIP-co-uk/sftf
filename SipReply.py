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
# $Id: SipReply.py,v 1.7 2004/03/19 18:37:25 lando Exp $
#
from SipMessage import SipMessage

class SipReply (SipMessage):
	"""This class inherits all code from SipMessage and implements all
	required functions to handle SIP reply messages.
	"""

	def __init__(self):
		SipMessage.__init__(self)
		self.isRequest = False
		self.code = None
		self.reason = None
		self.request = None

	def __str__(self):
		return '[' + SipMessage.__str__(self) \
				+ ', code:\'' + str(self.code) + '\', ' \
				+ 'reason:\'' + str(self.reason) + '\' ' \
				+ 'request:\'' + str(self.request) + '\']'

	def parseFirstLine(self, fLine):
		"""Tries to parse the given first line from the message. Returns
		True on success and False on error.
		"""
		try:
			if (fLine.lower().startswith("sip")):
				index = fLine.index('/')
				self.protocol = fLine[0:index]
				fLine = fLine[index+1:]
				index = fLine.index(' ')
				self.version = fLine[0:index]
				fLine = fLine[index+1:]
				self.code = int(fLine[0:3])
				self.reason = fLine[4:].replace("\n", "").replace("\r", "").rstrip()
				return True
			else:
				return False
		except:
			return False

	def createFirstLine(self):
		"""Creates and inserts the first line of the reply into the event.
		"""
		self.event.headers.insert(0, self.protocol + "/" + str(self.version) + " " + str(self.code) + " " + self.reason + "\r\n")
