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
# $Id: case225close.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log, time

class case225close (TestCase):

	def config(self):
		self.name = "Case 225close"
		self.description = "TCP handling (reopening after UAS closed)"
		self.isClient = True
		self.transport = "TCP"
		self.interactRequired = False

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		self.end = False
		self.invited = False
		self.connected = False

		while not self.end:
			if self.invited:
				print "  !!!!  PLEASE CALL ANY NUMBER/NAME WITHIN 60 SECONDS OVER TCP  !!!!"
			elif self.connected:
				print "  !!!!  PLEASE TERMINATE/HANGUP THE CALL  !!!!"
			repl = self.readMessageFromNetwork(self.neh, 60, TimeoutError=False)
			if repl is None:
				if not self.invited:
					self.addResult(TestCase.TC_ERROR, "did not received INVITE over TCP")
				elif self.neh.state != NEH.NetworkEventHandler.NEH_CONNECTED:
					self.addResult(TestCase.TC_FAILED, "TCP connection was not reopened by UA after closing")
				else:
					self.addResult(TestCase.TC_ERROR, "did not received BYE on the reopened TCP connection")

				self.end = True

		self.neh.closeSock()

	def onINVITE(self, message):
		Log.logTest("received INVITE over TCP, replying with 200")
		self.invited = True
		repl200 = self.createReply(200, "OK", message)
		co = repl200.getParsedHeaderValue("Contact")
		co.uri.params.append("transport=TCP")
		repl200.setHeaderValue("Contact", co.create())
		self.writeMessageToNetwork(self.neh, repl200)

	def onACK(self, message):
		Log.logTest("received ACK")
		self.connected = True
		Log.logTest("closing TCP connection")
		self.neh.close()
		self.neh = NEH.NetworkEventHandler(self.transport)
		Log.logTest("sleeping for 3 seconds...")
		time.sleep(3)

	def onBYE(self, message):
		self.addResult(TestCase.TC_PASSED, "received BYE over reopened connection")
		Log.logTest("sending 200 on BYE")
		repl = self.createReply(200, "OK", message)
		self.writeMessageToNetwork(self.neh, repl)
		self.end = True
