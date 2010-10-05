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
# $Id: case302bye.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case302bye (TestCase):

	def config(self):
		self.name = "Case 302bye"
		self.description = "Digest Authentication of BYE without qop"
		self.isClient = True
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)
		
		#if not self.userInteraction("case302bye: proceed when ready to send a INVITE"):
		#	neh.closeSock()
		#	return

		inv = self.createRequest("INVITE")
		self.challenged = 0
		self.writeMessageToNetwork(self.neh, inv)

		self.end = 0
		while self.end == 0:
			req = self.readMessageFromNetwork(self.neh, 10)
			if req is None:
				self.end = 1


		if req is None:
			if self.challenged == 1:
				self.addResult(TestCase.TC_FAILED, "missing BYE after sending challenge (401)")
			else:
				self.addResult(TestCase.TC_ERROR, "missing reply on INVITE")
		else:
			if self.challenged == 1:
				if req.hasParsedHeaderField("Authorization"):
					auth_p = req.getParsedHeaderValue("Authorization")
					ret = auth_p.verify(req.getHeaderValue("Authorization"))
					if ret:
						Log.logDebug("case302bye: warnings or errors about the Authorization header, see test log", 1)
						Log.logTest("case302bye: warnings or errors about the Authorization header, see WARNINGS above")
						self.results.extend(ret)
					if self.first_bye.hasParsedHeaderField("CSeq") and self.bye.hasParsedHeaderField("CSeq"):
						if (self.bye.getParsedHeaderValue("CSeq").number <= self.first_bye.getParsedHeaderValue("CSeq").number) and (self.bye.getParsedHeaderValue("CallID") == self.first_bye.getParsedHeaderValue("CallID")):
							self.addResult(TestCase.TC_WARN, "CSeq number was not increased for authorization")
				else:
					if req.hasHeaderField("Authorization"):
						Log.logDebug("case302bye: failed to parse the given Authorization header", 1)
						Log.logTest("case302bye: unable to parse the Authorization header")
						self.addResult(TestCase.TC_ERROR, "failed to parse Authorization header")
					else:
						Log.logDebug("case302bye: missing Authorization header in request", 1)
						Log.logTest("case302bye: missing Authorization header in request")
						self.addResult(TestCase.TC_FAILED, "missing Authorization header in request")
	
				if self.checkAuthResponse(req):
					Log.logDebug("case302bye: authenticaton reply is valid", 2)
					Log.logTest("case302bye: authenticaton reply is valid")
					self.addResult(TestCase.TC_PASSED, "authentication reply is valid")
				else:
					Log.logDebug("case302bye: authentication reply is NOT valid", 1)
					Log.logTest("case302bye: authentication reply is NOT valid")
					self.addResult(TestCase.TC_FAILED, "wrong authentication reply")

		self.neh.closeSock()

	def on180(self, message):
		print "  !!!!  PLEASE ANSWER/PICKUP THE CALL  !!!!"

	def on183(self, message):
		self.on180(message)

	def on200(self, message):
		ack = self.createRequest("ACK", trans=message.transaction)
		self.writeMessageToNetwork(self.neh, ack)
		print "  !!!! PLEASE TERMINATE/HANGUP THE CALL  !!!!!!"

	def onBYE(self, message):
		if self.challenged == 0:
			self.first_bye = message
			repl = self.createChallenge(mes=message)
			self.writeMessageToNetwork(self.neh, repl)
			self.challenged = 1
		else:
			self.bye = message
			repl = self.createReply(200, "OK")
			self.end = 1
			self.writeMessageToNetwork(self.neh, repl)
