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
# $Id: case506.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log
import copy

class case506 (TestCase):

	def config(self):
		self.name = "Case 506"
		self.description = "Record-routing is write-once"
		self.isClient = True
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		self.fst_inv = self.createRequest("INVITE")
		via = self.fst_inv.getParsedHeaderValue("Via")
		rr = self.getParsedHeaderInstance("Record-Route")
		rr.uri.protocol = "sip"
		rr.uri.host = via.host
		rr.uri.port = via.port
		rr.uri.params.append("lr")
		rr.looseRouter= True
		rr.next = self.getParsedHeaderInstance("Record-Route")
		rr.next.uri.protocol = "sip"
		rr.next.uri.host = "good.example.com"
		rr.next.uri.params.append("lr")
		rr.next.looseRouter = True
		self.fst_inv.setParsedHeaderValue("Record-Route", rr)
		self.fst_inv.setHeaderValue("Record-Route", rr.create())
		self.fst_inv.transaction.dialog.ignoreRoute = True

		self.reinvited = 0
		self.byed = 0
		self.writeMessageToNetwork(self.neh, self.fst_inv)

		self.code = 0
		while (self.code <= 200) and (self.byed == 0):
			repl = self.readMessageFromNetwork(self.neh)
			if (repl is not None) and (not repl.isRequest) and (repl.code > self.code):
				self.code = repl.code
			elif  repl is None:
				self.code = 999

		if (repl is None):
			if (self.byed == 0):
				self.addResult(TestCase.TC_FAILED, "missing reply on request")
		if self.byed == 1:
			if repl.isRequest and repl.method == "BYE":
				if repl.hasParsedHeaderField("Route"):
					r = repl.getParsedHeaderValue("Route")
					if r.next.uri.host == "good.example.com":
						self.addResult(TestCase.TC_PASSED, "Record-Routing overwritting in re-INVITE ignored")
					elif r.next.uri.host == "bad.example.com":
						self.addResult(TestCase.TC_FAILED, "Record-Routing in re-INVITE overwrote Route")
					else:
						self.addResult(TestCase.TC_ERROR, "unknown host in Route header")
				else:
					self.addResult(TestCase.TC_ERROR, "received BYE misses Route header")

		self.neh.closeSock()

	def on180(self, message):
		print "PLEASE ANSWER/PICKUP THE CALL!!!!!!"

	def on183(self, message):
		self.on180(message)

	def on200(self, message):
		Log.logDebug("case506: sending ACK for 200 reply", 2)
		ack = self.createRequest("ACK", trans=message.transaction)
		self.writeMessageToNetwork(self.neh, ack)
		if self.reinvited == 0:
			self.snd_inv = self.createRequest("INVITE")
			via = self.snd_inv.getParsedHeaderValue("Via")
			rr = self.getParsedHeaderInstance("Record-Route")
			rr.uri.protocol = "sip"
			rr.uri.host = via.host
			rr.uri.port = via.port
			rr.uri.params.append("lr")
			rr.looseRouter= True
			rr.next = self.getParsedHeaderInstance("Record-Route")
			rr.next.uri.protocol = "sip"
			rr.next.uri.host = "bad.example.com"
			rr.next.uri.params.append("lr")
			rr.next.looseRouter = True
			self.snd_inv.setParsedHeaderValue("Record-Route", rr)
			self.snd_inv.setHeaderValue("Record-Route", rr.create())
			self.mediaSockPair = self.setMediaBody(self.snd_inv)
			Log.logDebug("case506: sending the re-INVITE", 1)
			self.writeMessageToNetwork(self.neh, self.snd_inv)
			self.reinvited = 1
		else:
			print "PLEASE TERMINATE/HANGUP THE CALL!!!!"

	def onBYE(self, message):
		Log.logDebug("case506: sending 200 for BYE", 2)
		replok = self.createReply(200, "OK", mes=message)
		self.writeMessageToNetwork(self.neh, replok)
		self.byed = 1
		self.code = 999
