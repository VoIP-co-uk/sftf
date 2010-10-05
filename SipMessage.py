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
# $Id: SipMessage.py,v 1.25 2004/03/30 21:52:36 lando Exp $
#
import SipEvent, Log, Helper
from TestResult import TestResult
from SCException import SCException, SCNotImplemented

class SipMessage:
	"""This class provides generic code for SIP requests and replies.
	"""

	def __init__(self):
		self.protocol = None
		self.version = None
		self.headerFields = {}
		self.parsedHeader = {}
		self.body = []
		self.parsedBody = None
		self.event = None
		self.transaction = None
		self.isRequest = None

	def __str__(self):
		return '[protocol:\'' + str(self.protocol) + '\', ' \
				+ 'version:\'' + str(self.version) + '\', ' \
				+ 'headerFields:\'' + str(self.headerFields) + '\', ' \
				+ 'parsedHeader:\'' + str(self.parsedHeader) + '\', ' \
				+ 'body:\'' + str(self.body) + '\', ' \
				+ 'parsedBody:\'' + str(self.parsedBody) + '\', ' \
				+ 'event:\'' + str(self.event) + '\', ' \
				+ 'transaction:\'' + str(id(self.transaction)) + '\', ' \
				+ 'isRequest:\'' + str(self.isRequest) + '\']'

	def getHeaderFieldNames(self):
		"""Returns a sequence off all header field names of this message
		instance.
		"""
		return self.headerFields.keys()

	def hasHeaderField(self, hfName):
		"""Returns a boolean if the given header filed is present in the
		message.
		"""
		return self.headerFields.has_key(hfName.replace("-", "").capitalize())

	def getHeaderValue(self, hfName):
		"""Returns the raw content of the given header field. If the header
		field is not present in the message None is returned.
		"""
		if self.headerFields.has_key(hfName.replace("-", "").capitalize()):
			return self.headerFields[hfName.replace("-", "").capitalize()]
		else:
			return None

	def setHeaderValue(self, hfName, hfValue):
		"""Sets the value of the given header field. The header filed
		will be added if not present and overwritten if present. If the
		header field name is known from RFC it will be written like in the
		BNF of RFC3261 and only the value will kept raw. If the header field
		name is not know also the raw name will be used.
		"""
		if Helper.getRevMappedHFH(Helper.getMappedHFH(hfName)):
			self.headerFields[Helper.getMappedHFH(hfName)] = hfValue
		else:
			self.headerFields[hfName] = hfValue

	def removeHeaderField(self, hfName):
		"""Removes the given header field from the message.
		"""
		if self.headerFields.has_key (hfName.replace("-", "").capitalize()):
			del self.headerFields[hfName.replace("-", "").capitalize()]
	
	def parseHeaderField(self, headerStr, checkHeaderNames):
		"""Trys to genericly seperate the given line into the header field 
		name and the value. If the second parameter is True the header field
		name is checked if is written like in the BNF of RFC3261. In case
		it is not written like in the RFC3261 a sequence of TestResults
		(result CAUTION) will be returned.
		"""
		ret = []
		try:
			index = headerStr.index(':')
		except:
			Log.logDebug("SipMessage.parseHeaderField(): failed to find the name-value sperator in: " + str(headerStr), 2)
			return ret
		if checkHeaderNames:
			hfn_raw = headerStr[0:index].strip()
			if hfn_raw.capitalize() in Helper.rfc_headers:
				if not (hfn_raw in Helper.rfc_bfn_headers):
					ret.append(TestResult(TestResult.TR_CAUT, "header name '" + str(hfn_raw) + "' is not exactly written as in RFC3261's BNF"))
			else:
				Log.logDebug("SipMessage.parseHeaderFiled(): header field name '" + str(hfn_raw) + "' is not in RFC3261", 2)
		hfn = Helper.getMappedHFH(headerStr[0:index].rstrip())
		if (self.headerFields.has_key(hfn) and (hfn in Helper.multiple_headers)):
			self.setHeaderValue(hfn, self.getHeaderValue(hfn).rstrip() + \
				", " + headerStr[index+1:].lstrip())
		else:
			self.setHeaderValue(hfn, headerStr[index+1:].lstrip())
		return ret

	def parseFirstLine(self, fLine):
		"""Trys to parse the first line of the message. Not implemented in
		this class.
		"""
		raise SCNotImplemented("SipMessage", "parseFirstLine", "not implemented")

	def createFirstLine(self):
		"""Generates the first line of a message. Not implemented in this 
		class.
		"""
		raise SCNotImplemented("SipMessage", "createFirstLine", "not implemented")

	def createEvent(self):
		"""Creates a SIP event out of the data in the instance.
		"""
		src = dst = None
		if self.event is not None:
			src = self.event.srcAddress
			dst = self.event.dstAddress
		self.event = SipEvent.SipEvent()
		self.event.body = self.body
		self.createFirstLine()
		# FIXME: should we use any order???
		hf_len = range(0, len(self.headerFields))
		hf = self.headerFields.items()
		for i in hf_len:
			att, val = hf[i]
			att_m = Helper.getRevMappedHFH(att)
			if att_m is None:
				Log.logDebug("SipMessage.createEvent(): unable to map back the HFH: \'" + str(att) + "\'", 3)
				att_m = att
			self.event.headers.append(att_m + ": " + val)
		if (src is not None) and (dst is not None):
			self.setEventAddresses(src, dst)

	def hasParsedHeaderField(self, hfName):
		"""Returns boolean if the message has a parsed header field with
		the given name.
		"""
		hfn_m = Helper.getMappedHFH(hfName)
		if hfn_m is None:
			Log.logDebug("SipMessage.hasParsedHeaderField(): unable to map HFH: " + str(hfName), 3)
			hfn_m = hfName
		return self.parsedHeader.has_key(hfn_m)

	def getParsedHeaderValue(self, hfName):
		"""Returns the object of the parsed header field if present. If the
		header is not present None will be returned.
		"""
		hfn_m = Helper.getMappedHFH(hfName)
		if hfn_m is None:
			Log.logDebug("SipMessage.getParsedHeaderValue(): unable to map HFH: " + str(hfName), 3)
			hfn_m = hfName
		if self.parsedHeader.has_key(hfn_m):
			return self.parsedHeader[hfn_m]
		else:
			return None
	
	def setParsedHeaderValue(self, hfName, hfValue):
		"""Sets the given object as the parsed header field.
		"""
		hfn_m = Helper.getMappedHFH(hfName)
		if hfn_m is None:
			Log.logDebug("SipMessage.setParsedHeaderValue(): unable to map HFH: " + str(hfName), 3)
			hfn_m = hfName
		self.parsedHeader[hfn_m] = hfValue

	def removeParsedHeaderField(self, hfName):
		"""Removes the object with the given name from the list
		of parsed haeder fields.
		"""
		if self.parsedHeader.has_key (hfName.replace("-", "").capitalize()):
			del self.parsedHeader[hfName.replace("-", "").capitalize()]
	
	def setEventAddresses(self, Src, Dst):
		"""Sets the source and destination address of the event in the
		message.
		"""
		if self.event is None:
			raise SCException("SipMessage", "setEventAddresses", "missing event to set addresses")
		if len(Src) != 3:
			raise SCException("SipMessage", "setEventAddresses", "source address requires 3 parameter, got: " + str(Src))
		if len(Dst) != 2:
			raise SCException("SipMessage", "setEventAddresses", "destination address requires 2 parameter, got: " + str(Dst))
		self.event.dstAddress = Dst
		self.event.srcAddress = Src

	def getReplyAddress(self):
		"""Returns a tuple of hostname and port where the reply has to be
		sent to according to the Via header content.
		"""
		h = None
		p = None
		if (self.parsedHeader.has_key("Via")):
			if (self.parsedHeader["Via"].received is not None):
				h = self.event.srcAddress[0]
			elif self.parsedHeader["Via"].rport is not None:
				h = self.event.srcAddress[0]
			else:
				h = self.parsedHeader["Via"].host
			if (self.parsedHeader["Via"].rport is not None):
				p = self.event.srcAddress[1]
			else:
				if (self.parsedHeader["Via"].port is None):
					p = 5060
				else:
					p = self.parsedHeader["Via"].port
		else:
			Log.logDebug("Transaction.createReply(): no parsed Via header found. Using socket defaults", 2)
			h, p = self.event.srcAddress
		return (h, int(p))
