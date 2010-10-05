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
# $Id: case224.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case224 (TestCase):

	def config(self):
		self.name = "Case 224"
		self.description = "OPTIONS support"
		self.isClient = True
		self.transport = "UDP"

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		inv = self.createRequest("OPTIONS")
		self.writeMessageToNetwork(self.neh, inv)

		self.code = 0
		while (self.code < 200):
			repl = self.readReplyFromNetwork(self.neh)
			if (repl is not None) and (repl.code > self.code):
				self.code = repl.code
			elif repl is None:
				self.code = 999

		if repl is None:
			self.addResult(TestCase.TC_FAILED, "missing reply on request")
		self.neh.closeSock()

	def onDefaultCode(self, message):
		if message.code > self.code:
			self.code = message.code
		if message.code == 200:
			#FIXME should we also check the content of the 200?
			self.addResult(TestCase.TC_PASSED, "OPTIONS answered with 200")
			if (len(message.body) > 0):
				self.addResult(TestCase.TC_WARN, "no body expected in OPTIONS reply")
		else:
			self.addResult(TestCase.TC_FAILED, "OPTIONS request rejected")
