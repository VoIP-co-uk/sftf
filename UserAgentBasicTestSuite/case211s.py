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
# $Id: case211s.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case211s (TestCase):

	def config(self):
		self.name = "Case 211s"
		self.description = "Missing Required Header Fields"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		#if not self.userInteraction("case211s: proceed when ready to send INVITE"):
		#	neh.closeSock()
		#	return

		self.end = 0
		print "  !!!! PLEASE CALL ANY NUMBER/USER !!!!"
		while self.end == 0:
			req = self.readRequestFromNetwork(self.neh, TimeoutError=False)


		self.neh.closeSock()

		res = True
		for hf in ("From", "To", "CSeq", "Call-ID"):
			if not self.req.hasHeaderField(hf):
				res = False
				Log.logDebug("case211s: request misses \'" + hf + "\' header field", 1)
				Log.logTest("case211s: request misses \'" + hf + "\' header field")

		if res:
			Log.logDebug("case211s: all mandatory header fields found", 2)
			Log.logTest("case211s: all mandatory header fields present")
			self.addResult(TestCase.TC_PASSED, "all mandatory header fields present")
		else:
			Log.logDebug("case211s: request misses a mandatory header field", 1)
			Log.logTest("case211s: request misses a mandatory header field")
			self.addResult(TestCase.TC_FAILED, "request misses mandatory header field")


	def onINVITE(self, message):
		self.end = 1
		self.req = message
		repl = self.createReply(404, "Not Found")
		self.writeMessageToNetwork(self.neh, repl)
		ack = self.readRequestFromNetwork(self.neh)
		if ack is None:
			self.addResult(TestCase.TC_ERROR, "missing ACK for 404")
