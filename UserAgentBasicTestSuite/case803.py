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
# $Id: case803.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log, select

class case803 (TestCase):

	def config(self):
		self.name = "Case 803"
		self.description = "Media on-hold support"
		self.isClient = True
		self.transport = "UDP"
		self.interactRequired = True

	def run(self):
		# creating a network socket is always required
		self.neh = NEH.NetworkEventHandler(self.transport)

		self.fst_inv = self.createRequest("INVITE")
		self.mediaSockPair = self.setMediaBody(self.fst_inv)
		self.writeMessageToNetwork(self.neh, self.fst_inv)

		self.invited = self.onhold = self.byed = 0

		while self.byed == 0:
			repl = self.readMessageFromNetwork(self.neh)
			if repl is None:
				if self.invited == 1:
					bye = self.createRequest("BYE", dia=self.fst_inv.transaction.dialog)
					Log.logTest("sending BYE for original INVITE")
					self.writeMessageToNetwork(self.neh, bye)
					rep = self.readReplyFromNetwork(self.neh)
					if rep is None:
						self.addResult(TestCase.TC_ERROR, "missing reply on BYE")
				self.addResult(TestCase.TC_ERROR, "missing reply on request")
				self.byed = 1

		# at the end please close the socket again
		self.neh.closeSock()

	def on180(self, message):
		print "  !!!!  PLEASE ANSWER/PICKUP THE CALL  !!!!"

	def on183(self, message):
		self.on180(message)

	def on200(self, message):
		if message.getParsedHeaderValue("CSeq").method == "INVITE":
			ack = self.createRequest("ACK", trans=message.transaction)
			self.writeMessageToNetwork(self.neh, ack)
			if self.invited == 0:
				self.invited = 1
				self.snd_inv = self.createRequest("INVITE", dia=message.transaction.dialog)
				self.writeMessageToNetwork(self.neh, self.snd_inv)
			else:
				self.onhold = 1
				# no comfort API function for media (yet;)
				# lets look 20 times if we received something on the media
				# socket
				print "  looking for media packet..."
				for i in range(0, 20):
					s_in, s_out, s_exc = select.select([self.mediaSockPair[0]], [], [], 0.1)
					if len(s_in) > 0:
						data = True
						buf, addr = s_in[0].recvfrom(65535)
					else:
						data = False
				if data:
					self.addResult(TestCase.TC_FAILED, "received media when being on hold")
				else:
					self.addResult(TestCase.TC_PASSED, "no media received when being on hold")
				bye = self.createRequest("BYE", dia=message.transaction.dialog)
				self.writeMessageToNetwork(self.neh, bye)
				self.byed = 1
				repl = self.readReplyFromNetwork(self.neh)
				if repl is None:
					self.addResult(TestCase.TC_ERROR, "missing 200 for BYE")
