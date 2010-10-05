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
# $Id: case202.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case202 (TestCase):

	def config(self):
		self.name = "Case 202"
		self.description = "Wide range of valid charaters"
		self.isClient = True
		self.transport = "UDP"

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		inv = self.createRequest("INVITE")
		inv.rUri.username = "1_unusual.URI~(to-be!sure)&isn't+it$/crazy?,/;;*:&it+has=1,weird!*pass$wo~d_too.(doesn't-it)"
		via = inv.getParsedHeaderValue("Via")
		via.branch = "z9hG4bK-.!%66*_+`'~"
		inv.setHeaderValue("Via", via.create())
		to = inv.getParsedHeaderValue("To")
		to.displayname = "BEL:\\\x07 NUL:\\\x00 DEL:\\\x7F"
		to.uri.username = "1_unusual.URI~(to-be!sure)&isn't+it$/crazy?,/;;*:&it+has=1,weird!*pass$wo~d_too.(doesn't-it)"
		inv.setHeaderValue("To", to.create())
		inv.transaction.dialog.remoteUri = to
		self.writeMessageToNetwork(self.neh, inv)

		self.code = 0
		while (self.code <= 200):
			repl = self.readReplyFromNetwork(self.neh)
			if (repl is not None) and (repl.code > self.code):
				self.code = repl.code
			elif  repl is None:
				self.code = 999

		if repl is None:
			self.addResult(TestCase.TC_FAILED, "missing reply on request")

		self.neh.closeSock()

	def onDefaultCode(self, message):
		if message.code > self.code:
			self.code = message.code
		if message.code >= 200:
			if (message.hasParsedHeaderField("CSeq") and (message.getParsedHeaderValue("CSeq").method == "INVITE")):
				Log.logDebug("case202: sending ACK for >= 200 reply", 3)
				ack = self.createRequest("ACK", trans=message.transaction)
				self.writeMessageToNetwork(self.neh, ack)
				if message.code != 487:
					self.addResult(TestCase.TC_WARN, "INVITE with wide range of characters rejected with '" + str(message.code) + "'")
				elif message.code == 200:
					if len(self.results):
						self.addResult(TestCase.TC_PASSED, "INVITE with wide range of characters accepted")
					Log.logDebug("case202: sending BYE for accepted INVITE", 3)
					bye = self.createRequest("BYE", dia=message.transaction.dialog)
					self.writeMessageToNetwork(self.neh, bye)
					rep = self.readReplyFromNetwork(self.neh)
					if rep is None:
						self.addResult(TestCase.TC_ERROR, "missing response on BYE")
			elif (message.hasParsedHeaderField("CSeq")) and (message.getParsedHeaderValue("CSeq").method == "CANCEL") and (message.code != 200):
				self.addResult(TestCase.TC_WARN, "received \'" + str(message.code) + "\' for CANCEL")
			elif (not message.transaction.canceled) and (message.hasParsedHeaderField("CSeq")) and (message.getParsedHeaderValue("CSeq").method == "INVITE"):
				Log.logDebug("case202: sending ACK for >= 200 reply", 3)
				ack = self.createRequest("ACK", trans=message.transaction)
				self.writeMessageToNetwork(self.neh, ack)
				if message.code != 487:
					self.addResult(TestCase.TC_WARN, "INVITE with wide range of characters rejected with '" + str(message.code) + "'")
		else:
			self.addResult(TestCase.TC_PASSED, "INVITE with wide range of characters accepted")
			can = self.createRequest("CANCEL", trans=message.transaction)
			message.transaction.canceled = True
			self.writeMessageToNetwork(self.neh, can)
			canrepl = self.readReplyFromNetwork(self.neh)
			if canrepl is None:
				self.addResult(TestCase.TC_ERROR, "missing 200 on CANCEL")
