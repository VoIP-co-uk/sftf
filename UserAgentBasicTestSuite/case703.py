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
# $Id: case703.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log, Helper, socket

class case703 (TestCase):

	def config(self):
		self.name = "Case 703"
		self.description = "SRV return failover support"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True
		self.register = True
		# the retry at the backup server is a retransmission :)
		self.ignoreRetrans = False
		self.domain = ""
		self.expires = 30

	def srvlookup(self):
		# this has to be done because of a bug in the Helper.importModule above
		import dns.resolver
		self.srv_que = "_sip._" + self.transport.lower() + "." + self.domain
		try:
			return dns.resolver.query(self.srv_que, "SRV")
		except dns.resolver.NXDOMAIN:
			return None

	def run(self):
		dns = Helper.importModule("dns")
		if dns is None:
			Log.logTest("case703: failed to import dns library")
			Log.logTest("case703: for this test case the dnspython package from www.dnspython.org is required")
			self.addResult(TestCase.TC_ERROR, "missing required dnspython library")
			return

		hostname = socket.getfqdn()
		if self.domain == "":
			hn = hostname
			ld = hn.find(".")
			if ld == -1:
				hn, aliases, ip = socket.gethostbyaddr(hn)
				ld = hn.find(".")
				if ld == -1:
					Log.logTest("case703: failed to get the domain name: please fix the DNS setup or try to add a domain (by editing the case703.py file)")
					return
				
			self.domain = hn[ld+1:]
			dns_rsp = self.srvlookup()
			if dns_rsp is None:
				rd = hn.rfind(".")
				rd2 = hn.rfind(".", 0, rd)
				if rd2 == -1:
					print "missing second dot"
					Log.logTest("case703: missing DNS SRV records for '" + self.srv_que + "' and automatic domain detection failed")
					Log.logTest("case703: please adjust the domain and transport values in the case703.py file if you have a working DNS SRV setup")
					self.addResult(TestCase.TC_ERROR, "automatic domain and DNS SRV lookups failed")
					return
				else:
					self.domain = hn[rd2+1:]
					dns_rsp = self.srvlookup()
					if dns_rsp is None:
						Log.logTest("case703: automatic domainname and SRV lookup failed")
						Log.logTest("case703: please adjust the domain and transport values in the case703.py file if you have a working DNS SRV setup")
						self.addResult(TestCase.TC_ERROR, "automatic domain and DNS SRV lookup failed")
						return
		else:
			dns_rsp = self.srvlookup()
			if dns_rsp is None:
				Log.logTest("case703: missing DNS SRV records for '" + self.srv_que + "'")
				Log.logTest("case703: please add SRV records to your DNS setup or adjust the domain value to the correct value")
				self.addResult(TestCase.TC_ERROR, "missing DNS SRV records for '" + self.srv_que + "'")
				return

		if len(dns_rsp) != 2:
			Log.logTest("case703: for this test we need exactly two SRV records, currently " + str(len(dns_rsp)) + " records are configured")
			self.addResult(TestCase.TC_ERROR, "wrong number (" + str(len(dns_rsp)) + ")of SRV records for this test (exactly 2 required)")
			return
		for srv in dns_rsp:
			if str(srv.target).endswith(".") and not hostname.endswith("."):
				hostname = hostname + "."
			if str(srv.target) != hostname:
				Log.logTest("case703: both SRV records have to point at this host")
				Log.logTest("case703: one entry (" + str(srv) + ") is not pointing at this host (" + str(hostname) +")")
				self.addResult(TestCase.TC_ERROR, "SRV entry pointing to wrong host")
				return
		entry1, entry2 = dns_rsp
		if entry1.port == entry2.port:
			Log.logTest("case703: the ports of the SRV records are equal, but they have to be different")
			self.addResult(TestCase.TC_ERROR, "ports of the SRV records are equal")
			return
		if entry1.priority == entry2.priority:
			Log.logTest("case703: the priorities of the SRV records are equal, but the have to be different")
			self.addResult(TestCase.TC_ERROR, "priorities of the SRV records are equal")
			return
		elif entry1.priority < entry2.priority:
			pri = entry1
			sec = entry2
		else:
			pri = entry2
			sec = entry1
		# creating the network socket
		self.pri_neh = NEH.NetworkEventHandler(self.transport, str(pri.target), pri.port)
		self.sec_neh = NEH.NetworkEventHandler(self.transport, str(sec.target), sec.port)

		self.ignore = 1
		self.prim = 1
		print "  !!!!  PLEASE REGISTER AT " + str(self.domain) + " WITHIN 5 MINUTES  !!!!"
		req = self.readRequestFromNetwork(self.pri_neh, 300)
		if req is None:
			self.addResult(TestCase.TC_ERROR, "missing REGISTER request at primary socket")
		else:
			self.ignore = 0
			self.prim = 0
			req2 = self.readRequestFromNetwork(self.sec_neh, 60)
			if req2 is None:
				self.addResult(TestCase.TC_FAILED, "did not received REGISTER at secondary socket within 60 seconds")
			else:
				self.prim = 1
				req3 = self.readRequestFromNetwork(self.pri_neh, 3*self.expires)
				if req3 is None:
					self.addResult(TestCase.TC_FAILED, "did not received REGISTER at primary socket within " + str(3*self.expires) + " seconds")
				else:
					self.autoReact = False
					test = self.readRequestFromNetwork(self.sec_neh, 0.1, TimeoutError=False)
					if (test is not None) and (test.method == "REGISTER"):
						self.addResult(TestCase.TC_WARN, "disregarded SRV priorities and tried to re-register at backup server first")
					diff = int(Helper.eventTimeDiff(req3.event, req2.event))
					if diff > self.expires:
						self.addResult(TestCase.TC_WARN, "re-registration at primary server was " + str(diff - self.expires) + " seconds after expiration of Contact at backup server")

		# at the end please close the sockets again
		self.pri_neh.closeSock()
		self.sec_neh.closeSock()

	def onREGISTER(self, message):
		if self.ignore == 1:
			Log.logTest("ignoring REGISTER on the primary socket")
		else:
			Log.logTest("sending 200 for REGISTER on secondary socket")
			repl = self.createReply(200, "OK", message)
			if self.prim == 0:
				# flush the primary socket
				end = 0
				self.autoReact = False
				while end == 0:
					re = self.readMessageFromNetwork(self.pri_neh, 0.1, TimeoutError=False)
					if re is None:
						end = 1
				self.autoReact = True
				co = repl.getParsedHeaderValue("Contact")
				co.expires = self.expires
				repl.setHeaderValue("Contact", co.create())
				self.writeMessageToNetwork(self.sec_neh, repl)
			else:
				self.writeMessageToNetwork(self.pri_neh, repl)
				self.addResult(TestCase.TC_PASSED, "returing to primary SRV after failover succeeded")
