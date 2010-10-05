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
# $Id: case604c.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log
import copy

class case604c (TestCase):

	def config(self):
		self.name = "Case 604c"
		self.description = "Correct strict routing"
		self.isClient = True
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		fst_inv = self.createRequest("INVITE")
		via = fst_inv.getParsedHeaderValue("Via")
		rr = self.getParsedHeaderInstance("Record-Route")
		rr.uri.protocol = "sip"
		rr.uri.host = via.host
		rr.uri.port = via.port
		cur = rr
		for i in range(1, 5):
			cur.next = self.getParsedHeaderInstance("Record-Route")
			cur.next.uri.protocol = "sip"
			cur.next.uri.host = "porxy0" + str(i) +".example.com"
			cur = cur.next
		fst_inv.setParsedHeaderValue("Record-Route", rr)
		fst_inv.setHeaderValue("Record-Route", rr.create())
		fst_inv.transaction.dialog.ignoreRoute = True
		self.mediaSockPair = self.setMediaBody(fst_inv)

		self.byed = 0
		self.writeMessageToNetwork(self.neh, fst_inv)

		while self.byed == 0:
			repl = self.readMessageFromNetwork(self.neh)

		self.neh.closeSock()

		if (repl is None):
			if (self.byed == 0):
				self.addResult(TestCase.TC_FAILED, "missing reply on request")
		if self.byed == 1:
			if repl.isRequest and repl.method == "BYE":
				if repl.hasParsedHeaderField("Route"):
					passed = True
					r = repl.getParsedHeaderValue("Route")
					c = fst_inv.getParsedHeaderValue("Contact")
					if repl.rUri != rr.uri:
						self.addResult(TestCase.TC_FAILED, "BYE does not contain the first Record-Route URI as request URI")
						passed = False
					# convert the Contact into a RR header ;) to be able
					# to use the RR.cmp() function
					cur.next = self.getParsedHeaderInstance("Record-Route")
					cur.next.uri = c.uri
					cur.next.params = c.params
					if not rr.next.cmp(r):
						self.addResult(TestCase.TC_FAILED, "Route header does not fit to the Record-Route and Contact header")
						passed = False
					if passed:
						self.addResult(TestCase.TC_PASSED, "Strict routing is correct (request URI and Route header)")
				else:
					self.addResult(TestCase.TC_FAILED, "received BYE misses Route header")


	def on180(self, message):
		print "PLEASE ANSWER/PICKUP THE CALL!!!!!!"

	def on183(self, message):
		self.on180(message)

	def on200(self, message):
		Log.logDebug("case604c: sending ACK for 200 reply", 2)
		ack = self.createRequest("ACK", trans=message.transaction)
		self.writeMessageToNetwork(self.neh, ack)
		print "  !!!!  PLEASE TERMINATE/HANGUP THE CALL  !!!!"

	def onBYE(self, message):
		Log.logDebug("case604c: sending 200 for BYE", 2)
		replok = self.createReply(200, "OK", mes=message)
		self.writeMessageToNetwork(self.neh, replok)
		self.byed = 1
