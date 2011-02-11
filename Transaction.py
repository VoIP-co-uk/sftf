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
# $Id: Transaction.py,v 1.33 2004/03/30 21:52:36 lando Exp $
#
from SipReply import SipReply
from SipRequest import SipRequest
from Dialog import Dialog
import Log, copy, Helper, Config
from SCException import SCException

class Transaction:
	"""This class stores all informations and provides procedures which are 
	required for SIP transactions.
	"""

	TR_ST_INIT = 0
	TR_ST_READ = 1
	TR_ST_RECV = 2
	TR_ST_SEND = 4
	TR_ST_REQ  = 8
	TR_ST_REPL = 16
	TR_ST_ACK  = 32
	TR_ST_CAN  = 64

	def __init__(self):
		self.state = Transaction.TR_ST_INIT
		self.replyCode = 0
		self.canceled = False
		self.isClient = None
		self.CSeq = None
		self.number = None
		self.message = []
		self.firstRequest = None
		self.firstReply = None
		self.lastRequest = None
		self.lastReply = None
		self.firstACK = None
		self.lastACK = None
		self.firstCAN = None
		self.lastCAN = None
		self.dialog = None

	def __str__(self):
		return '[state:\'' + str(self.state) + '\', ' \
				+ 'replyCode:\'' + str(self.replyCode) + '\', ' \
				+ 'canceled:\'' + str(self.canceled) + '\', ' \
				+ 'isClient:\'' + str(self.isClient) + '\', ' \
				+ 'CSeq:\'' + str(self.CSeq) + '\', ' \
				+ 'number:\'' + str(self.number) + '\', ' \
				+ 'message:\'' + str(self.message) + '\', ' \
				+ 'firstRequest:\'' + str(self.firstRequest) + '\', ' \
				+ 'lastRequest:\'' + str(self.lastRequest) + '\', ' \
				+ 'firstReply:\'' + str(self.firstReply) + '\' ' \
				+ 'lastReply:\'' + str(self.lastReply) + '\', ' \
				+ 'firstACK:\'' + str(self.firstACK) + '\', ' \
				+ 'lastACK:\'' + str(self.lastACK) + '\', ' \
				+ 'firstCAN:\'' + str(self.firstCAN) + '\', ' \
				+ 'lastCAN:\'' + str(self.lastCAN) + '\', ' \
				+ 'dialog:\'' + str(id(self.dialog)) + '\']'

	def appendMessage(self, message):
		"""Appends the given SIP message to the transaction instance. There
		is no check if the message belongs to the transaction. Not only the
		transaction instance, but also the dialog instance of the transaction
		is modified by this function.
		"""
		retrans = False
		if len(self.message) == 0:
			if message.event is not None:
				self.isClient = not message.event.received
			else:
				if (self.state == Transaction.TR_ST_INIT) or \
					(self.state == Transaction.TR_ST_READ):
					self.isClient = True
				else:
					self.isClient = False
			Log.logDebug("Transaction.appendMessage(): isClient set to " + str(self.isClient), 5)
		if isinstance(message, SipRequest):
			if message.method == "ACK":
				self.lastACK = message
				if self.firstACK is None:
					self.firstACK = message
					self.state = self.state | Transaction.TR_ST_ACK
					if self.lastReply is not None:
						if self.replyCode == 200:
							self.dialog.state |= Dialog.DI_ST_ESTABLISHED
						else:
							self.dialog.state |= Dialog.DI_ST_TERMINATED
				else:
					retrans = True
			elif message.method == "CANCEL":
				self.lastCAN = message
				self.canceled = True
				if self.firstCAN is None:
					self.firstCAN = message
					self.state = self.state | Transaction.TR_ST_CAN
				else:
					retrans = True
			else:
				self.lastRequest = message
				if self.firstRequest is None:
					self.firstRequest = message
					self.state = self.state | Transaction.TR_ST_REQ
				else:
					retrans = True
		elif isinstance(message, SipReply):
			self.lastReply = message
			#FIXME should we always update the last reply code?
			if self.replyCode == message.code:
				retrans = True
			else:
				self.replyCode = message.code
			if self.firstReply is None:
				self.firstReply = message
				self.state = self.state | Transaction.TR_ST_REPL
			for j in self.message:
				if j.isRequest:
					if j.hasParsedHeaderField("CSeq") and message.hasParsedHeaderField("CSeq"):
						if j.getParsedHeaderValue("CSeq") == message.getParsedHeaderValue("CSeq"):
							message.request = j
							break
					else:
						if j.getHeaderValue("CSeq") == message.getHeaderValue("CSeq"):
							message.request = j
							break
			if message.hasParsedHeaderField("CSeq"):
				pcs = message.getParsedHeaderValue("CSeq").method
			else:
				pcs = ''
			if (self.dialog is not None):
				if (self.dialog.state & Dialog.DI_ST_ESTABLISHED) and (message.code >= 200) and (pcs == "BYE"):
					self.dialog.state |= Dialog.DI_ST_TERMINATED
				elif (message.code >= 200) and (pcs != "INVITE") and (pcs != "BYE"):
					self.dialog.state |= Dialog.DI_ST_TERMINATED
			if self.isClient:
				if message.code < 200:
					Log.logDebug("Transaction.appendMessage(): ignoring provisional response for target update", 3)
				elif (self.number > 1) and (message.code >= 400):
					Log.logDebug("Transaction.appendMessage(): ignoring negative in dialog reply for target update")
				elif self.dialog and self.dialog.remoteUri:
					if self.dialog.remoteUri.tag is None:
						if message.hasParsedHeaderField("To"):
							if message.getParsedHeaderValue("To").uri.host is not None:
								Log.logDebug("Transaction.appendMessage(): updating remoteUri from reply", 3)
								self.dialog.remoteUri = copy.deepcopy(message.getParsedHeaderValue("To"))
							else:
								Log.logDebug("Transaction.appendMessage(): remoteURI invalid keeping original", 3)
						else:
							Log.logDebug("Transaction.appendMessage(): missing parsed To header, using raw (which can be empty)", 2)
							self.dialog.remoteUri = copy.copy(message.getHeaderValue("To"))
					if message.hasHeaderField("Contact"):
						if message.hasParsedHeaderField("Contact"):
							if message.getParsedHeaderValue("Contact").uri.host is not None:
								Log.logDebug("Transaction.appendMessage(): updating remoteContact from reply", 3)
								self.dialog.remoteContact = copy.deepcopy(message.getParsedHeaderValue("Contact"))
							else:
								Log.logDebug("Transaction.appendMessage(): remoteContact invalid keeping original", 3)
						else:
							Log.logDebug("Transaction.appendMessage(): missing parsed Contact header, using raw (which can be empty)", 2)
							self.dialog.remoteContact = copy.copy(message.getHeaderValue("Contact"))
			else:
				if message.code < 200:
					Log.logDebug("Transaction.appendMessage(): ignoring provisional response for target update", 3)
				elif self.dialog and self.dialog.localUri and (self.dialog.localUri.tag is None):
					if message.hasParsedHeaderField("To"):
						if message.getParsedHeaderValue("To").uri.host is not None:
							Log.logDebug("Transaction.appendMessage(): updating localUri from reply", 3)
							self.dialog.localUri = copy.deepcopy(message.getParsedHeaderValue("To"))
						else:
							Log.logDebug("Transaction.appendMessage(): remoteURI invalid, keeping original", 3)
					else:
						Log.logDebug("Transaction.appendMessage(): missing parsed To header, using raw (which can be empty)", 2)
						self.dialog.localUri = copy.copy(message.getHeaderValue("To"))
		if self.CSeq is not None:
			Log.logDebug("Transaction.appendMessage(): using existing CSeq number", 4)
		elif message.hasParsedHeaderField("CSeq"):
			self.CSeq = copy.deepcopy(message.getParsedHeaderValue("CSeq"))
		elif message.hasHeaderField("CSeq"):
			Log.logDebug("Transaction.appendMessage(): WARNING: CSeq header unparsed => using raw value", 2)
			self.CSeq = copy.copy(message.getHeaderValue("CSeq"))
		else:
			Log.logDebug("Transaction.appendMessage(): ERROR: message and transaction have no CSeq", 1)
		self.message.append(message)
		message.transaction = self
		return retrans
	
	def createReply(self, code, reason, req=None, createEvent=True):
		"""Creates and returns a SIP reply with the given code and reason for
		the transaction instance.
		"""
		Log.logDebug("Transaction.createReply(): entered with code=\'" + str(code) + "\', reason=\'" + str(reason) + "\', createEvent=\'" + str(createEvent) + "\'", 5)
		if req is not None:
			if not req in self.message:
				raise SCException("Transaction", "createReply", "given request isnt in this transaction")
			if not isinstance(req, SipRequest):
				raise SCException("Transaction", "createReply", "message class != SipRequest")
		elif self.lastRequest is not None:
			req = self.lastRequest
		else:
			raise SCException("Transaction", "createReply", "transaction contains no request for reply creation")
		reply = SipReply()
		reply.code = int(code)
		reply.reason = reason
		reply.request = req
		reply.protocol = copy.copy(req.protocol)
		reply.version = copy.copy(req.version)
		# copy only the mandatory HFHs
		cp_hfh = Helper.get_rpl_hfh_dict(code)
		if cp_hfh is None:
			Log.logDebug("Transaction.createReply(): code not in reply HFH table, looking up generic code", 5)
			code_generic = (code / 100) * 100
			cp_hfh = Helper.get_rpl_hfh_dict(code_generic)
		if cp_hfh is None:
			Log.logDebug("Transaction.createReply(): unable to find generic reply in HFH table, copying all HFH", 2)
			reply.headerFields = copy.copy(req.headerFields)
			reply.parsedHeader = copy.deepcopy(req.parsedHeader)
		else:
			for i in cp_hfh:
				if req.hasHeaderField(i):
					reply.setHeaderValue(i, copy.copy(req.getHeaderValue(i)))
				else:
					Log.logDebug("Transaction.createReply(): request missing mandatory HFH: " + str(i), 2)
				i_m = Helper.getMappedHFH(i)
				if i_m is None:
					Log.logDebug("Transaction.createReply(): unable to match HFH: " + str(i), 3)
					i_m = i
				if req.hasParsedHeaderField(i_m):
					reply.setParsedHeaderValue(i_m, copy.deepcopy(req.getParsedHeaderValue(i_m)))
					if i == "Via":
						via = reply.getParsedHeaderValue("Via")
						regen = False
						if via.rport is not None:
							via.rport = req.event.srcAddress[1]
							regen = True
						if via.received is not None:
							via.received = req.event.srcAddress[0]
							regen = True
						if regen:
							reply.setHeaderValue("Via", via.create())
				else:
					Log.logDebug("Transaction.createReply(): request missing mandatory parsed HFH: "+  str(i), 2)
		if code/100 <= 2 and req.hasParsedHeaderField("Record-Route"):
			rr = copy.deepcopy(req.getParsedHeaderValue("Record-Route"))
			reply.setParsedHeaderValue("Record-Route", rr)
			reply.setHeaderValue("Record-Route", rr.create())
		if code/100 == 2 and req.method == "INVITE":
			if (self.dialog is not None):
				con = self.dialog.getLocalContact()
			else:
				con = Helper.createClassInstance("Contact")
				con.uri.protocol = "sip"
				con.uri.username = Config.SC_USER_NAME
				con.uri.host = Config.LOCAL_IP
				con.uri.port = Config.LOCAL_PORT
			reply.setParsedHeaderValue("Contact", con)
			reply.setHeaderValue("Contact", con.create())
			reply.body = Helper.createDummyBody()
		elif code/100 == 2 and req.method == "REGISTER":
			reply.body = []
			if req.hasParsedHeaderField("Contact"):
				reply.setParsedHeaderValue("Contact", copy.deepcopy(req.getParsedHeaderValue("Contact")))
				touri = req.getParsedHeaderValue("To").uri
				co = reply.getParsedHeaderValue("Contact")
				cco = co
				while cco is not None:
					if cco.expires is None:
						if req.hasParsedHeaderField("Expires"):
							cco.expires = req.getParsedHeaderValue("Expires").seconds
						else:
							cco.expires = int(Config.DEFAULT_EXPIRES)
					cco = cco.next
				Helper.usrlocAddContact(touri.create(), co)
				reply.setHeaderValue("Contact", co.create())
			else:
				if req.hasHeaderField("Contact"):
					Log.logDebug("Transaction.createReply(): missing parsed Contact using raw value", 3)
					reply.setHeaderValue("Contact", req.getHeaderValue("Contact"))
				else:
					co = Helper.usrlocGetContacts(req.getParsedHeaderValue("To").uri)
					if co is not None:
						reply.setParsedHeaderValue("Contact", co)
						reply.setHeaderValue("Contact", co.create())
		else:
			con = Helper.createClassInstance("Contact")
			con.uri.protocol = "sip"
			con.uri.username = Config.SC_USER_NAME
			con.uri.host = Config.LOCAL_IP
			con.uri.port = Config.LOCAL_PORT
			con.uri.params = ['transport=UDP']
			reply.setParsedHeaderValue("Contact", con)
			reply.setHeaderValue("Contact", con.create())
			reply.body = []
		cl = Helper.createClassInstance("Contentlength")
		cl.length = Helper.calculateBodyLength(reply.body)
		reply.setHeaderValue("Content-Length", cl.create())
		if (createEvent):
			reply.createEvent()
			reply.setEventAddresses(req.event.dstAddress, req.getReplyAddress())
		return reply
