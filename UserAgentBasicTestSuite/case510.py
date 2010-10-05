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
# $Id: case510.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log
import copy

class case510 (TestCase):

	def config(self):
		self.name = "Case 510"
		self.description = "Failed re-INIVTE does not change dialog"
		self.isClient = True
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		self.fst_inv = self.createRequest("INVITE")
		self.mediaSockPair = self.setMediaBody(self.fst_inv)

		self.reinvited = 0
		self.rereinvited = 0
		self.byed = 0
		self.writeMessageToNetwork(self.neh, self.fst_inv)

		self.code = 0
		while (self.byed == 0):
			repl = self.readReplyFromNetwork(self.neh)
			if (repl is not None) and (not repl.isRequest) and (repl.code > self.code):
				self.code = repl.code
			if (repl is None) and (self.reinvited == 1):
				self.addResult(TestCase.TC_ERROR, "missing reply on re-INVITE")
				bye = self.createRequest("BYE", dia=self.fst_inv.transaction.dialog)
				self.byed = 1
				self.writeMessageToNetwork(self.neh, bye)
				repl = self.readReplyFromNetwork(self.neh)
				if repl is None:
					self.addResult(TestCase.TC_ERROR, "missing reply on BYE request")
			elif repl is None:
				self.code = 999

		if (repl is None):
			self.addResult(TestCase.TC_FAILED, "missing reply on request")
		if (self.byed == 1) and (self.rereinvited == 1):
			self.addResult(TestCase.TC_PASSED, "re-INVITE with Require:FooBar rejected, but later re-INVITE accepted")

		self.neh.closeSock()

	def on180(self, message):
		print "  !!!!  PLEASE ANSWER/PICKUP THE CALL  !!!!"

	def on183(self, message):
		self.on180(message)

	def on200(self, message):
		if message.getParsedHeaderValue("CSeq").method == "INVITE":
			Log.logDebug("case510: sending ACK for 200 INVITE reply", 2)
			ack = self.createRequest("ACK", trans=message.transaction)
			self.writeMessageToNetwork(self.neh, ack)
		if self.reinvited == 0:
			self.snd_inv = self.createRequest("INVITE", dia=message.transaction.dialog)
			tmp = self.setMediaBody(self.snd_inv, self.mediaSockPair[0])
			req = self.getParsedHeaderInstance("Require")
			req.tags.append("FooBar")
			self.snd_inv.setParsedHeaderValue("Require", req)
			self.snd_inv.setHeaderValue("Require", req.create())
			self.reinvited = 1
			self.code = 0
			Log.logDebug("case510: sending the re-INVITE with Require:FooBar", 1)
			self.writeMessageToNetwork(self.neh, self.snd_inv)
		elif (self.rereinvited == 1) or (self.reinvited == 1):
			if (self.rereinvited == 0) and (self.reinvited == 1) and (message.getParsedHeaderValue("CSeq").method == "INVITE"):
				self.addResult(TestCase.TC_FAILED, "re-INVITE with Require:FooBar aceepted")
			if self.byed == 0:
				bye = self.createRequest("BYE", dia=message.transaction.dialog)
				self.byed = 1
				self.writeMessageToNetwork(self.neh, bye)
				repl = self.readReplyFromNetwork(self.neh)
				if repl is None:
					self.addResult(TestCase.TC_ERROR, "missing reply on BYE request")

	def on420(self, message):
		Log.logDebug("case510: sending ACK for 420 reply", 2)
		ack = self.createRequest("ACK", trans=message.transaction)
		self.writeMessageToNetwork(self.neh, ack)
		self.trd_inv = self.createRequest("INVITE", dia=message.transaction.dialog)
		tmp = self.setMediaBody(self.trd_inv, self.mediaSockPair[0])
		self.rereinvited = 1
		self.code = 0
		Log.logDebug("case510: sending the the final re-INVITE", 1)
		self.writeMessageToNetwork(self.neh, self.trd_inv)

	def onDefaultCode(self, message):
		if (message.hasParsedHeaderField("CSeq")) and (message.getParsedHeaderValue("CSeq").method == "INVITE") and (message.code >= 300):
			Log.logDebug("case510: sending ACK for >= 300 INVITE reply", 2)
			ack = self.createRequest("ACK", trans=message.transaction)
			self.writeMessageToNetwork(self.neh, ack)
		if self.reinvited == 1:
			self.addResult(TestCase.TC_ERROR, "re-INVITE with Require:FooBar rejected with \'" + str(message.code) + "\'")
		if self.rereinvited == 1:
			self.addResult(TestCase.TC_FAILED, "re-INVITE after re-INVITE with Require:FooBar rejected with \'" + str(message.code) + "\'")
		if self.byed == 0:
			bye = self.createRequest("BYE", dia=self.fst_inv.transaction.dialog)
			self.byed = 1
			self.writeMessageToNetwork(self.neh, bye)
			repl = self.readReplyFromNetwork(self.neh)
			if repl is None:
				self.addResult(TestCase.TC_ERROR, "missing reply on BYE request")
