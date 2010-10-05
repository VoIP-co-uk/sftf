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
# $Id: case229.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case229 (TestCase):

	def config(self):
		self.name = "Case 229"
		self.description = "INVITE with missing body"
		self.isClient = True
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		# creating a network socket is always required
		self.neh = NEH.NetworkEventHandler(self.transport)

		self.inv = self.createRequest("INVITE")
		self.setBody([], self.inv)
		self.inv.removeParsedHeaderField("Content-Type")
		self.inv.removeHeaderField("Content-Type")
		self.writeMessageToNetwork(self.neh, self.inv)

		self.end = 0
		self.invited = 0
		self.ringing = 0

		while self.end == 0:
			if self.invited == 0:
				print "  !!!!  PLEASE ANSWER/PICKUP THE CALL  !!!!"
			repl = self.readReplyFromNetwork(self.neh)
			if (repl is None) and (self.ringing == 0):
				self.end = 1
				self.addResult(TestCase.TC_ERROR, "missing reply")

		self.neh.closeSock()

	def on180(self, message):
		self.ringing = 1

	def on183(self, message):
		self.on180(message)

	def on200(self, message):
		if message.getParsedHeaderValue("CSeq").method == "INVITE":
			self.invited = 1
			self.ringing = 0
			#FIXME we should check the content of the body if it
			# relly contains a SDP offer
			self.addResult(TestCase.TC_PASSED, "INVITE without body accepted")
			ack = self.createRequest("ACK", trans=message.transaction)
			self.mediaSockPair = self.setMediaBody(ack)
			self.writeMessageToNetwork(self.neh, ack)
			bye = self.createRequest("BYE", dia=message.transaction.dialog)
			self.writeMessageToNetwork(self.neh, bye)
			self.end = 1
			repl = self.readReplyFromNetwork(self.neh)
			if repl is None:
				self.addResult(TestCase.TC_ERROR, "missing reply on BYE")

	def onDefaultCode(self, message):
		if (message.code >= 300) and (message.getParsedHeaderValue("CSeq").method == "INVITE"):
			self.addResult(TestCase.TC_FAILED, "INVITE without body rejected with '" + str(message.code) + "'")
			ack = self.createRequest("ACK", trans=message.transaction)
			self.mediaSockPair = self.setMediaBody(ack)
			self.writeMessageToNetwork(self.neh, ack)
			self.end = 1
