#
# Copyright (C) 2004 SIPfoundry Inc.
# Licensed by SIPfoundry under the GPL license.
#
# Copyright (C) 2004 SIP Forum
# Licensed to SIPfoundry under a Contributor Agreement.
#
#
# This file is part of SIP Forum Test Framework.
#
# SIP Forum Test Framework is free software; you can redistribute it 
# and/or modify it under the terms of the GNU General Public License as 
# published by the Free Software Foundation; either version 2 of the 
# License, or (at your option) any later version.
#
# SIP Forum Test Framework is distributed in the hope that it will 
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SIP Forum Test Framework; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id: Dialog.py,v 1.18 2004/03/30 21:52:36 lando Exp $
#
import Log, Config, Helper
import copy
from SCException import SCException

class Dialog:
	"""This class keeps all required informations and functions for a SIP 
	dialog.
	"""
	DI_ST_INIT = 0
	DI_ST_ESTABLISHED = 1
	DI_ST_TERMINATED = 2

	def __init__(self):
		self.number = None
		self.localUri = None
		self.remoteUri = None
		self.CallID = None
		self.remoteCSeq = None
		self.remoteContact = None
		self.localCSeq = None
		self.RouteSet = None
		self.ignoreRoute = False
		self.state = Dialog.DI_ST_INIT
		self.transaction = []

	def __str__(self):
		return '[number:\'' + str(self.number) + '\', ' \
				+ 'localUri:\'' + str(self.localUri) + '\', ' \
				+ 'remoteUri:\'' + str(self.remoteUri) + '\', ' \
				+ 'CallId:\'' + str(self.CallID) + '\', ' \
				+ 'remoteCSeq:\'' + str(self.remoteCSeq) + '\', ' \
				+ 'remoteContact:\'' + str(self.remoteContact) + '\', ' \
				+ 'localCSeq:\'' + str(self.localCSeq) + '\', ' \
				+ 'RouteSet:\'' + str(self.RouteSet) + '\', ' \
				+ 'ignoreRoute:\'' + str(self.ignoreRoute) + '\', ' \
				+ 'state:\'' + str(self.state) + '\', ' \
				+ 'transaction:\'' + str(self.transaction) + '\']'

	def getRoutingTarget(self):
		"""This function returns the complete routing informations
		for a given dialog. It returns a tripple: request URI (a parsed sip 
		uri instance), the route set as list of parsed route headers and
		the network target of the request as tuple of IP and port.
		"""
		#FIXME we should look for the requested transport type
		if (not self.ignoreRoute) and (self.RouteSet is not None):
			if self.RouteSet.uri.port is None:
				port = int(5060)
			else:
				port = int(self.RouteSet.uri.port)
			dst = (self.RouteSet.uri.host, port)
			if self.RouteSet.looseRouter:
				rs = ''
				RR = self.RouteSet
				while RR is not None:
					rs = rs + ',' + RR.sub_create()
					RR = RR.next
				rs = rs[1:]
				return self.remoteContact.uri, rs, dst
			else:
				rs = ''
				RR = self.RouteSet.next
				while RR is not None:
					rs = rs + ',' + RR.sub_create()
					RR = RR.next
				rs = rs[1:] + ',' + "<" + self.remoteContact.uri.create() + ">"
				return self.RouteSet.uri, rs, dst
		elif self.remoteContact is not None:
			if self.remoteContact.uri.port is None:
				port = int(5060)
			else:
				port = int(self.remoteContact.uri.port)
			dst = (self.remoteContact.uri.host, port)
			return self.remoteContact.uri, None, dst
		else:
			ruri = Helper.createClassInstance("sip_uri")
			ruri.protocol = "sip"
			ruri.username = str(Config.TEST_USER_NAME)
			ruri.host = str(Config.TEST_HOST)
			ruri.port = str(Config.TEST_HOST_PORT)
			dst = (Config.TEST_HOST, int(Config.TEST_HOST_PORT))
			return ruri, None, dst
		
	def buildRouteSet(self, isClient):
		"""This function creates the required routing informations for a dialog.
		The required parameter is if for this dialog the test software is the
		UAC as boolean. The returned boolean will be true when the route set
		building was successfull.
		"""
		if self.RouteSet is not None:
			Log.logDebug("Dialog.buildRouteSet(): RouteSet exists allready => skiping", 2)
			return False
		if len(self.transaction) == 0:
			raise SCException("Dialog", "buildRouteSet", "implementation error: called for dialog without transaction")
		if isClient:
			Log.logDebug("Dialog.buildRouteSet(): called for client side", 5)
			if self.transaction[0].lastReply is None:
				Log.logDebug("Dialog.buildRouteSet(): lastReply empty => unable to build RouteSet", 1)
				return False
			if self.transaction[0].lastReply.code >= 300:
				Log.logDebug("Dialog.buildRouteSet(): lastReply code (\'" + str(self.transaction[0].lastReply.code) + "\') is negative => won't build a RouteSet", 2)
				if self.transaction[0].lastReply.hasHeaderField("Record-Route"):
					Log.logTest("WARNING: the negative reply contains a Record-Route")
				return False
			if self.transaction[0].lastReply.hasParsedHeaderField("Record-Route"):
				RR = copy.deepcopy(self.transaction[0].lastReply.getParsedHeaderValue("Record-Route"))
				curRR = RR
				if curRR.next is None:
					# only on RR element nothing to invert
					self.RouteSet = RR
				else:
					# copy first element
					while curRR.next.next is not None:
						curRR = curRR.next
					self.RouteSet = copy.deepcopy(curRR.next)
					curRR.next = None
					curRR = RR
					# copy all middle elements
					RS = self.RouteSet
					while curRR.next is not None:
						while curRR.next.next is not None:
							curRR = curRR.next
						RS.next = copy.deepcopy(curRR.next)
						RS = RS.next
						curRR.next = None
						curRR = RR
					# copy last element
					RS.next = copy.deepcopy(RR)
				Log.logDebug("Dialog.buildRouteSet(): successfully build RouteSet", 4)
				Log.logDebug("Dialog.buildRouteSet(): RouteSet: " + str(self.RouteSet), 5)
			else:
				Log.logDebug("Dialog.buildRouteSet(): lastReply has no parsed Record-Route", 4)
			if self.transaction[0].lastReply.hasParsedHeaderField("Contact"):
				self.remoteContact = self.transaction[0].lastReply.getParsedHeaderValue("Contact")
				Log.logDebug("Dialog.buildRouteSet(): remoteContact updated in isClient", 5)
			else:
				Log.logDebug("Dialog.buildRouteSet(): lastReply has no parsed Contact", 2)
			return True
		else:
			Log.logDebug("Dialog.buildRouteSet(): called for server side", 5)
			if self.transaction[0].firstRequest is None:
				Log.logDebug("Dialog.buildRouteSet(): firstRequest empty => unable to build RouteSet", 1)
				return False
			if self.transaction[0].firstRequest.hasParsedHeaderField("Record-Route"):
				self.RouteSet = copy.deepcopy(self.transaction[0].firstRequest.getParsedHeaderValue("Record-Route"))
				Log.logDebug("Dialog.buildRouteSet(): successfully build RouteSet", 4)
				Log.logDebug("Dialog.buildRouteSet(): RouteSet: " + str(self.RouteSet), 5)
			else:
				Log.logDebug("Dialog.buildRouteSet(): firstRequest has no parsed Record-Route", 2)
			if self.transaction[0].firstRequest.hasParsedHeaderField("Contact"):
				self.remoteContact = self.transaction[0].firstRequest.getParsedHeaderValue("Contact")
				Log.logDebug("Dialog.buildRouteSet(): remoteContact update in isServer", 5)
			else:
				Log.logDebug("Dialog.buildRouteSet(): firstRequest has no parsed Contact", 4)
			return True

	def appendTransaction(self, trans):
		"""This function inserts the as parameter given transaction to the
		dialog instance. Returns nothing.
		"""
		if (len(self.transaction) == 0):
			# the first transaction in the dialog sets localUri, remoteUri 
			# and Call-ID to indentify the dialog for the future
			if trans.message[0].hasParsedHeaderField("To"):
				to_uri = copy.deepcopy(trans.message[0].getParsedHeaderValue("To"))
			else:
				Log.logDebug("Dialog.appendTransaction(): WRNING: parsed To missing, using raw To instead (can be empty)", 2)
				to_uri = copy.copy(trans.message[0].getHeaderValue("To"))
			if trans.message[0].hasParsedHeaderField("From"):
				from_uri = copy.deepcopy(trans.message[0].getParsedHeaderValue("From"))
			else:
				Log.logDebug("Dialog.appendTransaction(): parsed From missing, using raw From instead (can be empty)", 2)
				from_uri = copy.copy(trans.message[0].getHeaderValue("From"))
			if trans.isClient:
				self.localUri = from_uri
				self.remoteUri = to_uri
			else:
				self.localUri = to_uri
				self.remoteUri = from_uri
				if trans.message[0].hasParsedHeaderField("Contact"):
					self.remoteContact = copy.deepcopy(trans.message[0].getParsedHeaderValue("Contact"))
				else:
					Log.logDebug("Dialog.appendTransaction(): parsed Contact missing, using raw Contact instead (can be empty)", 2)
					self.remoteContact = copy.copy(trans.message[0].getHeaderValue("Contact"))

			Log.logDebug("Dialog.appendTransaction(): localUri: " + str(self.localUri), 5)
			Log.logDebug("Dialog.appendTransaction(): remoteUri: " + str(self.remoteUri), 5)
			if trans.message[0].hasParsedHeaderField("Call-ID"):
				self.CallID = copy.deepcopy(trans.message[0].getParsedHeaderValue("Call-ID"))
			else:
				Log.logDebug("Dialog.appendTransaction(): parsed Call-ID missing, using raw Call-ID instead (can be empty)", 2)
				self.CallID = copy.copy(trans.message[0].getHeaderValue("Call-ID"))
			self.transaction.append(trans)
			trans.dialog = self
			trans.number = 0
			if trans.isClient:
				if trans.message[0].hasParsedHeaderField("CSeq"):
					self.localCSeq = copy.deepcopy(trans.message[0].getParsedHeaderValue("CSeq"))
				else:
					Log.logDebug("Dialog.appendTransaction(): CSeq not parsed, cant get number", 1)
				self.buildRouteSet(trans.isClient)
			else:
				if trans.message[0].hasParsedHeaderField("CSeq"):
					self.remoteCSeq = copy.deepcopy(trans.message[0].getParsedHeaderValue("CSeq"))
				else:
					Log.logDebug("Dialog.appendTransaction(): CSeq not parsed, cant get number", 1)
				if trans.firstReply is not None:
					self.buildRouteSet(trans.isClient)
			# sanity checks for completness
			if self.localUri is None:
				Log.logDebug("Dialog.appendTransaction(): WARNING: missing local URI", 1)
			if self.remoteUri is None:
				Log.logDebug("Dialog.appendTransaction(): WARNING: missing remote URI", 1)
			if self.CallID is None:
				Log.logDebug("Dialog.appendTransaction(): missing CallID header", 1)
			if (not (self.localCSeq is None or self.remoteCSeq is None)):
				Log.logDebug("Dialog.appendTransaction(): missing CSeq header", 1)
		else:
			# we allready have a running dialog here; if we are the
			# client we either set or update the localCSeq (same op);
			# if we are not the client we have to set or update the
			# remoteCSeq (same operation)
			if (trans.isClient):
				self.localCSeq = copy.deepcopy(trans.CSeq)
			else:
				self.remoteCSeq = copy.deepcopy(trans.CSeq)
			self.transaction.append(trans)
			trans.dialog = self
			trans.number = len(self.transaction)-1
			if (self.localCSeq is None and self.remoteCSeq is None):
				Log.logDebug("Dialog.appendTransaction(): dialog informations incomplete: missing CSeq", 1)
