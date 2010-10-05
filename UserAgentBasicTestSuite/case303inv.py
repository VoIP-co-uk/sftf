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
# $Id: case303inv.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case303inv (TestCase):

	def config(self):
		self.name = "Case 303inv"
		self.description = "Digest Authentication of INVITE with qop"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)
		
		#if not self.userInteraction("case303inv: proceed when ready to send a INVITE"):
		#	neh.closeSock()
		#	return

		print "  !!!!  PLEASE CALL ANY NUMBER/USER WITHIN 1 MINUTE  !!!!"
		self.challenged = 0
		req = self.readRequestFromNetwork(self.neh, 60)

		if req is None:
			self.addResult(TestCase.TC_ERROR, "missing INVITE request")
			self.neh.closeSock()
			return

		req = self.readRequestFromNetwork(self.neh)

		if req is None:
			self.addResult(TestCase.TC_ERROR, "missing INVITE after sending 401 on first")
		else:
			if req.hasParsedHeaderField("Authorization"):
				auth_p = req.getParsedHeaderValue("Authorization")
				ret = auth_p.verify(req.getHeaderValue("Authorization"))
				if ret:
					Log.logDebug("case303inv: warnings or errors about the Authorization header, see test log", 1)
					Log.logTest("case303inv: warnings or errors about the Authorization header, see WARNINGS above")
					self.results.extend(ret)
				if self.first_inv.hasParsedHeaderField("CSeq") and self.inv.hasParsedHeaderField("CSeq"):
					if (self.inv.getParsedHeaderValue("CSeq").number <= self.first_inv.getParsedHeaderValue("CSeq").number) and (self.inv.getParsedHeaderValue("CallID") == self.first_inv.getParsedHeaderValue("CallID")):
						self.addResult(TestCase.TC_WARN, "CSeq number was not increased for authorization")
			else:
				if req.hasHeaderField("Authorization"):
					Log.logDebug("case303inv: failed to parse the given Authorization header", 1)
					Log.logTest("case303inv: unable to parse the Authorization header")
					self.addResult(TestCase.TC_ERROR, "failed to parse Authorization header")
				else:
					Log.logDebug("case303inv: missing Authorization header in request", 1)
					Log.logTest("case303inv: missing Authorization header in request")
					self.addResult(TestCase.TC_FAILED, "missing Authorization header in request")
	
			if self.checkAuthResponse(req):
				Log.logDebug("case303inv: authenticaton reply is valid", 2)
				Log.logTest("case303inv: authenticaton reply is valid")
				self.addResult(TestCase.TC_PASSED, "authentication reply is valid")
			else:
				Log.logDebug("case303inv: authentication reply is NOT valid", 1)
				Log.logTest("case303inv: authentication reply is NOT valid")
				self.addResult(TestCase.TC_FAILED, "wrong authentication reply")

		self.neh.closeSock()

	def onINVITE(self, message):
		if self.challenged == 0:
			self.first_inv = message
			repl = self.createChallenge(mes=message, qop=True)
			self.writeMessageToNetwork(self.neh, repl)
			self.challenged = 1
			ack = self.readRequestFromNetwork(self.neh)
			if ack is None:
				self.addResult(TestCase.TC_ERROR, "missing ACK on 401")
		else:
			self.inv = message
			repl = self.createReply(404, "Not Found")
			self.writeMessageToNetwork(self.neh, repl)
			ack = self.readRequestFromNetwork(self.neh)
			if ack is None:
				self.addResult(TestCase.TC_ERROR, "missing ACK on 404")
