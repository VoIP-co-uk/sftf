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
# $Id: case303reg.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log, Config

class case303reg (TestCase):

	def config(self):
		self.name = "Case 303reg"
		self.description = "Digest Authentication of REGISTER with qop"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True
		self.register = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)
		
		#if not self.userInteraction("case303reg: proceed when ready to send REGISTER"):
		#	neh.closeSock()
		#	return

		print "  !!!! PLEASE REGISTER WITH USERNAME='" + str(Config.TEST_USER_NAME) + "' and PASSWORD='" + str(Config.TEST_USER_PASSWORD) + "' WITHIN 5 MINUTES !!!!"
		self.challenged = 0
		req = self.readMessageFromNetwork(self.neh, 300, RequestMethod="REGISTER")

		if req is None:
			self.addResult(TestCase.TC_ERROR, "missing REGISTER request")
			self.neh.closeSock()
			return

		reg = self.readMessageFromNetwork(self.neh, RequestMethod="REGISTER")

		if reg is None:
			self.addResult(TestCase.TC_ERROR, "missing REGISTER after challenge")
		else:
			if reg.hasParsedHeaderField("Authorization"):
				auth_p = reg.getParsedHeaderValue("Authorization")
				ret = auth_p.verify(reg.getHeaderValue("Authorization"))
				if ret:
					Log.logDebug("case303reg: warnings or errors about the Authorization header, see test results", 1)
					Log.logTest("case303reg: warnings or erros about the Authorization header, see test results")
					self.results.extend(ret)
				if self.first_reg.hasParsedHeaderField("CSeq") and self.reg.hasParsedHeaderField("CSeq"):
					if (self.reg.getParsedHeaderValue("CSeq").number <= self.first_reg.getParsedHeaderValue("CSeq").number) and (self.reg.getParsedHeaderValue("CallID") == self.first_reg.getParsedHeaderValue("CallID")):
						self.addResult(TestCase.TC_WARN, "CSeq number was not increased for authorization")
			else:
				if reg.hasHeaderField("Authorization"):
					Log.logDebug("case303reg: failed to parse the given Authorization header", 1)
					Log.logTest("case303reg: unable to parse the Authorization header")
					self.addResult(TestCase.TC_ERROR, "failed to parse Authorization header")
				else:
					Log.logDebug("case303reg: missing Authorization header in request", 1)
					Log.logTest("case303reg: missing Authorization header in request")
					self.addResult(TestCase.TC_FAILED, "missing Authorization header in request")

			if self.checkAuthResponse(reg):
				Log.logDebug("case303reg: authenticaton reply is valid", 2)
				Log.logTest("case303reg: authenticaton reply is valid")
				self.addResult(TestCase.TC_PASSED, "authentication reply is valid")
			else:
				Log.logDebug("case303reg: authentication reply is NOT valid", 1)
				Log.logTest("case303reg: authentication reply is NOT valid")
				self.addResult(TestCase.TC_FAILED, "wrong authentication reply")

		self.neh.closeSock()

	def onREGISTER(self, message):
		if self.challenged == 0:
			self.first_reg = message
			chal = self.createChallenge(mes=message, qop=True)
			self.writeMessageToNetwork(self.neh, chal)
			self.challenged = 1
		else:
			self.reg = message
			repl = self.createReply(200, "OK")
			self.writeMessageToNetwork(self.neh, repl)
