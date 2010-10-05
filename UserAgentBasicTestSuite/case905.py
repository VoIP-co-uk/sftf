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
# $Id: case905.py,v 1.3 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log
import copy

class case905 (TestCase):

	first_branch = "z9hG4bK-0-first-request"
	second_branch = "z9hG4bK-1-second-request"

	def config(self):
		self.name = "Case 905"
		self.description = "Request merging"
		self.isClient = True
		self.transport = "UDP"
		#Note: otherwiese multiple 180's could be treated as
		# retransmissions and we will not see them
		self.ignoreRetrans = False
		self.minAPIVersion = 0.3

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		self.fst_inv = self.createRequest("INVITE")
		f_via = self.fst_inv.getParsedHeaderValue("Via")
		f_via.branch = case905.first_branch
		f_via.next = self.getParsedHeaderInstance("Via")
		f_via.next.protocol = "SIP"
		f_via.next.version = "2.0"
		f_via.next.transport = "UDP"
		f_via.next.host = "proxy1.example.com"
		f_via.next.branch = "z9hG4bK-proxy1-request1-fake"
		ua_via = self.getParsedHeaderInstance("Via")
		ua_via.protocol = "SIP"
		ua_via.version = "2.0"
		ua_via.transport = "UDP"
		ua_via.host = "ua.example.com"
		ua_via.branch = "z9hG4bK-ua-request-fake"
		f_via.next.next = ua_via
		self.fst_inv.setHeaderValue("Via", f_via.create())

		self.snd_inv = copy.deepcopy(self.fst_inv)
		s_via = self.snd_inv.getParsedHeaderValue("Via")
		s_via.branch = case905.second_branch
		s_via.next = self.getParsedHeaderInstance("Via")
		s_via.next.protocol = "SIP"
		s_via.next.version = "2.0"
		s_via.next.transport = "UDP"
		s_via.next.host = "proxy2.example.com"
		s_via.next.branch = "z9hG4bK-proxy2-request1-fake"
		s_via.next.next = ua_via
		self.snd_inv.setHeaderValue("Via", s_via.create())
		t = self.newTransaction(self.fst_inv.transaction.dialog, self.snd_inv)

		self.replied = 0
		self.invited = 0
		self.rejected = False
		self.writeMessageToNetwork(self.neh, self.fst_inv)

		self.code = 0
		while (self.code <= 200):
			repl = self.readReplyFromNetwork(self.neh)
			if (repl is not None) and (repl.code > self.code):
				self.code = repl.code
			elif  repl is None:
				self.code = 999

		if repl is None:
			if self.replied == 0:
				self.addResult(TestCase.TC_ERROR, "missing reply on request")
			else:
				self.addResult(TestCase.TC_WARN, "received only replies for the first requests")
				can = self.createRequest("CANCEL", trans=self.fst_inv.transaction)
				self.writeMessageToNetwork(self.neh, can)
				canrepl = self.readReplyFromNetwork(self.neh)
				if canrepl is None:
					self.addResult(TestCase.TC_ERROR, "missing reply on CANCEL")
		if (self.dialog[0].transaction[0].canceled and (self.dialog[0].transaction[0].firstACK is None)) or ((self.dialog[0].transaction[0].firstReply is not None) and (self.dialog[0].transaction[0].firstReply.code != 487)):
			ack = self.readReplyFromNetwork(self.neh)

		self.neh.closeSock()

	def on100(self, message):
		Log.logDebug("case905: received 100", 1)
		if self.invited == 0:
			Log.logDebug("case905: sending the forked INVITE", 1)
			self.addMessage(self.snd_inv)
			self.writeMessageToNetwork(self.neh, self.snd_inv)
			self.invited = 1

	def on180(self, message):
		if self.invited == 0:
			self.writeMessageToNetwork(self.neh, self.snd_inv)
			self.invited = 1
		via = message.getParsedHeaderValue("Via")
		if via.branch == case905.first_branch:
			new_rep = 1
		elif via.branch == case905.second_branch:
			new_rep = 2
		else:
			Log.logTest("branch value of 18[03] does not match any know value")
			new_rep = 3
		if self.replied == 0:
			self.replied = new_rep
		elif new_rep != self.replied:
			self.addResult(TestCase.TC_WARN, "UA did not rejected the second forked request")
			#Note: as the UA seems to be only 2543 compliant we cancel
			# only one time
			can = self.createRequest("CANCEL", trans=message.transaction)
			self.writeMessageToNetwork(self.neh, can)
			canrepl = self.readReplyFromNetwork(self.neh)
			if canrepl is None:
				self.addResult(TestCase.TC_ERROR, "missing reply on CANCEL")
		elif self.rejected:
			if new_rep == self.replied:
				self.addResult(TestCase.TC_WARN, "received 18[03] for allready rejected INVITE")
			if not message.transaction.canceled:
				can = self.createRequest("CANCEL", trans=message.transaction)
				self.writeMessageToNetwork(self.neh, can)
				canrepl = self.readReplyFromNetwork(self.neh)
				if canrepl is None:
					self.addResult(TestCase.TC_ERROR, "missing reply on CANCEL")

	def on183(self, message):
		self.on180(message)

	# overwrite the default 486 because in this case 486 is ok
	def on486(self, message):
		self.onDefaultCode(message)

	def onDefaultCode(self, message):
		if message.code > self.code:
			self.code = message.code
		if message.code >= 200:
			if message.getParsedHeaderValue("CSeq").method == "INVITE":
				Log.logDebug("case905: sending ACK for >= 200 reply", 3)
				ack = self.createRequest("ACK", trans=message.transaction)
				self.writeMessageToNetwork(self.neh, ack)
				if (self.replied != 0) and not message.transaction.canceled:
					via = message.getParsedHeaderValue("Via")
					if via.branch == case905.first_branch:
						new_rep = 1
					elif via.branch == case905.second_branch:
						new_rep = 2
					else:
						new_rep =3
						Log.logTest("branch value of negative reply does not match any know value")
					if new_rep != self.replied:
						self.rejected = True
						self.addResult(TestCase.TC_PASSED, "one request accepted, the other rejected")
						if message.code != 482:
							self.addResult(TestCase.TC_WARN, "the second forked INVITE should be rejected with 482, instead received '" + str(message.code) + "'")
					else:
						Log.logTest("received negative reply \'" + str(message.code) + "\' for a different branch then the first 180")
						self.addResult(TestCase.TC_ERROR, "received negative reply for the accepted request")
					can = self.createRequest("CANCEL", trans=message.transaction)
					self.writeMessageToNetwork(self.neh, can)
					canrepl = self.readReplyFromNetwork(self.neh)
					if canrepl is None:
						self.addResult(TestCase.TC_ERROR, "missing reply on CANCEL")
				elif (self.replied == 0):
					via = message.getParsedHeaderValue("Via")
					if via.branch == case905.first_branch:
						self.replied = 1
					elif via.branch == case905.second_branch:
						self.replied = 2
					if message.code >= 400:
						self.rejected = True
						self.addResult(TestCase.TC_PASSED, "forked INVITE rejected with '" + str(message.code) + "'")
						if message.code != 482:
							self.addResult(TestCase.TC_WARN, "the second forked INVITE should be rejected with 482, instead received '" + str(message.code) + "'")
			elif message.code == 200:
				if message.getParsedHeaderValue("CSeq").method == "CANCEL":
					Log.logDebug("case905: received 200 for CANCEL", 3)
				elif message.getParsedHeaderValue("CSeq").method == "INVITE":
					Log.logDebug("case905: sending BYE for accepted INVITE", 3)
					bye = self.createRequest("BYE", dia=message.transaction.dialog)
					self.writeMessageToNetwork(self.neh, bye)
					rep = self.readReplyFromNetwork(self.neh)
					if rep is None:
						self.addResult(TestCase.TC_ERROR, "missing response on BYE")
