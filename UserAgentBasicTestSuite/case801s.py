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
# $Id: case801s.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case801s (TestCase):

	def config(self):
		self.name = "Case 801s"
		self.description = "Presence of the rport parameter in Via"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)
		
		#if not self.userInteraction("case801s: proceed when ready to send INVITE"):
		#	neh.closeSock()
		#	return

		print "  !!!!  PLEASE CALL ANY NUMBER/USER WITHIN 1 MINUTE  !!!!"
		req = self.readRequestFromNetwork(self.neh, 60)

		self.neh.closeSock()

		if req is None:
			self.addResult(TestCase.TC_ERROR, "missing INVITE request")
		else:
			if req.hasHeaderField("Via"):
				if req.hasParsedHeaderField("Via"):
					via = req.getParsedHeaderValue("Via")
					if via.rport is None:
						Log.logDebug("case801s: parsed Via does not contain rport", 1)
						Log.logTest("case801s: Via does not contain rport")
						self.addResult(TestCase.TC_WARN, "missing rport in Via")
					else:
						Log.logDebug("case801s: Via contains rport", 2)
						Log.logTest("case801s: Via contains rport")
						self.addResult(TestCase.TC_PASSED, "Via contains rport")
				else:
					Log.logDebug("case801s: unable to find parsed Via header", 1)
					Log.logTest("case801s: unable to find parsed Via header")
					self.addResult(TestCase.TC_ERROR, "missing parsed Via header")
			else:
				Log.logDebug("case801s: unable to find Via header in request", 1)
				Log.logTest("case801s: unable to find Via header in request")
				self.addResult(TestCase.TC_ERROR, "missing Via header in request")

	def onINVITE(self, message):
		repl = self.createReply(603, "Decline")
		self.writeMessageToNetwork(self.neh, repl)
		ack = self.readRequestFromNetwork(self.neh)
		if ack is None:
			self.addResult(TestCase.TC_ERROR, "missing ACK for 603 reply")
