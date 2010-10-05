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
# $Id: case203.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case203 (TestCase):

	def config(self):
		self.name = "Case 203"
		self.description = "Valid URI escaping"
		self.isClient = True
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		self.fst_inv = self.createRequest("INVITE")
		co = self.fst_inv.getParsedHeaderValue("Contact")
		co.uri.username = "sc%40sip%63ert"
		co.uri.params.append("%6C%72")
		self.fst_inv.setHeaderValue("Contact", co.create())

		self.invited = 0
		self.byed = 0
		self.writeMessageToNetwork(self.neh, self.fst_inv)

		self.code = 0
		while (self.code <= 200) and (self.byed == 0):
			if self.invited == 0:
				print "  !!!!  PLEASE ANSWER/PICKUP THE CALL  !!!!"
			else:
				print "  !!!!  PLEASE TERMINATE/HANGUP THE CALL  !!!!"
			repl = self.readMessageFromNetwork(self.neh)
			if (repl is not None) and (not repl.isRequest) and (repl.code > self.code):
				self.code = repl.code
			elif  repl is None:
				self.code = 999

		self.neh.closeSock()

		if (repl is None) and (self.byed == 0):
				self.addResult(TestCase.TC_FAILED, "missing BYE request for evaluation")
		if self.byed == 1:
			if self.bye.rUri.username == "sc":
				self.addResult(TestCase.TC_FAILED, "request URI contained un-escaped @ in username")
			elif self.bye.rUri.username == "sc@sipcert":
				self.addResult(TestCase.TC_PASSED, "escaped username in request URI used")
			elif self.bye.rUri.username == "sc%40sipcert":
				self.addResult(TestCase.TC_WARN, "illegal charaters in request URI still escaped, but other escapings removed")
			else:
				self.addResult(TestCase.TC_FAILED, "request URI of the BYE did not contained the given escaped Contact value from the INVITE")


	def on200(self, message):
		Log.logDebug("case203: sending ACK for 200 reply", 2)
		ack = self.createRequest("ACK", trans=message.transaction)
		self.invited = 1
		self.writeMessageToNetwork(self.neh, ack)
		print "  !!!!  PLEASE TERMINATE/HANGUP THE CALL  !!!!"

	def onBYE(self, message):
		Log.logDebug("case203: sending 200 for BYE", 2)
		self.bye = message
		replok = self.createReply(200, "OK", mes=message)
		self.writeMessageToNetwork(self.neh, replok)
		self.byed = 1
		self.code = 999
