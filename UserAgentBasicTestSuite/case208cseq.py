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
# $Id: case208cseq.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case208cseq (TestCase):

	def config(self):
		self.name = "Case 208cseq"
		self.description = "Request scalar fields with overlarge values (CSeq)"
		self.isClient = True
		self.transport = "UDP"

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		inv = self.createRequest("INVITE")
		self.cs = inv.getParsedHeaderValue("CSeq")
		self.cs.number = 4294967297
		inv.setParsedHeaderValue("CSeq", self.cs)
		inv.setHeaderValue("CSeq", self.cs.create())
		inv.transaction.CSeq = self.cs
		inv.transaction.dialog.localCSeq = self.cs
		self.writeMessageToNetwork(self.neh, inv)

		self.code = 0
		while (self.code <= 200):
			repl = self.readReplyFromNetwork(self.neh)
			if (repl is not None) and (repl.code > self.code):
				self.code = repl.code
			elif  repl is None:
				self.code = 999

		if repl is None:
			self.addResult(TestCase.TC_FAILED, "missing reply on request")

		self.neh.closeSock()

	def onDefaultCode(self, message):
		if message.code > self.code:
			self.code = message.code
		# seen that some UAs change the CSeq value: NASTY!
		cs = message.getParsedHeaderValue("CSeq")
		if cs.method == "INVITE" and (cs.number != self.cs.number):
			self.addResult(TestCase.TC_WARN, "UA changed CSeq value from \'" + str(self.cs.number) + "\' to \'" + str(cs.number) + "\'")
		if message.code >= 200:
			if message.getParsedHeaderValue("CSeq").method == "INVITE":
				Log.logDebug("case208cseq: sending ACK for >= 200 reply", 3)
				# we have to give the transaction by hand to prevent
				# that a rewritten CSeq establishes a new transaction
				# which we cant react on
				ack = self.createRequest("ACK", trans=self.dialog[0].transaction[0])
				self.writeMessageToNetwork(self.neh, ack)
			if message.code == 400:
				self.addResult(TestCase.TC_PASSED, "INVITE rejected with 400")
			elif message.code == 200:
				if message.transaction.canceled:
					Log.logDebug("case208cseq: received 200 for CANCEL", 3)
				else:
					Log.logDebug("case208cseq: sending BYE for accepted INVITE", 3)
					bye = self.createRequest("BYE", dia=message.transaction.dialog)
					self.writeMessageToNetwork(self.neh, bye)
					rep = self.readReplyFromNetwork(self.neh)
					if rep is None:
						self.addResult(TestCase.TC_ERROR, "missing response on BYE")
			elif message.code != 487:
				self.addResult(TestCase.TC_FAILED, "INVITE rejected, but not with 400")
		else:
			self.addResult(TestCase.TC_FAILED, "INVITE accepted, not rejected with 400")
			can = self.createRequest("CANCEL", trans=self.dialog[0].transaction[0])
			message.transaction.canceled = True
			self.writeMessageToNetwork(self.neh, can)
			canrepl = self.readReplyFromNetwork(self.neh)
			if canrepl is None:
				self.addResult(TestCase.TC_ERROR, "missing 200 on CANCEL")
