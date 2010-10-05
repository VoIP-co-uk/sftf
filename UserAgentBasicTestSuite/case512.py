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
# $Id: case512.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case512 (TestCase):

	def config(self):
		self.name = "Case 512"
		self.description = "To-tag in CANCEL"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.testtag = "SC-test-tag"

		self.neh = NEH.NetworkEventHandler(self.transport)

		#if not self.userInteraction("case512: proceed when ready to send INVITE"):
		#	neh.closeSock()
		#	return

		self.invited = 0
		self.canceled = 0
		while self.canceled == 0:
			if self.invited == 0:
				print "  !!!! PLEASE CALL ANY NUMBER/USER  !!!!"
			else:
				print "  !!!! PLEASE CANCEL/HANGUP THE CALL  !!!!"
			req = self.readMessageFromNetwork(self.neh)

		self.neh.closeSock()

		if self.canceled == 1:
			if self.first_to.tag == self.new_to.tag:
				Log.logDebug("case512: To-tag in CANCEL matches tag in INVITE", 2)
				Log.logTest("case512: To-tag in CANCEL matches tag in INVITE")
				self.addResult(TestCase.TC_PASSED, "To-tag is equal in CANCEL and INVITE")
			elif self.new_to.tag is not None:
				if self.new_to.tag == self.testtag:
					Log.logDebug("case512: To-tag in CANCEL is from provisional response", 1)
					Log.logTest("case512: To-tag in CANCEL is from provisional response")
					self.addResult(TestCase.TC_FAILED, "CANCEL To-tag from provisional response")
				else:
					Log.logDebug("case512: To-tag in CANCEL is not equal to the INVITE tag", 2)
					Log.logTest("case512: To-tag in CANCEL is not equal to the INVITE tag")
					self.addResult(TestCase.TC_WARN, "CANCEL and INVITE To-tags are not equal")
			else:
				Log.logDebug("case512: To-tag in CANCEL is not equal to the INVITE tag", 2)
				Log.logTest("case512: To-tag in CANCEL is not equal to the INVITE tag")
				self.addResult(TestCase.TC_WARN, "CANCEL and INVITE To-tags are not equal")

	def onINVITE(self, message):
		self.inv = message
		if message.hasParsedHeaderField("To"):
			self.first_to = message.getParsedHeaderValue("To")
		else:
			Log.logDebug("case512: missing To in INVITE", 1)
			Log.logTest("case512: missing To in INVITE")
			self.addResult(TestCase.TC_ERROR, "missing To in INVITE")
		repl180 = self.createReply(180, "Ringing")
		to = repl180.getParsedHeaderValue("To")
		if to is None:
			Log.logDebug("case512: To header missing in request", 1)
			Log.logTest("case512: To header missing in request")
			self.addResult(TestCase.TC_ERROR, "To header missing in request")
		else:
			to.tag = self.testtag
			repl180.setHeaderValue("To", to.create())
		self.invited = 1
		self.writeMessageToNetwork(self.neh, repl180)

	def onCANCEL(self, message):
		if message.hasParsedHeaderField("To"):
			self.new_to = message.getParsedHeaderValue("To")
		else:
			Log.logDebug("case512: missing To in CANCEL", 1)
			Log.logTest("case512: missing To in CANCEL")
			self.addResult(TestCase.TC_ERROR, "missing To in CANCEL")
		repl200 = self.createReply(200, "OK", mes=message)
		self.writeMessageToNetwork(self.neh, repl200)
		repl487 = self.createReply(487, "Request Terminated", mes=self.inv)
		self.canceled = 1
		self.writeMessageToNetwork(self.neh, repl487)
		ack = self.readRequestFromNetwork(self.neh)
		if ack is None:
			self.addResult(TestCase.TC_ERROR, "missing ACK for 487")
