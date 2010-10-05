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
# $Id: case507.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case507 (TestCase):

	def config(self):
		self.name = "Case 507"
		self.description = "Correct Record-Routing parameter returning"
		self.isClient = True
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		self.rrrepl = None

		inv = self.createRequest("INVITE")
		via = inv.getParsedHeaderValue("Via")
		rr = self.getParsedHeaderInstance("Record-Route")
		rr.uri.protocol = "sip"
		rr.uri.host = via.host
		rr.uri.port = via.port
		rr.uri.params.append("lr")
		rr.looseRouter = True
		rr.uri.params.append("unknownParameter=unknownValue")
		rr.uri.params.append("   unknownParameterWithLeadingLWS=   unknowValueWithLeadingLWS")
		rr.uri.params.append("unknownParameterWithoutAValue")
		rr.uri.params.append("   unknownParameterWithoutAValueAndWithLeadingLWS")
		inv.setParsedHeaderValue("Record-Route", rr)
		inv.setHeaderValue("Record-Route", rr.create())
		inv.transaction.dialog.ignoreRoute = True
		self.writeMessageToNetwork(self.neh, inv)

		self.code = 0
		self.byed = 0
		while (self.code <= 200) and (self.byed == 0):
			repl = self.readReplyFromNetwork(self.neh)
			if (repl is not None) and (repl.code > self.code):
				self.code = repl.code
			elif  repl is None:
				self.code = 999

		if repl is None:
			self.addResult(TestCase.TC_FAILED, "missing reply on request")
		elif self.rrrepl is not None:
			if self.rrrepl.hasParsedHeaderField("Record-Route"):
				reprr = self.rrrepl.getParsedHeaderValue("Record-Route")
				if reprr == rr:
					self.addResult(TestCase.TC_PASSED, "Record-Route header contains all parameters from request")
				else:
					self.addResult(TestCase.TC_FAILED, "Record-Route header is not equal to Record-Route from request")
			else:
				self.addResult(TestCase.TC_ERROR, "missing Record-Route in reply")
		else:
			self.addResult(TestCase.TC_ERROR, "valid reply (1xx|2xx) with Record-Route missing")

		self.neh.closeSock()

	def onDefaultCode(self, message):
		if message.code > self.code:
			self.code = message.code
		if message.code >= 200:
			if message.getParsedHeaderValue("CSeq").method == "INVITE":
				Log.logDebug("case507: sending ACK for >= 200 reply", 3)
				ack = self.createRequest("ACK", trans=message.transaction)
				self.writeMessageToNetwork(self.neh, ack)
			if message.code == 200:
				if message.transaction.canceled:
					Log.logDebug("case507: received 200 for CANCEL", 3)
				elif message.getParsedHeaderValue("CSeq").method == "INVITE":
					self.rrrepl = message
					Log.logDebug("case507: sending BYE for accepted INVITE", 3)
					bye = self.createRequest("BYE", dia=message.transaction.dialog)
					self.writeMessageToNetwork(self.neh, bye)
					self.byed = 1
					self.code = 999
					rep = self.readReplyFromNetwork(self.neh)
					if rep is None:
						self.addResult(TestCase.TC_ERROR, "missing response on BYE")
		else:
			if message.hasParsedHeaderField("Record-Route"):
				self.rrrepl = message
				can = self.createRequest("CANCEL", trans=message.transaction)
				message.transaction.canceled = True
				self.writeMessageToNetwork(self.neh, can)
				canrepl = self.readReplyFromNetwork(self.neh)
				if canrepl is None:
					self.addResult(TestCase.TC_ERROR, "missing 200 on CANCEL")
			else:
				print "  !!!!  PLEASE ANSWER/PICKUP THE CALL  !!!!"
