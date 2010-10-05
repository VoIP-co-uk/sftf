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
# $Id: case509.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case509 (TestCase):

	def config(self):
		self.name = "Case 509"
		self.description = "Proper To-tag use after receipt of multiple 18x"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.testtag1 = "SC-test-tag-1"
		self.testtag2 = "SC-test-tag-2"
		self.testtag3 = "SC-test-tag-3"
		self.ack = None

		self.neh = NEH.NetworkEventHandler(self.transport)

		#if not self.userInteraction("case509: proceed when ready to send INVITE"):
		#	neh.closeSock()
		#	return

		self.rejected = 0
		while self.rejected == 0:
			print "  !!!! PLEASE CALL ANY NUMBER/USER  !!!!"
			req = self.readMessageFromNetwork(self.neh)

		self.neh.closeSock()

		if (req is not None) and (self.ack is not None):
			if self.ack.hasParsedHeaderField("To"):
				ack_to = self.ack.getParsedHeaderValue("To")
			else:
				Log.logDebug("case509: missing To in ACK", 1)
				Log.logTest("case509: missing To in ACK")
				self.addResult(TestCase.TC_ERROR, "missing To in ACK")

			if ack_to.tag == self.testtag2:
				Log.logDebug("case509: To-tag in ACK matches tag from correct 180", 2)
				Log.logTest("case509: To-tag in ACK matches tag from correct 180")
				self.addResult(TestCase.TC_PASSED, "To-tag in ACK matches correct 180 tag")
			else:
				Log.logDebug("case509: To-tag in ACK (\'" + str(ack_to.tag) + "\') differes from tag in 603 (\'" + str(self.testtag2) + "\')", 1)
				Log.logTest("case509: To-tag in ACK differes from tag in 603")
				if ack_to.tag == self.testtag1:
					Log.logTest("case509: wrong To-tag from first 180 is used")
				elif ack_to.tag == self.testtag3:
					Log.logTest("case509: wrong To-tag from third 180 is used")
				self.addResult(TestCase.TC_FAILED, "To-tag in ACK differes from tag in 603")
		elif (self.ack is None):
			self.addResult(TestCase.TC_ERROR, "missing ACK on 603 to check the correct use of the To-tag")


	def onINVITE(self, message):
		repl180first = self.createReply(180, "Ringing")
		to = repl180first.getParsedHeaderValue("To")
		if to is None:
			Log.logDebug("case509: To header missing in request", 1)
			Log.logTest("case509: To header missing in request")
			self.addResult(TestCase.TC_ERROR, "To header missing in request")
		to.tag = self.testtag1
		repl180first.setHeaderValue("To", to.create())
		self.writeMessageToNetwork(self.neh, repl180first)

		repl180sec = self.createReply(180, "Ringing")
		to = repl180sec.getParsedHeaderValue("To")
		if to is None:
			Log.logDebug("case509: To header missing in request", 1)
			Log.logTest("case509: To header missing in request")
			self.addResult(TestCase.TC_ERROR, "To header missing in request")
		to.tag = self.testtag2
		repl180sec.setHeaderValue("To", to.create())
		self.writeMessageToNetwork(self.neh, repl180sec)

		repl180trd = self.createReply(180, "Ringing")
		to = repl180trd.getParsedHeaderValue("To")
		if to is None:
			Log.logDebug("case509: To header missing in request", 1)
			Log.logTest("case509: To header missing in request")
			self.addResult(TestCase.TC_ERROR, "To header missing in request")
		to.tag = self.testtag3
		repl180trd.setHeaderValue("To", to.create())
		self.writeMessageToNetwork(self.neh, repl180trd)

		repl603 = self.createReply(603, "Decline")
		to = repl603.getParsedHeaderValue("To")
		if to is None:
			Log.logDebug("case509: To header missing in request", 1)
			Log.logTest("case509: To header missing in request")
			self.addResult(TestCase.TC_ERROR, "To header missing in request")
		to.tag = self.testtag2
		repl603.setHeaderValue("To", to.create())
		self.rejected = 1
		self.writeMessageToNetwork(self.neh, repl603)
		
		self.ack = self.readRequestFromNetwork(self.neh)
		if self.ack is None:
			self.addResult(TestCase.TC_ERROR, "missing ACK for 603")
