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
# $Id: case211from.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case211from (TestCase):

	def config(self):
		self.name = "Case 211from"
		self.description = "Missing required header fields (From)"
		self.isClient = True
		self.transport = "UDP"
		self.fixHeaders = False

	def run(self):
		self.branchvalue = "z9hG4bK-SFTF-dummy-branch-value"

		self.neh = NEH.NetworkEventHandler(self.transport)

		inv = self.createRequest("INVITE")
		inv.removeParsedHeaderField("From")
		inv.removeHeaderField("From")
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
		f = None
		if message.hasHeaderField("From"):
			f = message.getHeaderValue("From")
			self.addResult(TestCase.TC_WARN, "UA added From: '" + str(f).strip() + "'")
		if message.code >= 200:
			if message.hasParsedHeaderField("CSeq") and message.getParsedHeaderValue("CSeq").method == "INVITE":
				Log.logDebug("case211from: sending ACK for >= 200 reply", 3)
				ack = self.createRequest("ACK", trans=message.transaction)
				ack.removeParsedHeaderField("From")
				if f is not None:
					ack.setHeaderValue("From", f)
				else:
					ack.removeHeaderField("From")
				ack.createEvent()
				self.writeMessageToNetwork(self.neh, ack)
			if message.code == 400:
				self.addResult(TestCase.TC_PASSED, "INVITE rejected with 400")
			elif message.code == 200:
				if message.transaction.canceled:
					Log.logDebug("case211from: received 200 for CANCEL", 3)
				else:
					Log.logDebug("case211from: sending BYE for accepted INVITE", 3)
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
			can.removeParsedHeaderField("From")
			if f is not None:
				can.setHeaderValue("From", f)
			else:
				can.removeHeaderField("From")
			can.createEvent()
			self.writeMessageToNetwork(self.neh, can)
			canrepl = self.readMessageFromNetwork(self.neh)
			if canrepl is None:
				self.addResult(TestCase.TC_ERROR, "missing 200 on CANCEL")
