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
# $Id: case604s.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log, Config

class case604s (TestCase):

	def config(self):
		self.name = "Case 604s"
		self.description = "Correct strict routing"
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

		self.neh.closeSock()

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
					cur = ro
					pr = range(1, 5)
					pr.reverse()
					for i in pr:
						cur.next = self.getParsedHeaderInstance("Record-Route")
						cur.next.uri.protocol = "sip"
						cur.next.uri.host = "proxy0" + str(i) +".example.com"
						cur = cur.next
					# convert Contact into a RR header ;) to be able to use
					# the RR.cmp() function
					cur.next = self.getParsedHeaderInstance("Record-Route")
					cur.next.uri = c.uri
					cur.next.params = c.params
					if req.rUri != ro.uri:
						self.addResult(TestCase.TC_FAILED, "BYE does not contain the first Record-Route URI as request URI")
						passed = False
					if not ro.next.cmp(r):
						self.addResult(TestCase.TC_FAILED, "Route header is not equal with the Record-Route and Contact header")
						passed = False
					if passed:
						self.addResult(TestCase.TC_PASSED, "Strict routing is correct (request URI and Route header)")
				else:
					self.addResult(TestCase.TC_FAILED, "received BYE misses Route header")

	def onINVITE(self, message):
		self.inv = message
		self.replok = self.createReply(200, "OK", mes=message)
		rr = self.getParsedHeaderInstance("Record-Route")
		cur = rr
		for i in range(1, 5):
			cur.uri.protocol = "sip"
			cur.uri.host = "proxy0" + str(i) +".example.com"
			cur.next = self.getParsedHeaderInstance("Record-Route")
			cur = cur.next
		cur.uri.protocol = "sip"
		cur.uri.host = Config.LOCAL_IP
		cur.uri.port = Config.LOCAL_PORT
		self.replok.setParsedHeaderValue("Record-Route", rr)
		self.replok.setHeaderValue("Record-Route", rr.create())
		self.replok.transaction.dialog.ignoreRoute = True
		self.mediaSockPair = self.setMediaBody(self.replok)
		self.writeMessageToNetwork(self.neh, self.replok)

	def onACK(self, message):
		self.connected = 1

	def onBYE(self, message):
		Log.logDebug("case604s: sending 200 for BYE", 2)
		replok = self.createReply(200, "OK", mes=message)
		self.writeMessageToNetwork(self.neh, replok)
		self.byed = 1
