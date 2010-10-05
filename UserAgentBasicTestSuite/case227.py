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
# $Id: case227.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log, Config

class case227 (TestCase):

	def config(self):
		self.name = "Case 227"
		self.description = "Redirection"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.redirect_user_name = "redirect"

		self.neh = NEH.NetworkEventHandler(self.transport)

		#if not self.userInteraction("case227: proceed when ready to send INVITE"):
		#	neh.closeSock()
		#	return

		print "  !!!!  PLEASE CALL ANY NUMBER/USER WITHIN 1 MINUTE  !!!!"
		self.redirected = 0
		req = self.readRequestFromNetwork(self.neh, 60)

		if req is None:
			self.addResult(TestCase.TC_ERROR, "missing INVITE request")
			self.neh.closeSock()
			return

		red = self.readRequestFromNetwork(self.neh)

		if red is None:
			self.addResult(TestCase.TC_FAILED, "missing INVITE to redirected user")
		else:
			if self.redinv.rUri == self.co.uri:
				self.addResult(TestCase.TC_PASSED, "successfull redirected")
			else:
				self.addResult(TestCase.TC_FAILED, "request URI in redirected request differ from Contact URI")

		self.neh.closeSock()

	def onINVITE(self, message):
		if self.redirected == 0:
			repl302 = self.createReply(302, "Moved Temporarily")
			self.co = self.getParsedHeaderInstance("Contact")
			self.co.uri.protocol = "sip"
			self.co.uri.username = self.redirect_user_name
			self.co.uri.host = Config.LOCAL_IP
			self.co.uri.port = Config.LOCAL_PORT
			if (self.neh.port != 5060):
				self.co.uri.port = self.neh.port
			self.co.uri.params = ['transport=UDP']
			repl302.setParsedHeaderValue("Contact", self.co)
			repl302.setHeaderValue("Contact", self.co.create())
			self.writeMessageToNetwork(self.neh, repl302)
			self.redirected = 1
			ack = self.readRequestFromNetwork(self.neh)
			if ack is None:
				self.addResult(TestCase.TC_ERROR, "missing ACK for 302 reply")
		else:
			self.redinv = message
			repl = self.createReply(603, "Decline")
			self.writeMessageToNetwork(self.neh, repl)
			ack = self.readRequestFromNetwork(self.neh)
			if ack is None:
				self.addResult(TestCase.TC_ERROR, "missing ACK for 603")
