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
# $Id: case502can.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log
from SCException import SCException

class case502can (TestCase):

	def config(self):
		self.name = "Case 502can"
		self.description = "Proper Generation of transaction ID"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		#if not self.userInteraction("case502can: proceed when ready to send INVITE"):
		#	neh.closeSock()
		#	return

		self.canceled = 0
		self.invited = 0

		while self.canceled == 0:
			if self.invited == 0:
				print "  !!!! PLEASE CALL ANY NUMBER/USER  !!!!"
			else:
				print "  !!!! PLEASE CANCEL/HANGUP THE CALL !!!!"
			req = self.readRequestFromNetwork(self.neh)

		self.neh.closeSock()

		if self.invited == 1:
			if self.first_inv.hasParsedHeaderField("Via"):
				via = self.first_inv.getParsedHeaderValue("Via")
				if via.branch is not None:
					first_branch = via.branch
				else:
					Log.logDebug("case502can: INVITE's Via misses required branch", 1)
					Log.logTest("case502can: INVITE's Via misses required branch")
					self.addResult(TestCase.TC_WARN, "Via in INVITE misses branch")
			else:
				Log.logDebug("case502can: missing Via in INVITE request", 1)
				Log.logTest("case502can: missing Via in INVITE request")
				self.addResult(TestCase.TC_ERROR, "missing Via in request")
		else:
			self.addResult(TestCase.TC_ERROR, "missing INVITE request")

		if self.canceled == 1:
			if self.cancel.hasParsedHeaderField("Via"):
				new_via = self.cancel.getParsedHeaderValue("Via")
				if new_via.branch is not None:
					cancel_branch = new_via.branch
					if first_branch == cancel_branch:
						Log.logDebug("case502can: branches matching", 2)
						Log.logTest("case502can: branches matching")
						self.addResult(TestCase.TC_PASSED, "branches in CANCEL and INVITE are equal")
					else:
						Log.logDebug("case502can: branches from INVITE (" + str(first_branch) + ") and CANCEL (" + str(cancel_branch) + ") are NOT equal", 1)
						Log.logTest("case502can: branches from INVITE and CANCEL are NOT equal")
						self.addResult(TestCase.TC_WARN, "INVITE and CANCEL branches differ")

				else:
					Log.logDebug("case502can: CANCEL's Via misses required branch", 1)
					Log.logTest("case502can: CANCEL's Via misses required branch")
					self.addResult(TestCase.TC_WARN, "Via in CANCEL misses branch")
			else:
				Log.logDebug("case502can: missing Via in CANCEL", 1)
				Log.logTest("case502can: missing Via in CANCEL")
				self.addResult(TestCase.TC_ERROR, "missing Via in CANCEL")
		else:
			self.addReuslt(TestCase.TC_ERROR, "missing CANCEL request")


	def onINVITE(self, message):
		self.invited = 1
		self.first_inv = message
		repl180 = self.createReply(180, "Ringing")
		self.writeMessageToNetwork(self.neh, repl180)
		print "  !!!!  PLEASE CANCEL/HANGUP THE CALL  !!!!"

	def onCANCEL(self, message):
		self.cancel = message
		self.canceled = 1
		repl200 = self.createReply(200, "OK", mes=message)
		self.writeMessageToNetwork(self.neh, repl200)
		repl487 = self.createReply(487, "Request Terminated", mes=self.first_inv)
		self.writeMessageToNetwork(self.neh, repl487)
		ack = self.readRequestFromNetwork(self.neh)
		if ack is None:
			self.addResult(TestCase.TC_ERROR, "missing ACK for 487")
