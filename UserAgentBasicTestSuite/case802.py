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
# $Id: case802.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log
import copy

class case802 (TestCase):

	def config(self):
		self.name = "Case 802"
		self.description = "REFER-based click-to-dial"
		self.isClient = True
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.refer_name = "refered"

		self.neh = NEH.NetworkEventHandler(self.transport)

		self.fst_inv = self.createRequest("INVITE")
		self.mediaSockPair = self.setMediaBody(self.fst_inv)

		self.end = 0
		self.refered = 0
		self.invited = 0
		self.byed = 0
		self.refbyed = 0
		self.acked = 0
		self.notified = 0
		self.writeMessageToNetwork(self.neh, self.fst_inv)

		while self.end == 0:
			repl = self.readMessageFromNetwork(self.neh)
			if repl is None:
				if self.refered == 1:
					bye = self.createRequest("BYE", dia=self.fst_inv.transaction.dialog)
					Log.logTest("case802: sending BYE for original INVITE")
					self.writeMessageToNetwork(self.neh, bye)
					rep = self.readReplyFromNetwork(self.neh)
					if rep is None:
						self.addResult(TestCase.TC_ERROR, "missing reply on BYE")
				if self.invited == 1:
					bye = self.createRequest("BYE", dia=self.refinvite.transaction.dialog)
					Log.logTest("case802: sending BYE for refered INVITE")
					self.writeMessageToNetwork(self.neh, bye)
					rep = self.readReplyFromNetwork(self.neh)
					if rep is None:
						self.addResult(TestCase.TC_ERROR, "missing reply on BYE")
				self.end = 1

		if (repl is None):
			self.addResult(TestCase.TC_FAILED, "missing reply on request")
		else:
			passed = True
			if self.refered == 0:
				passed = False
			if self.notified == 0 and passed:
				passed = False
				self.addResult(TestCase.TC_FAILED, "missing Notifiy for REFER")
			elif self.notified == 1:
				if len(self.notify.body) == 0:
					self.addResult(TestCase.TC_WARN, "NOTIFY is without body")
				elif not self.notify.body[0].lower().startswith("sip/2.0 200 ok"):
					self.addResult(TestCase.TC_WARN, "NOTIFY body does not contain result from refered connection")
			if self.invited == 0 and passed:
				passed = False
				self.addResult(TestCase.TC_FAILED, "missing INVITE to refer address")
			elif self.invited == 1:
				if self.refinvite.rUri != self.refto.uri:
					passed = False
					self.addResult(TestCase.TC_FAILED, "request URI in refered INVITE differes from Refer-To URI")
			if self.byed == 0 and passed:
				passed = False
				self.addResult(TestCase.TC_FAILED, "missing BYE for first connection")
			if self.refbyed == 0 and passed:
				passed = False
				self.addResult(TestCase.TC_FAILED, "missing BYE for refered connection")
			if passed:
				self.addResult(TestCase.TC_PASSED, "refering worked without errors")

		self.neh.closeSock()

	def on180(self, message):
		print "  !!! PLEASE ANSWER/PICKUP THE CALL  !!!"

	def on183(self, message):
		self.on180(message)

	def on200(self, message):
		cs = message.getParsedHeaderValue("CSeq")
		if cs.method == "INVITE":
			Log.logTest("case802: sending ACK for 200 reply")
			ack = self.createRequest("ACK", trans=message.transaction)
			self.writeMessageToNetwork(self.neh, ack)
			ref = self.createRequest("REFER")
			fr = ref.getParsedHeaderValue("From")
			self.refto = self.getParsedHeaderInstance("Refer-To")
			self.refto.uri.protocol = "sip"
			self.refto.uri.username = self.refer_name
			self.refto.uri.host = fr.uri.host
			self.refto.uri.port = fr.uri.port
			self.refto.uri.params.append("transport=UDP")
			ref.setParsedHeaderValue("Refer-To", self.refto)
			ref.setHeaderValue("Refer-To", self.refto.create())
			Log.logTest("case802: sending REFER")
			self.writeMessageToNetwork(self.neh, ref)
			self.refered = 1
		elif (cs.method == "BYE") and (self.invited == 1) and (self.refbyed == 0):
			bye = self.createRequest("BYE", dia=self.refinvite.transaction.dialog)
			Log.logTest("case802: sending BYE for refered INVITE")
			self.writeMessageToNetwork(self.neh, bye)
			self.refbyed = 1
			self.end = 1

	def on202(self, message):
		Log.logTest("case802: received 202 for REFER")

	def onINVITE(self, message):
		self.refinvite = message
		Log.logTest("case802: sending 200 for INVITE")
		repl = self.createReply(200, "OK", mes=message)
		self.writeMessageToNetwork(self.neh, repl)
		self.invited = 1
		
	def onACK(self, message):
		Log.logTest("case802: received ACK for refered INVITE")
		self.acked = 1
		if (self.notified == 1) and (self.refbyed == 0):
			bye = self.createRequest("BYE", dia=message.transaction.dialog)
			Log.logTest("case802: sending BYE for refered INVITE")
			self.writeMessageToNetwork(self.neh, bye)
			self.refbyed = 1
			self.end = 1

	def onNOTIFY(self, message):
		self.notify = message
		Log.logTest("case802: sending 200 for NOTIFY")
		replok = self.createReply(200, "OK", mes=message)
		self.writeMessageToNetwork(self.neh, replok)
		self.notified = 1
		if (len(message.body) > 0):
			if message.body[0].lower().startswith("sip/2.0 200 ok"):
				if self.byed == 0:
					bye = self.createRequest("BYE", dia=self.fst_inv.transaction.dialog)
					Log.logTest("case802: sending BYE for original INVITE because received success NOTIFY")
					self.writeMessageToNetwork(self.neh, bye)
					self.byed = 1
			else:
				self.addResult(TestCase.TC_WARN, "received NOTIFY about a reply on the refered connection which was never send")
		else:
			self.addResult(TestCase.TC_WARN, "received NOTIFY without body")

	def onBYE(self, message):
		Log.logTest("case802: received BYE for original INVITE")
		repl = self.createReply(200, "OK", mes=message)
		Log.logTest("case802: sending 200 for BYE")
		self.writeMessageToNetwork(self.neh, repl)
		self.byed = 1
		if (self.invited == 1) and (self.refbyed == 0):
			bye = self.createRequest("BYE", dia=self.refinvite.transaction.dialog)
			Log.logTest("case802: sending BYE for refered INVITE")
			self.writeMessageToNetwork(self.neh, bye)
			self.refbyed = 1
			repl = self.readReplyFromNetwork(self.neh)
			if repl is None:
				self.addResult(TestCase.TC_ERROR, "missing reply on BYE for refered connection")
		self.end = 1

	def onDefaultCode(self, message):
		if (message.code >= 300) and (message.getParsedHeaderValue("CSeq").method == "INVITE"):
			Log.logTest("case802: sending ACK for " + str(message.code) + " reply")
			ack = self.createRequest("ACK", trans=message.transaction)
			self.writeMessageToNetwork(self.neh, ack)
		if self.refered == 0:
			self.addResult(TestCase.TC_ERROR, "INVITE rejected")
			self.end = 1
		else:
			if message.getParsedHeaderValue("CSeq").method == "REFER":
				self.addResult(TestCase.TC_FAILED, "REFER request rejected with " + str(message.code))
				bye = self.createRequest("BYE", dia=message.transaction.dialog)
				Log.logTest("case802: sending BYE for first INVITE")
				self.writeMessageToNetwork(self.neh, bye)
				repl = self.readReplyFromNetwork(self.neh)
				if repl is None:
					self.addResult(TestCase.TC_ERROR, "missing reply on BYE for refered connection")
				self.end = 1
			if self.refbyed == 1:
				self.addResult(TestCase.TC_ERROR, "BYE for refered connection rejected with " + str(message.code))
				self.end = 1
