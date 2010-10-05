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
# $Id: case502ack.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log
from SCException import SCException

class case502ack (TestCase):

	def config(self):
		self.name = "Case 502ack"
		self.description = "Proper Generation of transaction ID"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		#if not self.userInteraction("case502ack: proceed when ready to send INVITE"):
		#	neh.closeSock()
		#	return

		self.ack = None
		self.invited = 0

		while self.invited == 0:
			print "  !!!! PLEASE CALL ANY NUMBER/USER  !!!!"
			req = self.readRequestFromNetwork(self.neh)

		self.neh.closeSock()

		if self.invited == 1:
			if self.first_inv.hasParsedHeaderField("Via"):
				via = self.first_inv.getParsedHeaderValue("Via")
				if via.branch is not None:
					first_branch = via.branch
				else:
					Log.logDebug("case502ack: INVITE's Via misses required branch", 1)
					Log.logTest("case502ack: INVITE's Via misses required branch")
					self.addResult(TestCase.TC_WARN, "Via in INVITE misses branch")
			else:
				Log.logDebug("case502ack: missing Via in INVITE request", 1)
				Log.logTest("case502ack: missing Via in INVITE request")
				self.addResult(TestCase.TC_ERROR, "missing Via in request")
		else:
			self.addResult(TestCase.TC_ERROR, "missing INVITE request")

		if self.ack is not None:
			if self.ack.hasParsedHeaderField("Via"):
				new_via = self.ack.getParsedHeaderValue("Via")
				if new_via.branch is not None:
					ack = new_via.branch
					if first_branch == ack:
						Log.logDebug("case502ack: branches matching", 2)
						Log.logTest("case502ack: branches matching")
						self.addResult(TestCase.TC_PASSED, "branches in ACK and INVITE are equal")
					else:
						Log.logDebug("case502ack: branches from INVITE (" + str(first_branch) + ") and ACK (" + str(ack) + ") are NOT equal", 1)
						Log.logTest("case502ack: branches from INVITE and ACK are NOT equal")
						self.addResult(TestCase.TC_WARN, "INVITE and ACK branches differ")

				else:
					Log.logDebug("case502ack: ACK's Via misses required branch", 1)
					Log.logTest("case502ack: ACK's Via misses required branch")
					self.addResult(TestCase.TC_WARN, "Via in ACK misses branch")
			else:
				Log.logDebug("case502ack: missing Via in ACK", 1)
				Log.logTest("case502ack: missing Via in ACK")
				self.addResult(TestCase.TC_ERROR, "missing Via in ACK")
		else:
			self.addResult(TestCase.TC_ERROR, "missing ACK request")


	def onINVITE(self, message):
		self.invited = 1
		self.first_inv = message
		repl404 = self.createReply(404, "Not Found")
		self.writeMessageToNetwork(self.neh, repl404)
		self.ack = self.readRequestFromNetwork(self.neh)
		if self.ack is None:
			self.addResult(TestCase.TC_ERROR, "missing ACK on 404")
