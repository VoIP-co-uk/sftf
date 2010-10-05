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
# $Id: case503c.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case503c (TestCase):

	def config(self):
		self.name = "Case 503c"
		self.description = "No Record-Route in negative replies"
		self.isClient = True
		self.transport = "UDP"

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		inv = self.createRequest("INVITE")
		req = self.getParsedHeaderInstance("Require")
		req.tags.append("FooBarExtension")
		inv.setParsedHeaderValue("Require", req)
		inv.setHeaderValue("Require", req.create())
		via = inv.getParsedHeaderValue("Via")
		rr = self.getParsedHeaderInstance("Record-Route")
		rr.uri.protocol = "sip"
		rr.uri.host = via.host
		rr.uri.port = via.port
		inv.setParsedHeaderValue("Record-Route", rr)
		inv.setHeaderValue("Record-Route", rr.create())
		inv.transaction.dialog.ignoreRoute = True
		self.writeMessageToNetwork(self.neh, inv)

		self.reply = None
		self.code = 0
		while (self.code <= 200):
			repl = self.readReplyFromNetwork(self.neh)
			if (repl is not None) and (repl.code > self.code):
				self.code = repl.code
			elif repl is None:
				self.code = 999

		self.neh.closeSock()

		if repl is None:
			self.addResult(TestCase.TC_ERROR, "missing reply on request")
		if self.reply is None:
			self.addResult(TestCase.TC_FAILED, "missing negative reply, because 'Require: FooBarExtension' was not rejected")
		else:
			if self.reply.hasParsedHeaderField("Record-Route"):
				self.addResult(TestCase.TC_FAILED, "negative reply contains Record-Route header")
			else:
				self.addResult(TestCase.TC_PASSED, "negative reply does not contain Record-Route header")

	def onDefaultCode(self, message):
		if message.code > self.code:
			self.code = message.code
		if message.code >= 200:
			if message.code >= 300:
				self.reply = message
			if message.getParsedHeaderValue("CSeq").method == "INVITE":
				Log.logDebug("case503c: sending ACK for >= 200 reply", 3)
				ack = self.createRequest("ACK", trans=message.transaction)
				self.writeMessageToNetwork(self.neh, ack)
			if message.code == 200:
				if message.transaction.canceled:
					Log.logDebug("case503c: received 200 for CANCEL", 3)
				else:
					Log.logDebug("case503c: sending BYE for accepted INVITE", 3)
					bye = self.createRequest("BYE", dia=message.transaction.dialog)
					self.writeMessageToNetwork(self.neh, bye)
					rep = self.readReplyFromNetwork(self.neh)
					if rep is None:
						self.addResult(TestCase.TC_ERROR, "missing response on BYE")
		else:
			can = self.createRequest("CANCEL", trans=message.transaction)
			message.transaction.canceled = True
			self.writeMessageToNetwork(self.neh, can)
			canrepl = self.readReplyFromNetwork(self.neh)
			if canrepl is None:
				self.addResult(TestCase.TC_ERROR, "missing 200 on CANCEL")
