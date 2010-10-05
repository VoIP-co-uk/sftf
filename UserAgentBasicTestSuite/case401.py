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
# $Id: case401.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log, Helper
from SCException import SCException

class case401 (TestCase):

	def config(self):
		self.name = "Case 401"
		self.description = "Server-driven re-registration period"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True
		self.register = True

	def run(self):
		self.reregister_time = float(30)

		self.neh = NEH.NetworkEventHandler(self.transport)

		#if not self.userInteraction("case401: proceed when ready to send REGISTER"):
		#	neh.closeSock()
		#	return

		print "  !!!! PLEASE REGISTER WITHIN 5 MINUTES  !!!!"
		self.redriven = 0
		old_req = self.readRequestFromNetwork(self.neh, 300)

		if old_req is None:
			self.addResult(TestCase.TC_ERROR, "missing REGISTER request")
			self.neh.closeSock()
			return

		try:
			new_req = self.readRequestFromNetwork(self.neh, 1.2*self.reregister_time, False)
		except SCException:
			Log.logDebug("case401: timeout after " + str(1.2*self.reregister_time) + "sec, allthough Contact expired after " + str(self.reregister_time) + "sec", 1)
			Log.logTest("case401: did not receive REGISTER before timeout")
			self.addResult(TestCase.TC_FAILED, "did not reregistered before Contact expired")
			self.neh.closeSock()
			return

		if new_req.method != "REGISTER":
			Log.logDebug("case401: request method != REGISTER", 1)
			Log.logTest("case401: error: expected REGISTER, received " + str(new_req.method))
			self.addResult(TestCase.TC_ERROR, "request method != REGISTER")
			self.neh.closeSock()
			return

		delay = Helper.eventTimeDiff(new_req.event, old_req.event)
		if (delay > (self.reregister_time*0.25)) and (delay < (self.reregister_time*0.75)):
			Log.logDebug("case401: delay between REGISTER is between 0.25 * expires and 0.75 * expires => additional load", 2)
			Log.logTest("case401: received REGISTER far before expires value")
			self.addResult(TestCase.TC_CAUT, "received REGISTER far before (75%) expires value")
		elif (delay >= (self.reregister_time*0.75) and delay <= self.reregister_time):
			Log.logDebug("case401: delay between REGISTER is between 0.75 * expires and expires", 2)
			Log.logTest("case401: received REGISTER shortly before expires")
			self.addResult(TestCase.TC_PASSED, "received REGISTER shortly before expires")
		elif delay > self.reregister_time:
			Log.logDebug("case401: delay between re-REGISTER was " + str(delay) + " sec, which is above the expires value", 1)
			Log.logTest("case401: received re-REGISTER very too late")
			self.addResult(TestCase.TC_FAILED, "received the re-REGISTER too late")
		else:
			Log.logDebug("case401: delay between re-REGISTER was " + str(delay) + " sec, which is below 1/4 of the expires value", 1)
			Log.logTest("case401: received re-REGISTER very much too early")
			self.addResult(TestCase.TC_FAILED, "received the re-REGISTER very much too early")

		self.neh.closeSock()

	def onREGISTER(self, message):
		repl = self.createReply(200, "OK")
		if self.redriven == 0:
			con = repl.getParsedHeaderValue("Contact")
			con.expires = str(int(self.reregister_time))
			repl.setHeaderValue("Contact", con.create())
			self.redriven = 1
		self.writeMessageToNetwork(self.neh, repl)
