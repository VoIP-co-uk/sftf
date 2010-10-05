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
# $Id: case503s.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log, Config

class case503s (TestCase):

	def config(self):
		self.name = "Case 503s"
		self.description = "Ignore Record-Route from negative replies"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		#if not self.userInteraction("case503s: proceed when ready to send INVITE"):
		#	neh.closeSock()
		#	return

		self.replied = 0
		while self.replied == 0:
			print "  !!!!  PLEASE CALL ANY NUMBER/USER  !!!!"
			self.readMessageFromNetwork(self.neh, 30)

		self.neh.closeSock()

		if self.ack is None:
			self.addResult(TestCase.TC_ERROR, "missing ACK on 404 reply")
		else:
			if self.ack.hasHeaderField("Route"):
				Log.logDebug("case503s: ACK contains Route header (\'" + str(self.ack.getHeaderValue("Route")) + "\') created from RR in 404 reply", 1)
				Log.logTest("case503s: ACK contains Route header from RR in negative reply")
				self.addResult(TestCase.TC_FAILED, "ACK contains Route from RR in negative reply")
			else:
				Log.logDebug("case503s: even though RR in reply, no Route header in ACK", 2)
				Log.logTest("case503s: Route header omitted because of negative reply")
				self.addResult(TestCase.TC_PASSED, "Route header omitted because of negative reply")


	def onINVITE(self, message):
		# FIXME is an ACK ok, or do we need to see another request from the
		# UAC to see it fail?
		repl = self.createReply(404, "Not Found")
		rr = self.getParsedHeaderInstance("Record-Route")
		rr.uri.protocol = "sip"
		rr.uri.host = Config.LOCAL_IP
		rr.uri.port = Config.LOCAL_PORT
		repl.setParsedHeaderValue("Record-Route", rr)
		repl.setHeaderValue("Record-Route", rr.create())
		repl.transaction.dialog.ignoreRoute = True
		self.writeMessageToNetwork(self.neh, repl)
		self.replied = 1
		self.ack = self.readRequestFromNetwork(self.neh)
