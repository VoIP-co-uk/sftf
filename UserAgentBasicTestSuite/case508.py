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
# $Id: case508.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log, Config

class case508 (TestCase):

	def config(self):
		self.name = "Case 508"
		#FIXME should also test auth and not only 302
		self.description = "To-tag resetting after 3xx"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.testtag = "SC-test-tag"
		self.redirect_user_name = "redirect"

		self.neh = NEH.NetworkEventHandler(self.transport)

		#if not self.userInteraction("case508: proceed when ready to send INVITE"):
		#	neh.closeSock()
		#	return

		self.redirected = 0
		self.rejected = 0
		self.end = 0

		while self.end == 0:
			if self.redirected == 0:
				print "  !!!! PLEASE CALL ANY NUMBER/USER  !!!!"
			req = self.readMessageFromNetwork(self.neh)
			if req is None:
				if self.redirected == 1:
					self.addResult(TestCase.TC_FAILED, "did not received redirected INVITE")
				else:
					self.addResult(TestCase.TC_ERROR, "missing reply on request")
				self.end = 1

		self.neh.closeSock()


		if self.rejected == 1:
			if self.first_to.tag == self.new_to.tag:
				Log.logDebug("case508: To-tag in redirected INVITE matches tag in original INVITE", 2)
				Log.logTest("case508: To-tag in redirected INVITE matches tag in original INVITE")
				self.addResult(TestCase.TC_PASSED, "To-tag is equal in redirected INVITE and original INVITE")
			elif self.new_to.tag is not None:
				if self.new_to.tag == self.testtag:
					Log.logDebug("case508: To-tag in redirected INVITE is from redirect response", 1)
					Log.logTest("case508: To-tag in redirected INVITE is from redirect response")
					self.addResult(TestCase.TC_FAILED, "redirected INVITE To-tag from 302")
				else:
					Log.logDebug("case508: To-tag in redirected INVITE is not equal to the INVITE tag", 2)
					Log.logTest("case508: To-tag in redirected INVITE is not equal to the INVITE tag")
					self.addResult(TestCase.TC_WARN, "redirected INVITE and INVITE To-tags are not equal")
			else:
				Log.logDebug("case508: To-tag in redirected INVITE is not equal to the INVITE tag", 2)
				Log.logTest("case508: To-tag in redirected INVITE is not equal to the INVITE tag")
				self.addResult(TestCase.TC_WARN, "redirected INVITE and INVITE To-tags are not equal")
			


	def onINVITE(self, message):
		if self.redirected == 0:
			if message.hasParsedHeaderField("To"):
				self.first_to = message.getParsedHeaderValue("To")
			else:
				Log.logDebug("case508: missing To in INVITE", 1)
				Log.logTest("case508: missing To in INVITE")
				self.addResult(TestCase.TC_ERROR, "missing To in INVITE")
			repl302 = self.createReply(302, "Moved Temporarily")
			to = repl302.getParsedHeaderValue("To")
			if to is None:
				Log.logDebug("case508: To header missing in request", 1)
				Log.logTest("case508: To header missing in request")
				self.addResult(TestCase.TC_ERROR, "To header missing in request")
			to.tag = self.testtag
			repl302.setHeaderValue("To", to.create())
			co = self.getParsedHeaderInstance("Contact")
			co.uri.protocol = "sip"
			co.uri.username = self.redirect_user_name
			co.uri.host = Config.LOCAL_IP
			if (self.neh.port != 5060):
				co.uri.port = self.neh.port
			co.uri.params = ['transport=UDP']
			repl302.setHeaderValue("Contact", co.create())
			self.writeMessageToNetwork(self.neh, repl302)
			self.redirected = 1
			ack = self.readRequestFromNetwork(self.neh)
			if ack is None:
				self.addResult(TestCase.TC_ERROR, "missing ACK for 302")
		else:
			if message.hasParsedHeaderField("To"):
				self.new_to = message.getParsedHeaderValue("To")
			else:
				Log.logDebug("case508: missing To in redirected INVITE", 1)
				Log.logTest("case508: missing To in redirected INVITE")
				self.addResult(TestCase.TC_ERROR, "missing To in redirected INVITE")
			repl = self.createReply(603, "Decline")
			self.writeMessageToNetwork(self.neh, repl)
			self.rejected = 1
			self.end = 1
			ack = self.readRequestFromNetwork(self.neh)
			if ack is None:
				self.addResult(TestCase.TC_ERROR, "missing ACK for 603")
