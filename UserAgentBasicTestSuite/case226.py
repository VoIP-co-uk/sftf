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
# $Id: case226.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case226 (TestCase):

	def config(self):
		self.name = "Case 226"
		self.description = "Multipart body"
		self.isClient = True
		self.transport = "UDP"

	def run(self):
		# creating a network socket is always required
		self.neh = NEH.NetworkEventHandler(self.transport)

		self.inv = self.createRequest("INVITE")
		ct = self.getParsedHeaderInstance("Content-Type")
		ct.type = "multipart"
		ct.subtype = "mixed"
		ct.params.append("boundary=verybasicboundary")
		self.inv.setParsedHeaderValue("Content-Type", ct)
		self.inv.setHeaderValue("Content-Type", ct.create())
		dummy = self.inv.body
		bd = ['--verybasicboundary\r\n', 'Content-Type: text/plain\r\n', '\r\n', 'This is just a text to test the multipart capabilities of the UA.\r\n', '\r\n', '--verybasicboundary\r\n', 'Content-Type: application/sdp\r\n', '\r\n']
		bd.extend(dummy)
		bd.append("--verybasicboundary--\r\n")
		self.setBody(bd, self.inv)
		self.writeMessageToNetwork(self.neh, self.inv)

		self.end = 0
		while self.end == 0:
			repl = self.readReplyFromNetwork(self.neh)
			if repl is None:
				self.end = 1
				self.addResult(TestCase.TC_ERROR, "missing reply on request")

		# at the end please close the socket again
		self.neh.closeSock()


	#FIXME is it enough that the phones rings or do we have to wait for 200?
	def on180(self, message):
		self.addResult(TestCase.TC_PASSED, "multipart body accepted")
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
		if (message.code >= 300) and (message.getParsedHeaderValue("CSeq").method == "INVITE"):
			self.addResult(TestCase.TC_WARN, "INVITE with multipart body rejected with '" + str(message.code) + "'")
			ack = self.createRequest("ACK", trans=message.transaction)
			self.writeMessageToNetwork(self.neh, ack)
			self.end = 1
