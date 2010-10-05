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
# $Id: case511.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log, Config
import copy

class case511 (TestCase):

	def config(self):
		self.name = "Case 511"
		self.description = "Correct Route set construction"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		#if not self.userInteraction("case511: proceed when ready to send INVITE"):
		#	neh.closeSock()
		#	return

		self.invited = False
		self.end = 0
		while self.end == 0:
			if not self.invited:
				print "  !!!!  PLEASE CALL ANY NUMBER/USER  !!!!"
			req = self.readMessageFromNetwork(self.neh, TimeoutError=self.invited)
			if self.invited and req is None:
				self.addResult(TestCase.TC_ERROR, "missing ACK for 200")
				self.end = 1

		self.neh.closeSock()

		if self.ack.hasHeaderField("Route"):
			if self.ack.hasParsedHeaderField("Route"):
				ro_fst = self.ack.getParsedHeaderValue("Route")
				ro_sec = ro_fst.next
				rr_fst = self.rr
				rr_sec = self.rr.next
				passed = True
				# compare step by step
				if ro_fst != rr_sec:
					Log.logDebug("case511: first Record-Route is not equal with last Route header", 1)
					Log.logTest("case511: first RR and last Route differ")
					self.addResult(TestCase.TC_FAILED, "first RR and last Route entry differ")
					passed = False
				if ro_sec != rr_fst:
					Log.logDebug("case511: second Record-Route is not equal with first Route header", 1)
					Log.logTest("case511: second RR and first Route differ")
					self.addResult(TestCase.TC_FAILED, "second RR and first Route entry differ")
					passed = False
				if passed:
					Log.logDebug("case511: both Record-Route and Route entries are equal", 2)
					Log.logTest("case511: both RR and Route entries are equal")
					self.addResult(TestCase.TC_PASSED, "both RR and Route entries are equal")
			else:
				Log.logDebug("case511: ACK has Route but not parsed Route header; failed to parse??", 1)
				Log.logTest("case511: ACK misses parsed Route header")
				self.addResult(TestCase.TC_ERROR, "ACK misses parsed Route header")
		else:
			Log.logDebug("case511: ACK misses Route header", 1)
			Log.logTest("case511: ACK misses Route header")
			self.addResult(TestCase.TC_FAILED, "ACK misses Route header")


	def onINVITE(self, message):
		repl = self.createReply(200, "OK")
		self.rr = self.getParsedHeaderInstance("Record-Route")
		self.rr.uri.protocol = "sip"
		self.rr.uri.host = str(self.neh.ip)
		self.rr.uri.port = str(self.neh.port)
		self.rr.uri.params = ['foo', 'bar=1', 'test=x', 'lr']
		self.rr.looseRouter = True
		self.rr.next = self.getParsedHeaderInstance("Record-Route")
		# a displayname seems to be too nasty ;)
		#rr.next.displayname = "SC-Test Name"
		self.rr.next.uri = copy.deepcopy(self.rr.uri)
		self.rr.next.uri.protocol = "sip"
		self.rr.next.uri.host = str(self.neh.ip)
		self.rr.next.uri.port = str(self.neh.port)
		self.rr.next.uri.params = ['bar', 'test=200', 'foo=test', 'lr']
		self.rr.next.looseRouter = True
		if message.hasParsedHeaderField("Record-Route"):
			self.rr.next.next = copy.deepcopy(message.getParsedHeaderValue("Record-Route"))
		repl.setParsedHeaderValue("Record-Route", self.rr)
		repl.setHeaderValue("Record-Route", self.rr.create())
		repl.transaction.dialog.ignoreRoute = True
		self.invited = True
		self.writeMessageToNetwork(self.neh, repl)

	def onACK(self, message):
		self.ack = message
		bye = self.createRequest("BYE", dia=message.transaction.dialog)
		self.writeMessageToNetwork(self.neh, bye)
		self.end = 1
		repl = self.readReplyFromNetwork(self.neh)
		if repl is None:
			self.addResult(TestCase.TC_ERROR, "missing reply on BYE request")
