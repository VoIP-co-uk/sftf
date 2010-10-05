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
# $Id: case206.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case206 (TestCase):

	def config(self):
		self.name = "Case 206"
		self.description = "Unusual reason phrase"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		#if not self.userInteraction("case206: proceed when ready to send INVITE"):
		#	neh.closeSock()
		#	return

		self.challenged = 0
		print "  !!!! PLEASE CALL ANY NUMBER/USER WITHIN 1 MINUITE  !!!!"
		req = self.readMessageFromNetwork(self.neh, 60)

		if req is None:
			self.addResult(TestCase.TC_ERROR, "missing INVITE request")
		else:
			if self.dialog[0].transaction[0].lastACK is not None:
				self.addResult(TestCase.TC_PASSED, "received ACK for 404 without reason phrase")

		self.neh.closeSock()

	def onINVITE(self, message):
		Log.logTest("sending 404 without reason for the received INVITE")
		repl = self.createReply(404, "")
		self.writeMessageToNetwork(self.neh, repl)
		ack = self.readMessageFromNetwork(self.neh)
		if ack is None:
			self.addResult(TestCase.TC_FAILED, "missing ACK on 404 without reason")
