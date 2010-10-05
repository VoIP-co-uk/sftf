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
# $Id: case301.py,v 1.3 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log, Config

class case301 (TestCase):

	def config(self):
		self.name = "Case 301"
		self.description = "Digest Authentication of REGISTER without qop"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True
		self.register = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)
		
		#if not self.userInteraction("case301: proceed when ready to send REGISTER"):
		#	neh.closeSock()
		#	return

		print "  !!!! PLEASE REGISTER WITH USERNAME='" + str(Config.TEST_USER_NAME) + "' and PASSWORD='" + str(Config.TEST_USER_PASSWORD) + "' WITHIN 5 MINUTES !!!!"
		self.challenged = 0
		req = self.readMessageFromNetwork(self.neh, 300, RequestMethod="REGISTER")

		if req is None:
			self.addResult(TestCase.TC_ERROR, "missing REGISTER request")
			self.neh.closeSock()
			return

		reg = self.readMessageFromNetwork(self.neh, 60, RequestMethod="REGISTER")

		if reg is None:
			self.addResult(TestCase.TC_ERROR, "missing REGISTER after challenge")
		else:
			if reg.hasParsedHeaderField("Authorization"):
				auth_p = reg.getParsedHeaderValue("Authorization")
				ret = auth_p.verify(reg.getHeaderValue("Authorization"))
				if ret:
					Log.logDebug("case301: warnings or errors about the Authorization header, see test results", 1)
					Log.logTest("case301: warnings or erros about the Authorization header, see test results")
					self.results.extend(ret)
				if reg.hasParsedHeaderField("CSeq") and req.hasParsedHeaderField("CSeq"):
					if (reg.getParsedHeaderValue("CSeq").number <= req.getParsedHeaderValue("CSeq").number) and (reg.getParsedHeaderValue("CallID") == req.getParsedHeaderValue("CallID")):
						self.addResult(TestCase.TC_WARN, "CSeq number was not increased for authorization")
			else:
				if reg.hasHeaderField("Authorization"):
					Log.logDebug("case301: failed to parse the given Authorization header", 1)
					Log.logTest("case301: unable to parse the Authorization header")
					self.addResult(TestCase.TC_ERROR, "failed to parse Authorization header")
				else:
					Log.logDebug("case301: missing Authorization header in request", 1)
					Log.logTest("case301: missing Authorization header in request")
					self.addResult(TestCase.TC_FAILED, "missing Authorization header in request")

			if reg.hasParsedHeaderField("From"):
				fm = reg.getParsedHeaderValue("From")
				if (not NEH.compareHostNames(fm.uri.host, Config.LOCAL_IP)) and (not NEH.compareHostNames(fm.uri.host, Config.LOCAL_HOSTNAME)):
					self.addResult(TestCase.TC_FAILED, "host part of From URI does not contain the SFTF host")
			else:
				self.addResult(TestCase.TC_ERROR, "missing parsed From in REGSITER")

			if self.checkAuthResponse(reg):
				Log.logDebug("case301: authenticaton reply is valid", 2)
				Log.logTest("case301: authenticaton reply is valid")
				self.addResult(TestCase.TC_PASSED, "authentication reply is valid")
			else:
				Log.logDebug("case301: authentication reply is NOT valid", 1)
				Log.logTest("case301: authentication reply is NOT valid")
				self.addResult(TestCase.TC_FAILED, "wrong authentication reply")

		self.neh.closeSock()

	def onREGISTER(self, message):
		if self.challenged == 0:
			chal = self.createChallenge(mes=message)
			self.writeMessageToNetwork(self.neh, chal)
			self.challenged = 1
		else:
			repl = self.createReply(200, "OK", message)
			self.writeMessageToNetwork(self.neh, repl)
