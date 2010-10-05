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
# $Id: case601can.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case601can (TestCase):

	def config(self):
		self.name = "Case 601can"
		self.description = "Proper Generation of CANCEL"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		#if not self.userInteraction("case601can: proceed when ready to send INVITE"):
		#	neh.closeSock()
		#	return

		self.inv = None
		self.can = None
		self.invited = 0
		self.canceled = 0
		while self.canceled == 0:
			if self.invited == 0:
				print "  !!!!  PLEASE CALL ANY NUMBER/USER  !!!!"
			else:
				print "  !!!!  PLEASE CANCEL/HANGUP THE CALL  !!!!"
			req = self.readMessageFromNetwork(self.neh)


		self.neh.closeSock()

		if self.inv is not None:
			if self.inv.hasHeaderField("Via"):
				req_via = self.inv.getHeaderValue("Via")
			else:
				Log.logDebug("case601can: missing Via header in INVITE", 1)
				Log.logTest("case601can: missing Via header in INVITE")
				self.addResult(TestCase.TC_ERROR, "missing Via in first INVITE")
		if self.can is not None:
			if self.can.hasHeaderField("Via"):
				can_via = self.can.getHeaderValue("Via")
			else:
				Log.logDebug("case601can: missing Via header in CANCEL", 1)
				Log.logTest("case601can: missing Via header in CANCEL")
				self.addResult(TestCase.TC_ERROR, "missing Via in CANCEL")

			if self.inv.rUri != self.can.rUri:
				Log.logDebug("case601can: INVITE uri (\'" + str(self.inv.rUri.create()) + "\') and CANCEL uri (\'" + str(self.can.rUri.create()) + "\') differ", 1)
				Log.logTest("case601: INVITE and CANCEL request uri do not match")
				self.addResult(TestCase.TC_FAILED, "INVITE and CANCEL uri differ")
			elif req_via != can_via:
				Log.logDebug("case601can: INVITE topmost Via (\'" + str(req_via) + "\') and CANCEL topmost Via (\'" + str(can_via) + "\') differ", 1)
				Log.logTest("case601can: topmost Via of INVITE and CANCEL differ")
				self.addResult(TestCase.TC_FAILED, "INVITE and CANCEL topmost Via differ")
			else:
				Log.logDebug("case601can: request uri and topmost Via of INVITE and CANCEL are equal", 2)
				Log.logTest("case601can: r-uri and Via of INVITE and CANCEL are equal")
				self.addResult(TestCase.TC_PASSED, "r-uri and Via of INVITE and CANCEL are equal")


	def onINVITE(self, message):
		self.inv = message
		repl180 = self.createReply(180, "Ringing")
		self.writeMessageToNetwork(self.neh, repl180)
		self.invited = 1
	
	def onCANCEL(self, message):
		self.can = message
		repl200 = self.createReply(200, "OK", mes=message)
		self.writeMessageToNetwork(self.neh, repl200)
		repl487 = self.createReply(487, "Request Terminated", mes=self.inv)
		self.writeMessageToNetwork(self.neh, repl487)
		self.canceled = 1
		self.ack = self.readRequestFromNetwork(self.neh)
		if self.ack is None:
			self.addResult(TestCase.TC_ERROR, "missing ACK for 487")
