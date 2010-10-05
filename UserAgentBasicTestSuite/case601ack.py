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
# $Id: case601ack.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case601ack (TestCase):

	def config(self):
		self.name = "Case 601ack"
		self.description = "Proper Generation of ACK"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.testtag = "SC-test-tag"

		self.neh = NEH.NetworkEventHandler(self.transport)

		#if not self.userInteraction("case601ack: proceed when ready to send INVITE"):
		#	neh.closeSock()
		#	return

		self.inv = None
		self.ack = None
		self.rejected = 0
		while self.rejected == 0:
			print "  !!!! PLEASE CALL ANY NUMBER/USER  !!!!"
			req = self.readMessageFromNetwork(self.neh)

		self.neh.closeSock()

		if self.inv is not None:
			if self.inv.hasHeaderField("Via"):
				req_via = self.inv.getHeaderValue("Via")
			else:
				Log.logDebug("case601ack: missing Via header in INVITE", 1)
				Log.logTest("case601ack: missing Via header in INVITE")
				self.addResult(TestCase.TC_ERROR, "missing Via in first INVITE")
		if self.ack is not None:
			if self.ack.hasHeaderField("Via"):
				can_via = self.ack.getHeaderValue("Via")
			else:
				Log.logDebug("case601ack: missing Via header in ACK", 1)
				Log.logTest("case601ack: missing Via header in ACK")
				self.addResult(TestCase.TC_ERROR, "missing Via in ACK")
			if self.ack.hasParsedHeaderField("To"):
				ack_to = self.ack.getParsedHeaderValue("To")
			else:
				Log.logDebug("case601ack: missing To header in ACK", 1)
				Log.logTest("case601ack: missing To header in ACK")
				self.addResult(TestCase.TC_ERROR, "missing To in ACK")

			if self.inv.rUri != self.ack.rUri:
				Log.logDebug("case601ack: INVITE uri (\'" + str(self.inv.rUri.create()) + "\') and ACK uri (\'" + str(self.ack.rUri.create()) + "\') differ", 1)
				Log.logTest("case601: INVITE and ACK request uri do not match")
				self.addResult(TestCase.TC_FAILED, "INVITE and ACK uri differ")
			elif req_via != can_via:
				Log.logDebug("case601ack: INVITE topmost Via (\'" + str(req_via) + "\') and ACK topmost Via (\'" + str(can_via) + "\') differ", 1)
				Log.logTest("case601ack: topmost Via of INVITE and ACK differ")
				self.addResult(TestCase.TC_FAILED, "INVITE and ACK topmost Via differ")
			elif ack_to.tag != self.testtag:
				Log.logDebug("case601ack: To tag in ACK (\'" + str(ack_to.tag) + "\') differes from tag in reply (\'" + self.testtag + "\')", 1)
				Log.logTest("case601ack: To tag in reply and ACK differ")
				self.addResult(TestCase.TC_FAILED, "reply and ACK To tag differ")
			else:
				Log.logDebug("case601ack: request uri and topmost Via of INVITE and ACK are equal", 2)
				Log.logTest("case601ack: r-uri and Via of INVITE and ACK are equal")
				self.addResult(TestCase.TC_PASSED, "r-uri and Via of INVITE and ACK are equal")


	def onINVITE(self, message):
		self.inv = message
		repl = self.createReply(404, "Not Found")
		to = repl.getParsedHeaderValue("To")
		if to is None:
			Log.logDebug("case601ack: To header missing in request", 1)
			Log.logTest("case601ack: To header missing in request")
			self.addResult(TestCase.TC_ERROR, "To header missing in request")
		to.tag = self.testtag
		repl.setHeaderValue("To", to.create())
		self.writeMessageToNetwork(self.neh, repl)
		self.rejected = 1
		self.ack = self.readRequestFromNetwork(self.neh)
		if self.ack is None:
			self.addResult(TestCase.TC_ERROR, "missing ACK on 404")
