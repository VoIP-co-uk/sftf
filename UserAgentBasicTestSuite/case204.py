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
# $Id: case204.py,v 1.2 2004/05/02 18:57:35 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log

class case204 (TestCase):

	def config(self):
		self.name = "Case 204"
		self.description = "Long values in header fields"
		self.isClient = True
		# Note: the request is over 3k. on one side phones seem not
		# to be able to handle fragmentation but on the other side
		# many phones lack TCP support
		self.transport = "UDP"

	def run(self):
		self.neh = NEH.NetworkEventHandler(self.transport)

		inv = self.createRequest("INVITE")
		to = inv.getParsedHeaderValue("To")
		to.displayname = "I have a user name of extrem extrem extrem extrem extrem extrem extrem extrem extrem extrem proportion"
		to.uri.params.append("unknownparam=verylonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglongvalue")
		to.uri.params.append("longparamnamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamename=shortvalue")
		to.uri.params.append("verylonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglongParameterNameWithNoValue")
		inv.setHeaderValue("To", to.create())
		inv.transaction.dialog.remoteUri = to
		fo = inv.getParsedHeaderValue("From")
		fo.uri.username = "amazinglylongcallernameamazinglylongcallernameamazinglylongcallernameamazinglylongcallernameamazinglylongcallername"
		fo.uri.params.append("unknownheaderparamnamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamename=unknownheaderparamvaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevaluevalue")
		fo.uri.params.append("unknownValuelessparamnameparamnameparamnameparamnameparamnameparamnameparamnameparamnameparamnameparamname")
		inv.setHeaderValue("From", fo.create())
		inv.transaction.dialog.locaUri = fo
		inv.setHeaderValue("Unknown-LongLongLongLongLongLongLongLongLongLongLongLongLongLongLongLongLongLongLongLong-Name", "unknown-longlonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglong-value;unknown-longlonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglong-parameter-name = unknown-longlonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglong-parameter-value\r\n")
		co = inv.getParsedHeaderValue("Contact")
		co.uri.username = "amazinglylongcallernameamazinglylongcallernameamazinglylongcallernameamazinglylongcallernameamazinglylongcallername"
		inv.setHeaderValue("Contact", co.create())
		via = inv.getParsedHeaderValue("Via")
		r = range(1, 33)
		r.reverse()
		for i in r:
			via.next = self.getParsedHeaderInstance("Via")
			via.next.host = "sip" + str(i) + ".example.com"
			via.next.protocol = "SIP"
			via.next.version = "2.0"
			via.next.transport = "UDP"
			if i == 1:
				via.next.branch = "verylonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglongbranchvalue"
			via = via.next
		inv.setHeaderValue("Via", via.create())
		inv.rUri.params.append("verylonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglongparameter=verylonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglongvalue")
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
			if message.getParsedHeaderValue("CSeq").method == "INVITE":
				Log.logDebug("case204: sending ACK for >= 200 reply", 3)
				ack = self.createRequest("ACK", trans=message.transaction)
				self.writeMessageToNetwork(self.neh, ack)
			elif message.code == 200:
				if message.transaction.canceled:
					Log.logDebug("case204: received 200 for CANCEL", 3)
				else:
					Log.logDebug("case204: sending BYE for accepted INVITE", 3)
					bye = self.createRequest("BYE", dia=message.transaction.dialog)
					self.writeMessageToNetwork(self.neh, bye)
					rep = self.readReplyFromNetwork(self.neh)
					if rep is None:
						self.addResult(TestCase.TC_ERROR, "missing response on BYE")
		else:
			self.addResult(TestCase.TC_PASSED, "INVITE with very long headers accepted")
			can = self.createRequest("CANCEL", trans=message.transaction)
			message.transaction.canceled = True
			self.writeMessageToNetwork(self.neh, can)
			canrepl = self.readReplyFromNetwork(self.neh)
			if canrepl is None:
				self.addResult(TestCase.TC_ERROR, "missing 200 on CANCEL")
