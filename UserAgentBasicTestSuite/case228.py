#
# Copyright (C) 2004 SIPfoundry Inc.
# Licensed by SIPfoundry under the GPL license.
#
# Copyright (C) 2004 SIP Forum
# Licensed to SIPfoundry under a Contributor Agreement.
#
#
# This file is part of SIP Forum User Agent Basic Test Suite which
# belongs to the SIP Forum Test Framework.
#
# SIP Forum User Agent Basic Test Suite is free software; you can 
# redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation; either 
# version 2 of the License, or (at your option) any later version.
#
# SIP Forum User Agent Basic Test Suite is distributed in the hope that it 
# will be useful, but WITHOUT ANY WARRANTY; without even the implied 
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SIP Forum User Agent Basic Test Suite; if not, write to the 
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, 
# MA  02111-1307  USA
#
# $Id: case228.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case228 (TestCase):

	def config(self):
		self.name = "Case 228"
		self.description = "UTF in display names"
		self.isClient = True
		self.transport = "UDP"

	def run(self):
		# creating a network socket is always required
		self.neh = NEH.NetworkEventHandler(self.transport)

		self.inv = self.createRequest("INVITE")
		to = self.inv.getParsedHeaderValue("To")
		# the To displayname does not contain special characters
		# feel free to add some
		to.displayname = u"SC@SIP-Forum".encode('utf8')
		self.inv.setHeaderValue("To", to.create())
		fr = self.inv.getParsedHeaderValue("From")
		# german umlaute rulez (tribute to the german author of all this :-)
		fr.displayname = unicode("\xC4\xD6\xDC\xE4\xF6\xFC\xDF", "unicode_escape").encode('utf8')
		self.inv.setHeaderValue("From", fr.create())
		self.writeMessageToNetwork(self.neh, self.inv)

		self.end = 0
		while self.end == 0:
			repl = self.readReplyFromNetwork(self.neh)
			if repl == None:
				self.addResult(TestCase.TC_FAILED, "missing reply on INVITE")
				self.end = 1

		# at the end please close the socket again
		self.neh.closeSock()


	#FIXME is it enough that the phones rings or do we have to wait for 200?
	def on180(self, message):
		self.addResult(TestCase.TC_PASSED, "request with UTF display names accepted")
		self.addResult(TestCase.TC_INIT, "the From contained german umlauts: A\"O\"U\"a\"o\"u\"sz (verify the UA missed call log)")
		can = self.createRequest("CANCEL", trans=message.transaction)
		message.transaction.canceled = True
		self.writeMessageToNetwork(self.neh, can)
		canrepl = self.readReplyFromNetwork(self.neh)
		if canrepl is None:
			self.addResult(TestCase.TC_ERROR, "missing reply on CANCEL")
	
	def on183(self, message):
		self.on180(message)

	def on487(self, message):
		ack = self.createRequest("ACK", trans=message.transaction)
		self.writeMessageToNetwork(self.neh, ack)
		self.end = 1

	def onDefaultCode(self, message):
		if (message.code >= 300):
			if (message.getParsedHeaderValue("CSeq").method == "INVITE"):
				self.addResult(TestCase.TC_WARN, "INVITE with UTF displaynames rejected with '" + str(message.code) + "'")
				ack = self.createRequest("ACK", trans=message.transaction)
				self.writeMessageToNetwork(self.neh, ack)
				self.end = 1
			elif (message.getParsedHeaderValue("CSeq").method == "CANCEL"):
				self.addResult(TestCase.TC_ERROR, "CANCEL rejected with '" + str(message.code) + "'")
				self.end = 1
