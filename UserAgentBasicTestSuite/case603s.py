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
# $Id: case603s.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log, Config

class case603s (TestCase):

	def config(self):
		self.name = "Case 603s"
		self.description = "Correct loose routing"
		self.isClient = True
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		self.connected = 0
		self.byed = 0

		while self.byed == 0:
			if self.connected == 0:
				print "  !!!! PLEASE CALL ANY NUMBER/USER  !!!!"
			else:
				print "  !!!!  PLEASE TERMINATE/HANGUP THE CALL  !!!!"
			req = self.readRequestFromNetwork(self.neh)

		if (req is None):
			if (self.byed == 0):
				self.addResult(TestCase.TC_FAILED, "missing reply on request")
		if self.byed == 1:
			if req.isRequest and req.method == "BYE":
				if req.hasParsedHeaderField("Route"):
					passed = True
					r = req.getParsedHeaderValue("Route")
					c = self.replok.getParsedHeaderValue("Contact")
					ro = self.getParsedHeaderInstance("Record-Route")
					ro.uri.protocol = "sip"
					ro.uri.host = Config.LOCAL_IP
					ro.uri.port = Config.LOCAL_PORT
					ro.uri.params.append("lr")
					ro.looseRouter= True
					cur = ro
					pr = range(1, 5)
					pr.reverse()
					for i in pr:
						cur.next = self.getParsedHeaderInstance("Record-Route")
						cur.next.uri.protocol = "sip"
						cur.next.uri.host = "proxy0" + str(i) +".example.com"
						cur.next.uri.params.append("lr")
						cur.next.looseRouter = True
						cur = cur.next
					if req.rUri != c.uri:
						self.addResult(TestCase.TC_FAILED, "BYE does not contain Contact URI from INVITE in request URI")
						passed = False
					if not r.cmp(ro):
						self.addResult(TestCase.TC_FAILED, "Route header is not equal with the Record-Route header from INVITE")
						passed = False
					if passed:
						self.addResult(TestCase.TC_PASSED, "Loose routing is correct (request URI and Route header)")
				else:
					self.addResult(TestCase.TC_FAILED, "received BYE misses Route header")

		self.neh.closeSock()

	def onINVITE(self, message):
		self.inv = message
		self.replok = self.createReply(200, "OK", mes=message)
		rr = self.getParsedHeaderInstance("Record-Route")
		cur = rr
		for i in range(1, 5):
			cur.uri.protocol = "sip"
			cur.uri.host = "proxy0" + str(i) +".example.com"
			cur.uri.params.append("lr")
			cur.looseRouter = True
			cur.next = self.getParsedHeaderInstance("Record-Route")
			cur = cur.next
		cur.uri.protocol = "sip"
		cur.uri.host = Config.LOCAL_IP
		cur.uri.port = Config.LOCAL_PORT
		cur.uri.params.append("lr")
		cur.looseRouter= True
		self.replok.setParsedHeaderValue("Record-Route", rr)
		self.replok.setHeaderValue("Record-Route", rr.create())
		self.replok.transaction.dialog.ignoreRoute = True
		self.mediaSockPair = self.setMediaBody(self.replok)
		self.writeMessageToNetwork(self.neh, self.replok)

	def onACK(self, message):
		self.connected = 1

	def onBYE(self, message):
		Log.logDebug("case603s: sending 200 for BYE", 2)
		replok = self.createReply(200, "OK", mes=message)
		self.writeMessageToNetwork(self.neh, replok)
		self.byed = 1
