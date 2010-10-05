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
# $Id: case304.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
from SCException import SCException
import NetworkEventHandler as NEH
import Log, Helper

class case304 (TestCase):

	def config(self):
		self.name = "Case 304"
		self.description = "Authentication retry timer"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True
		self.register = True

	def run(self):
		self.required_min_delay = 3.0

		self.neh = NEH.NetworkEventHandler(self.transport)
		
		#if not self.userInteraction("case304: proceed when ready to send REGISTER"):
		#	neh.closeSock()
		#	return

		self.challenged = 0
		print "  !!!!  PLEASE REGISTER WITHIN 5 MINUTES  !!!!"
		self.old_req = self.readMessageFromNetwork(self.neh, 300)

		if self.old_req is None:
			self.addResult(TestCase.TC_ERROR, "missing REGISTER request")
			self.neh.closeSock()
			return

		self.last_delay = self.smallest_delay = 0
		for i in range(0, 3):

			try:
				self.new_req = self.readMessageFromNetwork(self.neh, 2*self.required_min_delay, False, RequestMethod="REGISTER")
			except SCException:
				Log.logDebug("case304: smallest delay between retries was: " + str(self.smallest_delay) + "sec", 2)
				Log.logTest("case304: smallest delay between retries was: " + str(self.smallest_delay) + "sec")
				if i == 0:
					Log.logDebug("case304: timeout after first 401, failed to answer the challenge", 1)
					Log.logTest("case304: timeout after sending first 401")
					self.addResult(TestCase.TC_WARN, "timeout after sending first 401")
				elif i == 1:
					if self.smallest_delay < self.required_min_delay:
						Log.logDebug("case304: timeout after sending second 401", 2)
						Log.logTest("case304: tried authentication only one time")
						self.addResult(TestCase.TC_PASSED, "tried authentication only one time")
					else:
						Log.logDebug("case304: timeout after sending second 401, but delay was big enough to retype password", 2)
						Log.logTest("case304: tried authentication only one time")
						self.addResult(TestCase.TC_PASSED, "tried authentication only one time")
				else:
					Log.logDebug("case304: timeout after third 401, but tried to authenticate two times", 1)
					Log.logTest("case304: timeout after sending third 401")
					self.addResult(TestCase.TC_WARN, "timeout after sending third 401")
				self.neh.closeSock()
				return

		Log.logDebug("case304: retired registration three times with same credentials", 1)
		Log.logTest("case304: retired registration three times with same credentials")
		self.addResult(TestCase.TC_FAILED, "retired registration three times with same credentials")

		self.neh.closeSock()

	def onREGISTER(self, message):
		if self.challenged == 0:
			repl401 = self.createChallenge(mes=message)
			self.challenged = 1
			self.writeMessageToNetwork(self.neh, repl401)
		else:
			# dont count the delay between the first un-authorized request
			# and the re-send request with authorization
			self.new_req = message
			if not ((not self.old_req.hasHeaderField("Authorization")) and self.new_req.hasHeaderField("Authorization")):
				self.last_delay = Helper.eventTimeDiff(self.new_req.event, self.old_req.event)
				if self.smallest_delay == 0:
					self.smallest_delay = self.last_delay
				if self.last_delay < self.smallest_delay :
					self.smallest_delay = self.last_delay

			repl = self.createChallenge(mes=message)
			self.writeMessageToNetwork(self.neh, repl)

			self.old_req = self.new_req
