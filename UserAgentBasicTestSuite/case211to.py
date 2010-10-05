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
# $Id: case211to.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case211to (TestCase):

	def config(self):
		self.name = "Case 211to"
		self.description = "Missing required header fields (To)"
		self.isClient = True
		self.transport = "UDP"
		self.fixHeaders = False

	def run(self):
		self.branchvalue = "z9hG4bK-SFTF-dummy-branch-value"

		self.neh = NEH.NetworkEventHandler(self.transport)

		inv = self.createRequest("INVITE")
		inv.removeParsedHeaderField("To")
		inv.removeHeaderField("To")
		via = inv.getParsedHeaderValue("Via")
		via.branch = self.branchvalue
		inv.setHeaderValue("Via", via.create())
		inv.createEvent()
		self.writeMessageToNetwork(self.neh, inv)

		self.code = 0
		while (self.code <= 200):
			repl = self.readReplyFromNetwork(self.neh)
			if (repl is not None) and (repl.code > self.code):
				self.code = repl.code
			elif repl is None:
				self.code = 999

		if repl is None:
			self.addResult(TestCase.TC_FAILED, "missing reply on request")

		self.neh.closeSock()

	def onDefaultCode(self, message):
		if message.code > self.code:
			self.code = message.code
		to = None
		if message.hasHeaderField("To"):
			to = message.getHeaderValue("To")
			self.addResult(TestCase.TC_WARN, "UA added To: '" + to.strip() +"'")
		if message.code >= 200:
			if message.getParsedHeaderValue("CSeq").method == "INVITE":
				Log.logDebug("case211to: sending ACK for >= 200 reply", 3)
				ack = self.createRequest("ACK", trans=message.transaction)
				ack.removeParsedHeaderField("To")
				if to is not None:
					ack.setHeaderValue("To", to)
				else:
					ack.removeHeaderField("To")
				ack.createEvent()
				self.writeMessageToNetwork(self.neh, ack)
			if message.code == 400:
				self.addResult(TestCase.TC_PASSED, "INVITE rejected with 400")
			elif message.code == 200:
				if message.transaction.canceled:
					Log.logDebug("case211to: received 200 for CANCEL", 3)
				else:
					Log.logDebug("case211to: sending BYE for accepted INVITE", 3)
					bye = self.createRequest("BYE", dia=message.transaction.dialog)
					self.writeMessageToNetwork(self.neh, bye)
					rep = self.readMessageFromNetwork(self.neh)
					if rep is None:
						self.addResult(TestCase.TC_ERROR, "missing response on BYE")
			elif message.code != 487:
				self.addResult(TestCase.TC_FAILED, "INVITE rejected, but not with 400")
		else:
			self.addResult(TestCase.TC_FAILED, "INVITE accepted, not rejected with 400")
			can = self.createRequest("CANCEL", trans=message.transaction)
			message.transaction.canceled = True
			can.removeParsedHeaderField("To")
			if to is not None:
				can.setHeaderValue("To", to)
			else:
				can.removeHeaderField("To")
			can.createEvent()
			self.writeMessageToNetwork(self.neh, can)
			canrepl = self.readMessageFromNetwork(self.neh)
			if canrepl is None:
				self.addResult(TestCase.TC_ERROR, "missing 200 on CANCEL")
