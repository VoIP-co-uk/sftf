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
# $Id: TestCase.py,v 1.70 2004/05/02 18:58:04 lando Exp $
#
import Config, Log, Helper
from SCException import SCException, SCNotImplemented, HFHException
import DigestAuthentication as DA
import copy
from Dialog import Dialog
from TestResult import TestResult
from Transaction import Transaction
from SipRequest import SipRequest
from SipReply import SipReply
from SipMessage import SipMessage
from NetworkEventHandler import createMediaSockets, compareHostNames, NetworkEventHandler, getTransportNumber
from FileEventHandler import FileEventHandler
import time, socket

class TestCase:
	"""This class implements the interface with all offered functions for
	test case implementations. Every test case have to inherit at least
	this class. These implementations have to overwrite the config and the
	run function of this class.
	For an explanation of the variables of an instances of this class please
	refer to the case_template file.
	"""

	TC_API_VERSION = 0.3

	TC_INIT   = TestResult.TR_INIT
	TC_PASSED = TestResult.TR_PASSED
	TC_FAILED = TestResult.TR_FAILED
	TC_WARN   = TestResult.TR_WARN
	TC_CAUT   = TestResult.TR_CAUT
	TC_CANC   = TestResult.TR_CANC
	TC_ERROR  = TestResult.TR_ERROR

	def __init__(self):
		self.name = None
		self.description = None
		self.isClient = None
		self.transport = None
		#FIXME we should not ignore retrans by default
		self.ignoreRetrans = True
		self.checkAllHeaders = False
		self.fixHeaders = True
		self.autoReact = True
		self.interactRequired = False
		self.register = False
		self.ignoreCSeq = False
		self.ignoreCallID = False
		self.minAPIVersion = None
		self.maxAPIVersion = None
		self.results = []
		self.dialog = []
		self.sink = []

	def __str__(self):
		return '[name:\'' + str(self.name) + '\', ' \
				+ 'description:\'' + str(self.description) + '\', ' \
				+ 'isClient:\'' + str(self.isClient) + '\', ' \
				+ 'transport:\'' + str(self.transport) + '\', ' \
				+ 'results:\'' + str(self.results) + '\', ' \
				+ 'ignoreRetrans:\'' + str(self.ignoreRetrans) + '\', ' \
				+ 'checkAllHeaders:\'' + str(self.checkAllHeaders) + '\', ' \
				+ 'fixHeaders:\'' + str(self.fixHeaders) + '\', ' \
				+ 'autoReact:\'' + str(self.autoReact) + '\', ' \
				+ 'interactRequired:\'' + str(self.interactRequired) + '\', ' \
				+ 'register:\'' + str(self.register) + '\', ' \
				+ 'ignoreCSeq:\'' + str(self.ignoreCSeq) + '\', ' \
				+ 'ignoreCallID:\'' + str(self.ignoreCallID) + '\', ' \
				+ 'minAPIVersion:\'' + str(self.minAPIVersion) + '\', ' \
				+ 'maxAPIVersion:\'' + str(self.maxAPIVersion) + '\', ' \
				+ 'results:\'' + str(self.results) + '\', ' \
				+ 'dialog:\'' + str(self.dialog) + '\']'

	def run(self):
		"""This function will be called by the test frame work to run the
		implementation of the test case. Please always overwrite this function
		in your test case! When this function returns the test is completed.
		"""
		raise SCNotImplemented("TestCase", "run", "not implemented => have to be overwritten by the TestCase")

	def config(self):
		"""This function will be called by the test frame work to get the
		basic settings of the test case instance. These settings, stored in
		the variables of the instance, determine if the loaded test case
		matches the requested type of test to run. This function always have 
		to be overwritten by a test case implementation! When this function
		returns the test frame work will decide if it will run this test or
		not.
		"""
		raise SCNotImplemented("TestCase", "config", "not implemented => have to be overwritten by the TestCase")

	def addResult(self, res, reason, name=None, descr=None):
		"""This function adds the given test result to the result list of
		the test case instance. 'res' should be one of the test results
		defined in the TestCase class. 'reason' can be any string which
		should explain why this result was chosen.
		"""
		r = TestResult(res, reason)
		if name is None:
			r.name = self.name
		else:
			r.name = name
		if descr is None:
			r.description = self.description
		else:
			r.description = descr
		Log.logDebug("TestCase.addResult(): result:" + str(r.result) + " reason:'" + str(r.reason) + "'", 2)
		self.results.append(r)

	def getEndResults(self):
		"""Summes the results from the result list of the
		instance to one number which will be returned.
		"""
		endres = TestResult.TR_INIT
		for i in self.results:
			endres = endres | i.result
		return endres

	def getOneResult(self):
		"""Returns one test result number out of the list of test results
		of the instance. The most significant will be returned, whereby errors
		are more significant then success results.
		INIT > FAILED > ERROR > WARN > CAUT > CANC > PASSED
		"""
		res = self.getEndResults()
		if res == TestResult.TR_INIT:
			res = TestResult.TR_INIT
		elif res & TestResult.TR_FAILED:
			res = TestResult.TR_FAILED
		elif res & TestResult.TR_ERROR:
			res = TestResult.TR_ERROR
		elif res & TestResult.TR_WARN:
			res = TestResult.TR_WARN
		elif res & TestResult.TR_CAUT:
			res = TestResult.TR_CAUT
		elif res & TestResult.TR_CANC:
			res = TestResult.TR_CANC
		elif res & TestResult.TR_PASSED:
			res = TestResult.TR_PASSED
		else:
			raise SCException("TestCase", "getOneResult", "unsupported result type")
		return res

	def userInteraction(self, message, cancel=True):
		"""Prints the given message on the standard output and reads from
		standard input until the return key is pressed. If 'cancel' is True
		ok and cancel will be presented as choises, otherwise only ok. The
		function returns True if return or 'o' was entered. If 'cancel' is
		True and 'c' was entered False will be returned.
		"""
		if Config.USE_GUI:
			raise SCNotImplemented("TestCase", "userInteraction", "a GUI is not implemented yet!")
		else:
			oc = "init"
			if cancel:
				addstr = " [o]k or [c]ancel"
			else:
				addstr = " [o]k"
			while (oc[0] != "o" and oc[0] != "O" and oc[0] != "C" and oc[0] != "c"):
				# FIXME replace raw_input with a single key reader
				oc = raw_input(message + addstr)
				if len(oc) == 0:
					return True
			if cancel:
				if oc == "c":
					self.addResult(TestResult.TR_CANC, "canceled by user")
					return False
				else:
					return True
			else:
				return True

	def addResource(self, resource):
		"""Adds the given resource to the "global" resource list.
		"""
		if not hasattr(Config, "resources"):
			Log.logDebug("TestCase.addResource(): initiating resource list", 5)
			Config.resources = {'NEH': {}, 'MediaSockets': [], 'FEH': {}, 'XMLEH': {}}
		if isinstance(resource, NetworkEventHandler):
			trp = resource.getTransport()
			key = str(resource.transp) + str(resource.ip) + str(resource.port)
			if trp == "UDP":
				key +=  "00"
			elif trp == "TCP":
				if resource.state == NetworkEventHandler.NEH_CONNECTED:
					key += str(resource.remoteip) + str(resource.remoteport)
				else:
					key += "00"
			else:
				raise SCException("TestCase", "addResource", "unsupported protocol used by NetworkEventHandler")
			Log.logDebug("TestCase.addResource(): adding resource to NEH list with key '" + key + "'", 5)
			Config.resources['NEH'][key] = resource
		elif isinstance(resource, FileEventHandler):
			Log.logDebug("TestCase.addResource(): adding resource to FEH list with key '" + str(resource.filename) + "'", 5)
			Config.resources['FEH'][str(resource.filename)] = resource
		else:
			Log.logDebug("TestCase.addResource(): adding resource to MediaSockets list", 5)
			Config.resources['MediaSockets'].append(resource)

	def findNEH(self, _transport, _lip, _lport, _rip, _rport):
		"""Searches for a NetworkEventHandler with the given parameters
		transport, ip and port in the "global" resource list. Returns 
		a list of the found NetworkEventHandler's, which might be empty.
		"""
		Log.logDebug("TestCase.findNEH(): called with transport: " + str(_transport) + " lip: " + str(_lip) + " lport: " + str(_lport) + " rip: " + str(_rip) + " rport: " + str(_rport), 5)
		#ret = []
		if Config.resources.has_key('NEH'):
			key = str(getTransportNumber(_transport)) + str(_lip) + str(_lport)
			if _transport.lower() == "udp":
				key += "00"
			elif _transport.lower() == "tcp":
				key += _rip + _rport
			if Config.resources['NEH'].has_key(key):
				Log.logDebug("TestCase.findNEH(): found NEH with key '" + key + "'", 5)
				return Config.resources['NEH'][key]
			else:
				return None
		else:
			return None
		#	for eh in Config.resources['NEH']:
		#		Log.logDebug("TestCase.findNEH(): NEH transport: " + str(eh.getTransport()) + " ip: " + str(eh.ip) + " port: " + str(eh.port) + " state: " + str(eh.state), 5)
		#		if (_transport.lower() == "udp") and (eh.getTransport() == _transport) and (eh.ip == _lip) and (eh.port == _lport) and (eh.state == NetworkEventHandler.NEH_BOUND):
		#			ret.append(eh)
		#		elif (_transport.lower() == "tcp") and (eh.getTransport() == _transport) and (((eh.remoteip == _rip) and (eh.remoteport == _rport)) or ((eh.ip == _lip) and (eh.port == _lport))) and (eh.state == NetworkEventHandler.NEH_CONNECTED):
		#			ret.append(eh)
		#Log.logDebug("TestCase.findNEH(): found " + str(len(ret)) + " NEHs", 5)
		#return ret

	def findFEH(self, _filename):
		"""Searches for a FileEventHandler with the given filename. Returns
		a list of the found FileEvnetHandler's, which might be empty.
		"""
		#ret = []
		if Config.resources.has_key('FEH'):
			if Config.resources['FEH'].has_key(_filename):
				Log.logDebug("TestCase.findFEH(): found FEH for " + _filename, 5)
				return Config.resources['FEH'][_filename]
			else:
				return None
		else:
			return None
			#for eh in Config.resources['FEH']:
			#	if eh.filename == _filename:
			#		ret.append(eh)
		#Log.logDebug("TestCase.findFEH(): found " + str(len(ret)) + " FEHs", 5)
		#return ret

	def newDialog(self):
		"""Adds and returns a new dialog instance."""
		dia = Dialog()
		self.dialog.append(dia)
		dia.number = len(self.dialog)-1
		Log.logDebug("newDialog(): added new dialog number " + str(dia.number), 5)
		return dia

	def newTransaction(self, dia, mes=None):
		"""Adds and returns a new transaction within the given Dialog.
		"""
		if (dia is None) or (not isinstance(dia, Dialog)):
			Log.logDebug("newTransaction(): called with no Dialog instance", 1)
			return None
		trans = Transaction()
		if (mes is not None) and (issubclass(mes.__class__, SipMessage)):
			trans.appendMessage(mes)
		dia.appendTransaction(trans)
		return trans

	def addMessage(self, message, dia=None, trans=None):
		"""Adds the given SipMessage instance 'message' to the correct dialog
		and transaction. If 'dia' and/or 'trans' are not given the correct
		dialog and transaction will be looked up or new one will be created
		and added to this test case instance. Returns True if the message was a 
		retransmissions, otherwise False will be returned.
		"""
		cur_dia = dia
		cur_trans = trans
		tag = None
		if (cur_dia is None) and (cur_trans is not None):
			cur_dia = cur_trans.dialog
		if cur_dia is None:
			# trying to find the dialog first by the To or From tag
			if message.hasParsedHeaderField("To"):
				to = message.getParsedHeaderValue("To")
				if to.tag is not None:
					if to.tag.lower().startswith("sct-"):
						tag = message.getParsedHeaderValue("To").tag
			if (tag is None) and message.hasParsedHeaderField("From"):
				fr = message.getParsedHeaderValue("From")
				if fr.tag is not None:
					if fr.tag.lower().startswith("sct-"):
						tag = message.getParsedHeaderValue("From").tag
			if tag is not None:
				tmp = tag[4:]
				numend = tmp.find("-")
				if numend != -1:
					tmp_num = tmp[:numend]
					if tmp_num.isdigit():
						tag_num = int(tmp_num)
						if len(self.dialog) > tag_num:
							cur_dia = self.dialog[tag_num]
							Log.logDebug("TestCase.addMessage(): dialog found by To/From tag", 5)
		# dialog finding by tag failed, trying by brute force
		if cur_dia is None:
			Log.logDebug("TestCase.addMessage(): dialog tag matching failed, falling back to 2543 matching", 3)
			if (message.hasParsedHeaderField("Call-ID")):
				ci = message.getParsedHeaderValue("Call-ID")
				for i in self.dialog:
					if i.CallID == ci:
						Log.logDebug("TestCase.addMessage(): dialog found by parsed Call-ID", 4)
						cur_dia = i
						break
				if cur_dia is None:
					if self.ignoreCallID:
						Log.logDebug("TestCase.addMessage(): ignoring Call-ID as requested => appending message at last dialog", 2)
						if len(self.dialog) > 0:
							cur_dia = self.dialog[len(self.dialog)-1]
						else:
							cur_dia = self.newDialog()
					elif message.isRequest:
						Log.logDebug("TestCase.addMessage(): no matching dialog found => creating new one", 3)
						cur_dia = self.newDialog()
					elif not self.ignoreCSeq:
						Log.logDebug("TestCase.addMessage(): dropping response without matching dialog", 4)
						#FIXME very dirty hack: if we do not store the message
						# the next try to send a message ends with "bad 
						# filedescriptor"?!
						self.sink.append(message)
						return True
			else:
				Log.logDebug("TestCase.addMessage(): no Call-ID in message => appending at last dialog", 1)
				if len(self.dialog) > 0:
					cur_dia = self.dialog[len(self.dialog)-1]
				else:
					cur_dia = self.newDialog()
		# To prevent that a request from the other side with the
		# same CSeq number and method we also compare if the
		# received status of the message matches with the transaction
		# status (which is inverted to the receive flag)
		if message.event is not None:
			recv = not message.event.received
		else:
			recv = True
		if cur_trans is None:
			# first try to find the transaction by Via branch
			if message.hasParsedHeaderField("Via"):
				via = message.getParsedHeaderValue("Via")
				if via.branch is not None:
					if via.branch.startswith("z9hG4bK-SCb-"):
						tmp = via.branch[12:]
						numend = tmp.find("-")
						if numend != -1:
							tr_num = int(tmp[:numend])
							if tr_num <= len(cur_dia.transaction):
								if message.hasParsedHeaderField("CSeq") and (message.getParsedHeaderValue("CSeq").number == cur_dia.transaction[tr_num].CSeq.number) and (cur_dia.transaction[tr_num].isClient != recv):
									cur_trans = cur_dia.transaction[tr_num]
									Log.logDebug("TestCase.addMessage(): transaction found by SFTF Via branch", 5)
					elif via.branch.startswith("z9hG4bK"):
						for i in cur_dia.transaction:
							if (i.message[0] is not None) and (i.message[0].hasParsedHeaderField("Via")) and (i.message[0].getParsedHeaderValue("Via").branch is not None) and (i.message[0].getParsedHeaderValue("Via").branch == via.branch):
								# to protect us from broken implementations 
								# which reuse same via branch for several 
								# transactions check the CSeq number too
								if message.hasParsedHeaderField("CSeq") and (message.getParsedHeaderValue("CSeq").number != i.CSeq.number):
									Log.logTest("re-use of Via branch value for different transactions is not RFC3261 compliant!!!")
									Log.logDebug("TestCase.addMessage(): re-use of Via branch value for different transactions is not RFC3261 compliant!!!", 1)
								elif (i.isClient != recv):
									cur_trans = i
									Log.logDebug("TestCase.addMessage(): transaction found by branch", 5)
									break;
		if cur_trans is None:
			Log.logDebug("TestCase.addMessage(): finding transaction by branch failed, trying by brute force", 3)
			if len(cur_dia.transaction) == 0:
				Log.logDebug("TestCase.addMessage(): dialog without transaction => creating new one", 5)
			elif message.hasParsedHeaderField("CSeq"):
				m_cseq = message.getParsedHeaderValue("CSeq")
				if message.isRequest and (message.method in ["ACK", "CANCEL"]):
					for i in cur_dia.transaction:
						if (i.isClient == recv) and (i.CSeq.number == m_cseq.number):
							cur_trans = i
							break
				elif message.isRequest:
					for i in cur_dia.transaction:
						if (i.isClient == recv) and (i.CSeq == m_cseq):
							cur_trans = i
							break
				else:
					for i in cur_dia.transaction:
						if i.CSeq == m_cseq:
							cur_trans = i
							break
			elif message.hasHeaderField("CSeq"):
				Log.logDebug("TestCase.addMessage(): Warning: message has no parsed CSeq => using raw CSeq value", 3)
				csval = message.getHeaderValue("CSeq")
				for i in cur_dia.transaction:
					if i.CSeq.create().replace('\r', '').replace('\n', '') == csval:
						cur_trans = i
						break
			else:
				Log.logDebug("TestCase.addMessage(): no CSeq number available => using last transaction", 1)
				cur_trans = cur_dia.transaction[len(cur_dia.transaction)-1]
		if self.ignoreCSeq and (cur_trans is None):
			Log.logDebug("TestCase.addMessage(): ignoring CSeq as requested => appending to last transaction", 2)
			if len(cur_dia.transaction) > 0:
				cur_trans = cur_dia.transaction[len(cur_dia.transaction)-1]
				retrans = cur_trans.appendMessage(message)
			else:
				cur_trans = Transaction()
				retrans = cur_trans.appendMessage(message)
				cur_dia.appendTransaction(cur_trans)
		elif cur_trans is None:
			Log.logDebug("TestCase.addMessage(): no matching transaction found => creating a new one", 2)
			cur_trans = Transaction()
			retrans = cur_trans.appendMessage(message)
			if retrans:
				Log.logDebug("TestCase.addMessage(): WARNING: retransmission in a new transaction? BUG?", 1)
			cur_dia.appendTransaction(cur_trans)
		else:
			Log.logDebug("TestCase.addMessage(): appending message to found transaction", 4)
			retrans = cur_trans.appendMessage(message)
		# Route can only be build during the first transaction
		if cur_trans.number == 0:
			cur_dia.buildRouteSet(cur_trans.isClient)
		return retrans

	def parseMessage(self, _message):
		"""Tries to import the header field handler for each header field
		in '_message' and parses the header if the import was successfull.
		"""
		# try to import header filed parser clases for each
		# header field and call the parser of the class
		for i in _message.getHeaderFieldNames():
			i_mapped = Helper.getMappedHFH(i)
			Log.logDebug("TestCase.parseMessage(): HF: " + str(i) + ", mapped: " + str(i_mapped), 5)
			hf = Helper.createClassInstance(i_mapped)
			if hf is not None:
				parse_s = "hf.parse(_message.getHeaderValue(\"" + i + "\"))"
				try:
					exec parse_s
				except HFHException, inst:
					Log.logDebug(inst.cls + '.' + inst.funct + '(): ' + inst.reason, 1)
				else:
					_message.parsedHeader[i_mapped] = hf
			else:
				Log.logDebug("TestCase.parseMessage(): missing parser for header field '" + i + "'", 4)
		if _message.hasParsedHeaderField("Content-Type"):
			ct = _message.getParsedHeaderValue("Content-Type")
			if ct.type is None:
				Log.logDebug("TestCase.parseMessage(): missing Type in Content-Tape header", 2)
				return
			parser_class = str(ct.type).lower()
			if ct.subtype is not None:
				parser_class += str(ct.subtype).lower()
			pi = Helper.createClassInstance(parser_class)
			if pi is not None:
				try:
					pi.parse(_message.body)
				except Exception, inst:
					Log.logDebug("TestCase.parseMessage(): parsing body failed: " + str(inst), 1)
				else:
					_message.parsedBody = pi
			else:
				Log.logDebug("TestCase.parseMessage(): missing parser for body '" + parser_class + "'", 3)

	def addEvent(self, _event):
		"""Converts the given SipEvent into a SipMessage instance. It calls
		parseMessage and addMessage, and returns the SipMessage instance 
		(either a SipReply instance or a SipRequest instance).
		"""
		message = None
		request = SipRequest()
		reply = SipReply()
		if (request.parseFirstLine(_event.headers[0])):
			request.event =_event
			message = request
		elif (reply.parseFirstLine(_event.headers[0])):
			reply.event = _event
			message = reply
		else:
			Log.logDebug("TestCase.addEvent(): failed to parse first line: SIP message?", 1)
			raise SCException("TestCase", "addEvent", "failed to parse first line: SIP message?")
		message.body = _event.body
		for i in range(1, len(_event.headers)):
			res = message.parseHeaderField(_event.headers[i], self.checkAllHeaders)
			if res:
				self.results.extend(res)
		self.parseMessage(message)
		retrans = self.addMessage(message)
		return message, retrans

	def getLastDialog(self, dia=None):
		"""Returns the latest dialog of this test case instance."""
		# find the dialog
		if len(self.dialog) == 0:
			return None
		if dia is None:
			dia = self.dialog[len(self.dialog)-1]
		return dia

	def getLastTransaction(self, dia=None, trans=None):
		"""Returns the latest transaction of this test case instace."""
		if dia is None:
			dia = self.getLastDialog(dia)
		# find the transaction
		if len(dia.transaction) == 0:
			return None
		elif trans is None:
			trans = dia.transaction[len(dia.transaction)-1]
		elif (not trans in dia.transaction):
			raise SCException("TestCase", "getLastTransaction", "given transaction doesnt belong to given dialog")
		return trans

	def getLastRequest(self, dia=None, trans=None, mes=None):
		"""Returns the dialog, transaction and instance of the latest 
		SipRequest wihtin this instace."""
		dia = self.getLastDialog(dia)
		trans = self.getLastTransaction(dia, trans)
		# find the request
		if mes is None:
			mes = trans.lastRequest
		elif not isinstance(mes, SipRequest):
			raise SCException("TestCase", "getLastRequest", "given message isnt a SipRequest")
		elif not (mes in trans.message):
			raise SCException("TestCase", "getLastRequest", "given message doesnt belong to the transaction")
		return dia, trans, mes

	def getLastReply(self, dia=None, trans=None, mes=None):
		"""Returns the dialog, transaction and instance of latest SipReply 
		within this instance."""
		dia = self.getLastDialog(dia)
		trans = self.getLastTransaction(dia, trans)
		# find the reply
		if mes is None:
			mes = trans.lastReply
		elif not isinstance(mes, SipReply):
			raise SCException("TestCase", "getLastReply", "given message isnt a SipReply")
		elif (not mes in trans.message):
			raise SCException("TestCase", "getLastReply", "given message doesnt belong to the transaction")
		return dia, trans, mes

	def getDiaTrans(self, mes):
		"""Returns the dialog and transaction for the given message. 
		DEPRACETED! Please use the transaction and dialog references from
		the instances instead.
		"""
		if mes is None:
			raise SCException("TestCase", "getDiaTrans", "called with no message")
		for dia in self.dialog:
			for trans in dia.transaction:
				if mes in trans.message:
					return dia, trans
		Log.logDebug("TestCase.getDiaTrans(): no dialog and transaction found", 3)
		return None, None

	def createReply(self, code, reason, mes=None, createEvent=True):
		"""Creates and returns a SipReply with the given code as reply code
		and the given reason phrase in the first line. If 'mes' is None the
		reply will be build for the latest request. To be safe that the reply
		will be build for the desired request, the request should be given as
		'mes'. If 'createEvent' is False the created SipReply will not contain
		a SipEvent, and thus can not be send out directly. The created reply
		message will be added automatically as parsed message to the test case.
		"""
		if mes is None:
			dia, trans, mes = self.getLastRequest(None, None, mes)
		else:
			#dia, trans = self.getDiaTrans(mes)
			trans = mes.transaction
			dia = trans.dialog
		if mes is None:
			raise SCException("TestCase", "createReply", "getLastRequest failed to return request")
		# create the reply
		rep = trans.createReply(code, reason, mes, createEvent)
		self.parseMessage(rep)
		self.addMessage(rep)
		return rep

	def createChallenge(self, mes=None, realm=None, qop=False, proxy=False):
		"""Creates and returns a challenge reply for the latest request. If
		'mes' is given the reply is created for that message. If 'qop' is
		True, the Authorization header will include qop=auth. If 'proxy' is
		True the reply will be 407 otherwise 401.
		"""
		if proxy:
			repl = self.createReply(407, "Proxy Authentication Required", mes, createEvent=False)
			if repl is None:
				raise SCException("TestCase", "createChallenge", "createReply(407, \"Proxy Authentication Required\", createEvent=False) failed")
			auth = Helper.createClassInstance("Proxyauthenticate")
			if realm is not None:
				auth.realm = realm
			auth.qop = qop
			repl.setParsedHeaderValue("Proxy-Authenticate", auth)
			repl.setHeaderValue("Proxy-Authenticate", auth.create())
		else:
			repl = self.createReply(401, "Unauthorized", mes, createEvent=False)
			if repl is None:
				raise SCException("TestCase", "createChallenge", "createReply(401, \"Unauthorized\", createEvent=False) failed")
			auth = Helper.createClassInstance("Wwwauthenticate")
			if realm is not None:
				auth.realm = realm
			auth.qop = qop
			repl.setParsedHeaderValue("WWWAuthenticate", auth)
			repl.setHeaderValue("WWW-Authenticate", auth.create())
		repl.createEvent()
		return repl

	def checkAuthResponse(self, mes=None, username=None, password=None, realm=None):
		"""Returns True when the response in the Autheorization header of the
		latest request is valid, otherwise False. NOTE: just the response value
		will be checked, nothing else. If 'mes' is given the Authorization
		header will checked from this message instead of the latest request.
		If 'username', 'password' and 'realm' are given, these values will be
		used for the calculation of the response, otherwise these values from
		the configuration will be used.
		"""
		if mes is None:
			dia, trans, mes = self.getLastRequest(None, None, mes)
		if mes is None:
			raise SCException("TestCase", "checkAuthResponse", "failed to get the latest request")
		if username is None:
			username = Config.TEST_USER_NAME
		if password is None:
			password = Config.TEST_USER_PASSWORD
		if realm is None:
			realm = Config.AUTH_REALM
		if not mes.hasParsedHeaderField("Authorization"):
			Log.logDebug("TestCase.checkAuthResponse(): Authorization header missing", 2)
			return False
		ah = mes.getParsedHeaderValue("Authorization")
		cr = ah.response
		a1 = DA.HA1(username, realm, password)
		a2 = DA.HA2(mes.method, ah.uri)
		# FIXME: should we use a given qop parameter or the values from 
		# our reply instead of getting them from the UA request ?!?
		if (ah.qop == "auth"):
			sr = DA.response(a1, ah.nonce, a2, ah.nc, ah.cnonce, ah.qop)
		else:
			sr = DA.response(a1, ah.nonce, a2)
		if cr == sr:
			Log.logTest("authentication response is correct")
			return True
		else:
			Log.logTest("authentication failure: client reponse (\'" + cr + "\') does not match calculated response (\'" + sr + "\')")
			return False

	def readMessageFromNetwork(self, _NetworkEventHandler=None, StartTimeout=None, CatchTimeout=True, TimeoutError=True, ignoreRequests=False, ignoreReplies=False, RequestMethod=None):
		"""Reads and returns SIP messages from the given NetworkEventHandler.
		If no SIP message was received which matches teh given criterias until
		the timeout hits None will be returned. NOTE: for now you have to give
		a NetworkEventHandler instance from which to read. If 'StartTimeout'
		is not given the timeouts will be 0.5, 1, 2 and 4 seconds. If 
		'CatchTimeout' is True the function will return None after a timeout
		and add a TestResult ERROR to the result list, otherwiese an exception
		will be reaised on a timeout. If 'TimeoutError' is False no ERROR 
		TestResult will be added to the result list in case of a timeout.
		If 'ignoreRequests' is True only SIP replies will be considered as
		valid messages which will be returned (see readReplxFromNetwork). If
		'ignoreReplies' is True only SIP Request will be considered as valid 
		messages which will be returned (see readRequestFromNetwork). If a
		string is given as 'RequestMethod' only SIP requests with exactly
		that string as request method will be considered as valid messages
		which will be returned.
		The received messages will be parsed and inserted into the right
		dialog and transaction. If 'autoReact' is True for this instance
		the on[ReplyCode|RequestMethod] method will be called if defined, or
		onDefault is no matching onMethod is present.
		"""
		if _NetworkEventHandler is None:
			#raise SCNotImplemented("TestCase", "readMessageFromNetwork", "reading without NetworkEventHandler not implemented")
			neh = self.findNEH(self.transport, Config.LOCAL_IP, Config.LOCAL_PORT, Config.TEST_HOST, Config.TEST_HOST_PORT)
			if neh is None:
				_NetworkEventHandler = NetworkEventHandler(self.transport)
			else:
				#if len(nehs) > 1:
				#	Log.logDebug("TestCase.readMessageFromNetwork(): more then one socket found, using first one", 5)
				_NetworkEventHandler = neh
		if StartTimeout is None:
			Log.logDebug("TestCase.readMessageFromNetwork(): setting default timeout to 0.5", 4)
			StartTimeout = 0.5
			MaxTimeout = Config.DEFAULT_NETWORK_TIMEOUT
		else:
			MaxTimeout = StartTimeout
		_NetworkEventHandler.setReadTimeout(StartTimeout)
		if ignoreRequests and ignoreReplies:
			Log.logDebug("TestCase.readMessageFromNetwork(): WARNING (implementation bug?):ignoring requests and replis is not reasonable, ignoring options", 1)
			ignoreRequests = ignoreReplies = False
		if (not self.autoReact) and (ignoreRequests or ignoreReplies):
			Log.logDebug("TestCase.readMessageFromNetwork(): WARNING: ignoreRequests or ignoreReplies is on, but automatic reaction is turned off, reasonable?", 1)
		if (not RequestMethod is None) and (ignoreRequests is True):
			Log.logDebug("TestCase.readMessageFromNetwork(): WARNING: ignoreRequests AND RequestMethod set, senceless, ignoring RequestMethod", 1)
			RequestMethod = None
		ev = None
		evtime = None
		start = time.time()
		while ev is None:
			while (_NetworkEventHandler.timeout <= MaxTimeout) and (ev is None):
				try:
					ev = _NetworkEventHandler.readEvent()
				except socket.error, inst:
					if inst[0] == 10054:
						self.addResult(TestResult.TR_ERROR, "received ICMP error from remote for the last message while trying to read")
						return None
					else:
						raise inst
				if ev is None:
					_NetworkEventHandler.setReadTimeout(_NetworkEventHandler.timeout*2)
			if ev is None:
				if CatchTimeout:
					Log.logDebug("TestCase.readMessageFromNetwork(): timeout while reading from network", 1)
					Log.logTest("timeout while reading from network")
					if TimeoutError:
						self.addResult(TestResult.TR_ERROR, "timeout while reading from network")
					return None
				else:
					raise SCException("TestCase", "readMessageFromNetwork", "timed out during reading from network")
			elif len(ev.rawEvent.data) < 10:
				# i think valid SIP request have to be at least 75 bytes, 
				# but maybe someone wants to add audio support where packets may be smaller
				Log.logDebug("TestCase.readMessageFromNetwork(): packet < 10 bytes, dropping", 3)
				Log.logTest("WARNING: received packets smaller then 10 bytes")
				evtime = ev.time
				ev = None
			else:
				mes, retrans = self.addEvent(ev)
				if Config.resources['XMLEH'].has_key(self.name):
					Config.resources['XMLEH'][self.name].writeMessage(mes)
				if self.ignoreRetrans and retrans:
					Log.logDebug("TestCase.readMessageFromNetwork(): ignoring received re-transmission", 2)
					_NetworkEventHandler.setReadTimeout(StartTimeout)
					evtime = ev.time
					ev = None
				else:
					if self.autoReact:
						self.reactOn(mes)
					evtime = ev.time
					if mes.isRequest and ignoreRequests:
						ev = None
					elif (not mes.isRequest) and ignoreReplies:
						ev = None
					elif mes.isRequest and (not RequestMethod is None) and (mes.method.lower() != RequestMethod.lower()):
						Log.logDebug("TestCase.readMessageFromNetwork(): ignoring unwatend request type '" + str(mes.method) + "'", 4)
						ev = None
					else:
						return mes
			if not evtime is None:
				elapsed = Helper.timeDiff(evtime, start)
				if elapsed > MaxTimeout:
					Log.logDebug("TestCase.readMessageFromNetwork(): elapsed time is bigger then Maxtimeout => timeout", 5)
					return None
				remain = MaxTimeout - elapsed
				Log.logDebug("TestCase.readMessageFromNetwork(): setting remaining timeout to " + str(remain),5)
				_NetworkEventHandler.setReadTimeout(remain)
				evtime = None
		return None

	def readReplyFromNetwork(self, _NetworkEventHandler=None, StartTimeout=None, CatchTimeout=True, TimeoutError=True):
		"""A convenient function which calls readMessageFromNetwork and only
		return replies. For the parameters please refer to the description
		of redMessageFromNetwork.
		"""
		return self.readMessageFromNetwork(_NetworkEventHandler, StartTimeout, CatchTimeout, TimeoutError, ignoreRequests=True, ignoreReplies=False, RequestMethod=None)

	def readRequestFromNetwork(self, _NetworkEventHandler=None, StartTimeout=None, CatchTimeout=True, TimeoutError=True, RequestMethod=None):
		"""A concenient function which calls readMessageFromNetwork and only
		return requests. For the parameters please refer to the description
		of readMessageFromNetwork.
		"""
		return self.readMessageFromNetwork(_NetworkEventHandler, StartTimeout, CatchTimeout, TimeoutError, ignoreRequests=False, ignoreReplies=True, RequestMethod=RequestMethod)

	def setBody(self, body, mes=None):
		"""Sets the body of the last message to the given 'body' value.
		If 'mes' is given that message will be used instead of the last one.
		"""
		if mes is None:
			dia = self.getLastDialog(None)
			trans = self.getLastTransaction(dia, None)
			mes = trans.message[len(trans.message)-1]
		mes.body = body
		
		mes.setHeaderValue("Content-Length", str(Helper.calculateBodyLength(mes.body)) + "\r\n")

	def setOnHoldBody(self, mes=None):
		"""Sets the body of the last message with a SDP description which
		contains on hold to prevent reseiving media. If 'mes' is given that
		message will be used instead of the last message.
		"""
		if mes is None:
			dia = self.getLastDialog(None)
			trans = self.getLastTransaction(dia, None)
			mes = trans.message[len(trans.message)-1]
		self.setBody(Helper.createDummyBody(), mes)
		mes.setHeaderValue("Content-Type", "application/sdp\r\n")

	def setMediaBody(self, mes=None, sock=None, checksend=True):
		"""Inserts a SDP body with a real listening socket into the last
		message. Returns the listening media socket. If 'mes' is given that 
		message will be used instead of the	last one. If 'sock' is None a
		random socket will be created and returned, otherwiese the given socket
		will be used for the SDP description. If the method is called for a
		reply and 'checksend' is True, the send/recv attribute will be adjusted
		according to the attribute of the original request. Otherwiese the
		send/recv attribute will be 'sendrecv'.
		"""
		if sock is None:
			sockpair, ip, port = createMediaSockets()
		else:
			ip, port = sock.getsockname()
			sockpair = (sock, None)
		body = Helper.createDummyBody()
		body[2] = body[2].replace("Dummy on hold", "Media dummy")
		body[3] = body[3].replace("0.0.0.0", str(ip))
		body[4] = body[4].replace("m=audio 65534", "m=audio " + str(port))
		if checksend and (mes is not None) and (not mes.isRequest) and (not mes.request is None) and (not mes.request.parsedBody is None) and (not mes.request.parsedBody.state is None):
			rstate = mes.request.parsedBody.state
			if rstate == 'sendrecv':
				body[6] = body[6].replace("recvonly", "sendrecv")
			elif rstate == 'recvonly':
				body[6] = body[6].replace("recvonly", "sendonly")
			elif rstate == 'inactive':
				body[6] = body[6].replace("recvonly", "inactive")
		else:
			body[6] = body[6].replace("recvonly", "sendrecv")
		self.setBody(body, mes)
		if (sock is None):
			self.addResource(sockpair)
		return sockpair
		
	def createRequest(self, method, ruri=None, trans=None, dia=None, createEvent=True):
		"""Creates and returns a SIP request with the given 'method' as request
		method. If 'ruri' is None the request URI will constructed out of the
		username, hostname and port of the target from the configuration, 
		otherwise 'ruri' will be used. If 'trans' and 'dia' are None the last
		request will belong to the last unterminated dialog, or a new dialog
		will be created. Otherwise the given transaction and/or dialog will be
		used. NOTE: for ACK's and CANCEL's the transaction should be given and
		for BYE's the dialog should be given to avoid errors. If 'createEvent'
		is False no SIPEvent will be created and the request can not be sent 
		out directly.
		The created request will be parsed and inserted into the right dialog
		and transaction.
		"""
		Log.logDebug("TestCase.createRequest(): entered with method=\'" + str(method) + "\', ruri=\'" + str(ruri) + "\', trans=\'" + str(id(trans)) + "\', dia=\'" + str(id(dia)) + "\', createEvent=\'" + str(createEvent) + "\'", 5)
		if (method.lower() == "bye") and (dia is None):
			Log.logDebug("TestCase.createRequest(): WARNING creating BYE without dialog!!! You should specify the dialog in the test to send the BYE for!", 1)
 		if (method.lower() == "cancel" or method.lower() == "ack") and (trans is None):
			Log.logDebug("TestCase.createRequest(): WARNING creating ACK or CANCEL without transaction!!! You should specify the transaction in the test to send the ACK or CANCEL for!", 1)
		route = None
		dsthost = None
		if (trans is not None) and (dia is None):
			dia = trans.dialog
			if dia is None:
				raise SCException("TestCase", "createRequest", "the given transaction misses a dialog")
		if dia is None:
			dia = self.getLastDialog()
			if dia is None:
				dia = self.newDialog()
			elif dia.state & Dialog.DI_ST_TERMINATED:
				dia = self.newDialog()
			else:
				if ruri is None:
					ruri, route, dsthost = dia.getRoutingTarget()
				else:
					raise SCException("TestCase", "createRequest", "creating a request from a dialog with a given request-uri is not supported")
		else:
			if ruri is None:
				ruri, route, dsthost = dia.getRoutingTarget()
			else:
				raise SCException("TestCase", "createRequest", "creating a request from a dialog with a given request-uri is not supported")
		if (trans is None) and ((method.lower() == "ack") or (method.lower() == "cancel")):
			trans = self.getLastTransaction(dia, None)
			if (trans is None) and ((method.lower() == "ack") or (method.lower() == "cancel")):
				raise SCException("TestCase", "createRequest", "creating ACK or CANCEL without transaction is not possible")
		req = SipRequest()
		req.method = method
		req.protocol = "SIP"
		req.version = "2.0"
		if (method.lower() == "cancel"):
			ruri = copy.deepcopy(trans.message[0].rUri)
		elif (method.lower() == "ack"):
			if (trans.lastReply is not None) and (trans.lastReply.code != 200):
				ruri = copy.deepcopy(trans.firstRequest.rUri)
		elif ruri is None:
			ruri = Helper.createClassInstance("sip_uri")
			ruri.protocol = "sip"
			ruri.username = str(Config.TEST_USER_NAME)
			ruri.host = str(Config.TEST_HOST)
			ruri.port = str(Config.TEST_HOST_PORT)
		req.rUri = ruri
		if (method.lower() == "ack") and (trans.lastReply is not None) and (trans.lastReply.hasParsedHeaderField("To")):
			req.setHeaderValue("To", trans.lastReply.getParsedHeaderValue("To").create())
		elif (method.lower() == "cancel") and (trans.firstRequest is not None) and (trans.firstRequest.hasParsedHeaderField("To")):
			req.setHeaderValue("To", trans.firstRequest.getParsedHeaderValue("To").create())
		elif dia.remoteUri is None:
			req.setHeaderValue("To", "sip:" + Config.TEST_USER_NAME + "@" + Config.TEST_HOST + "\r\n")
		else:
			req.setHeaderValue("To", dia.remoteUri.create())
		if dia.localUri is None:
			req.setHeaderValue("From", "sip:" + Config.SC_USER_NAME + "@" + Config.LOCAL_IP + "\r\n")
		else:
			req.setHeaderValue("From", dia.localUri.create())
		if dia.CallID is None:
			req.setHeaderValue("Call-ID", str(id(dia)) + "-" + str(hex(int(time.time())))[2:] + "@" + Config.LOCAL_IP + "\r\n")
		else:
			req.setHeaderValue("Call-ID", dia.CallID.create())
		if (method.lower() == "cancel") or (method.lower() == "ack"):
			req.setHeaderValue("CSeq", str(trans.CSeq.number) + " " + str(method) + "\r\n")
		elif dia.localCSeq is None:
			req.setHeaderValue("CSeq", str(Config.LOCAL_CSEQ) + " " + str(method) + "\r\n")
			Config.LOCAL_CSEQ = Config.LOCAL_CSEQ + 1
		else:
			req.setHeaderValue("CSeq", str(dia.localCSeq.number + 1) + " " + str(method) + "\r\n")
		if (method.lower() == "cancel") or (method.lower() == "ack"):
			req.setHeaderValue("Via", trans.message[0].getHeaderValue("Via"))
		else:
			req.setHeaderValue("Via", "SIP/2.0/" + self.transport + " " + str(Config.LOCAL_IP) + ":" + str(Config.LOCAL_PORT) + "\r\n")
		req.setHeaderValue("Max-Forwards", "70\r\n")
		req.setHeaderValue("Contact", "sip:" + Config.SC_USER_NAME + "@" + Config.LOCAL_IP + ":" + str(Config.LOCAL_PORT) + "\r\n")
		if route is not None:
			req.setHeaderValue("Route", route + "\r\n")
		if method.lower() == "invite":
			req.setHeaderValue("Supported", "\r\n")
			self.setOnHoldBody(req)
		else:
			req.setHeaderValue("Content-Length", str(Helper.calculateBodyLength(req.body)) + "\r\n")
		#FIXME add all other mandatory HFs lookuped from a dict
		if createEvent:
			req.createEvent()
			if (method.lower() == "cancel"):
				dsthost = trans.message[0].event.dstAddress
			elif (method.lower() == "ack"):
				if (trans.lastReply.code != 200):
					dsthost = trans.message[0].event.dstAddress
			elif dsthost is None:
				dsthost = (Config.TEST_HOST, int(Config.TEST_HOST_PORT))
			else:
				dsthost = (dsthost[0], dsthost[1])
			req.setEventAddresses((Config.LOCAL_IP, int(Config.LOCAL_PORT), self.transport), dsthost)
		self.parseMessage(req)
		self.addMessage(req, dia, trans)
		return req

	def writeMessageToNetwork(self, _NetworkEventHandler=None, Message=None):
		"""Sends the last message over the given NetworkEventHandler.
		NOTE: for now you have to give the NetworkEventHandler for sending
		the message. If 'Message' is None the last message in the latest
		transaction will be sent, but that should be avoided!
		If fixHeaders is True for this instance header values like the
		Via header, To or From tag etc. will be set correctly. Otherwise
		the message will be sent out like it is.
		"""
		# dirty workaround to prevent the reorder of the function arguments
		if issubclass(_NetworkEventHandler.__class__, SipMessage):
			Message = _NetworkEventHandler
			_NetworkEventHandler = None
		if _NetworkEventHandler is None:
			#raise SCNotImplemented("TestCase", "writeMessageToNetwork", "writing without NetworkEventHandler not implemented")
			neh = self.findNEH(self.transport, Config.LOCAL_IP, Config.LOCAL_PORT, Config.TEST_HOST, Config.TEST_HOST_PORT)
			if neh is None:
				if self.transport == "TCP":
					_NetworkEventHandler = NetworkEventHandler(self.transport, port=0)
				else:
					_NetworkEventHandler = NetworkEventHandler(self.transport)
			else:
			#	if len(nehs) > 1:
			#		Log.logDebug("writeMessageToNetwork(): more then one socket found, using first one", 5)
				_NetworkEventHandler = neh
		if Message is None:
			trans = self.getLastTransaction()
			Message = trans.message[len(trans.message)-1]
		if (Message.event is not None) and Message.event.received:
			raise SCException("TestCase", "writeMessageToNetwork", "last message is received, wont send received messages")
		if self.fixHeaders:
			trans = Message.transaction
			dia = trans.dialog
			if dia is None:
				raise SCException("TestCase", "writeMessageToNetwork", "no dialog found for message")
			elif dia.localUri.tag is None:
				dia.localUri.tag = "SCt-" + str(dia.number) + "-" + str(time.time()) + "-" + Config.LOCAL_IP + "~" + str(self.__class__.__name__)
			if trans is None:
				raise SCException("TestCase", "wirteMessageToNetwork", "no transaction found for message")
			if isinstance(Message, SipRequest):
				mes_req = True
				man_hfh = Helper.get_req_hfh_dict(Message.method)
			elif isinstance(Message, SipReply):
				mes_req = False
				man_hfh = Helper.get_rpl_hfh_dict(Message.code)
				if man_hfh is None:
					Log.logDebug("TestCase.writeMessageToNetwork(): trying generic lookup of the reply code", 3)
					code_generic = (Message.code / 100) * 100
					man_hfh = Helper.get_rpl_hfh_dict(code_generic)
			else:
				raise SCException("TestCase", "writeMessageToNetwork", "unsupported type of message to lookup the mandatory HFH")
			if man_hfh is None:
				Log.logDebug("TestCase.writeMessageToNetowkr(): missing table of mandatory headers", 2)
			else:
				for hfh in man_hfh:
					if not Message.hasParsedHeaderField(hfh):
						Log.logDebug("TestCase.writeMessageToNetwork(): WARNING: message misses mandatory header " + hfh, 1)
						Log.logTest("TestCase.writeMessageToNetwork(): WARNING: message misses mandatory header " + hfh)
						#FIXME we should insert the missing HFH here
						#hfh_m = Helper.getMappedHFH(hfh)
						#if hfh_m is not None:
						#	import_s = "import " + hfh_m
						#	instance_s = "inst =" + hfh_m + "." + hfh_m + "()"
						#	exec import_s
						#	exec instance_s
					if hfh == "Via":
						regen = False
						via = Message.getParsedHeaderValue("Via")
						if mes_req:
							if via.branch is None:
								via.branch = "z9hG4bK-SCb-" + str(trans.number) + "-" + str(time.time()) + "-" + Config.LOCAL_IP
								regen = True
							if _NetworkEventHandler.getTransport() != via.transport.upper():
								via.transport = _NetworkEventHandler.getTransport()
								regen = True
							if not compareHostNames(via.host, _NetworkEventHandler.ip):
								via.host = _NetworkEventHandler.ip
								regen = True
							port = via.port
							if port is None:
								port = 5060
							if port != _NetworkEventHandler.port:
								via.port = _NetworkEventHandler.port
								regen = True
						else:
							if (via.rport is not None) and (via.rport == "empty"):
								via.rport = Message.request.event.srcAddress[1]
								regen = True
							if via.received is not None:
								via.received = Message.request.event.srcAddress[0]
								regen = True
							elif not compareHostNames(via.host, Message.request.event.srcAddress[0]):
								via.received = Message.request.event.srcAddress[0]
								regen = True
						if regen:
							if mes_req and (via.rport is None):
								via.rport = "empty"
							Message.setHeaderValue("Via", via.create())
			if len(Message.body) > 0:
				if not Message.hasParsedHeaderField("Content-Type"):
					ct = Helper.createClassInstance("Contenttype")
					ct.type = "application"
					ct.subtype = "sdp"
					Message.setParsedHeaderValue("Content-Type", ct)
					Message.setHeaderValue("Content-Type", ct.create())
			if trans.isClient:
				fm = Message.getParsedHeaderValue("From")
				if fm.tag is None:
					fm.tag = dia.localUri.tag
					Message.setHeaderValue("From", fm.create())
				elif fm.tag != dia.localUri.tag:
					Log.logDebug("TestCase.writeMessageToNetwork(): From tag differes from dialog tag", 2)
			else:
				to = Message.getParsedHeaderValue("To")
				if to.tag is None:
					to.tag = dia.localUri.tag
					Message.setHeaderValue("To", to.create())
				elif to.tag != dia.localUri.tag:
					Log.logDebug("TestCase.writeMessageToNetwork(): To tag differes from dialog tag", 2)
			#FIXME is it correct to put the Route into EVERY request and reply?
			if mes_req:
				if dia.RouteSet is not None:
					if not Message.hasParsedHeaderField("Route"):
						uri, routeset, dsthost = dia.getRoutingTarget()
						Message.setEventAddresses((Config.LOCAL_IP, int(Config.LOCAL_PORT), self.transport), dsthost)
			else:
				#FIXME add RR header for < 300
				Message.setEventAddresses((Message.request.event.dstAddress[0], Message.request.event.dstAddress[1], self.transport), Message.request.getReplyAddress())
			Message.createEvent()
		_NetworkEventHandler.writeEvent(Message.event)
		if Config.resources['XMLEH'].has_key(self.name):
			Config.resources['XMLEH'][self.name].writeMessage(Message)

	def reactOn(self, message):
		"""This function will be called by readMessageFromNetwork if autoReact
		is True for this instance. It will try to find a matching onXXX 
		function and call it or call otherwise onDefault[Method|Code].
		"""
		if message is None:
			raise SCException("TestCase", "reactOn", "missing message to react on")
		if message.isRequest:
			on_str = "on" + str(message.method)
		else:
			on_str = "on" + str(message.code)

		if hasattr(self, on_str):
			try:
				exec("self." + on_str + "(message)")
			except TypeError, param:
				Log.logDebug("TestCase.reactOn(): TypeError: " + str(param), 1)
				Log.logDebug("TestCase.reactOn(): attribute defined for \'" + on_str + "\', but call failed", 1)
		else:
			if message.isRequest:
				Log.logDebug("TestCase.reactOn(): no method found for \'" + on_str + "\', calling onDefaultMethod...", 1)
				self.onDefaultMethod(message)
			else:
				Log.logDebug("TestCase.reactOn(): no method found for \'" + on_str + "\', calling onDefaultCode...", 1)
				self.onDefaultCode(message)
	
	def onINVITE(self, message):
		"""The default autoReact method will answer all incoming INVITE's
		with '404 Not Found'. Please overwrite if you want to process INVITE's.
		"""
		Log.logDebug("TestCase.onINVITE(): replying with 200 (with SDP=on_hold)", 4)
		replok = self.createReply(404, "Not Found", mes=message)
		self.writeMessageToNetwork(Message=replok)
	
	def onACK(self, message):
		"""The default autoReact method for ACK's does nothing then just
		logging that an ACK was received.
		"""
		Log.logDebug("TestCase.onACK(): nothing to do for an ACK", 4)

	def onBYE(self, message):
		"""The default autoReact method for BYE's will answer with 200 OK just
		to make the UA on the other side happy.
		"""
		Log.logDebug("TestCase.onBYE(): replying with 200 to make UA happy", 4)
		replok = self.createReply(200, "OK", mes=message)
		self.writeMessageToNetwork(Message=replok)

	def onREGISTER(self, message):
		"""The default autoReact method for REGISTER's answers with 200 OK
		to make the UA happy.
		"""
		Log.logDebug("TestCase.onREGISTER(): replying with 200 to make UA happy", 4)
		replok = self.createReply(200, "OK", mes=message)
		self.writeMessageToNetwork(Message=replok)

	def onDefaultMethod(self, message):
		"""The default autoReact method for all other/unknown request methods,
		like SUBSCRIBE, NOTIFY, INFO etc., answers with '501 Not Implemeted'.
		"""
		Log.logDebug("TestCase.onDefaultMethod(): replying with 501", 4)
		repl501 = self.createReply(501, "Not Implemented", mes=message)
		self.writeMessageToNetwork(Message=repl501)

	def onDefaultCode(self, message):
		"""The default autoReact method for replies will answer with ACK if
		required (INVITE), otherwise just log it.
		"""
		if message.code >= 200:
			if (message.hasParsedHeaderField("CSeq") and (message.getParsedHeaderValue("CSeq").method == "INVITE")) or (message.transaction.firstRequest.method == "INVITE"):
				Log.logDebug("TestCase.onDefaultCode(): replying with ACK", 4)
				ack= self.createRequest("ACK", trans=message.transaction)
				self.writeMessageToNetwork(Message=ack)
			else:
				Log.logDebug("TestCase.onDefaultCode(): request wasnt INVITE, no ACK required", 4)
		else:
			Log.logDebug("TestCase.onDefaultCode(): ignoring provisional response", 4)

	def on100(self, message):
		"""The default autoReact method for 100 replies does nothing except 
		logging it.
		"""
		Log.logDebug("TestCase.on100(): ignoring provisional 100", 2)
	
	def on486(self, message):
		"""The default autoReact method for '486 Busy' requests the user to
		hangup the phone, press a key when ready again, and then will retry
		it with the same request again.
		"""
		ack = self.createRequest("ACK", trans=message.transaction)
		Log.logDebug("TestCase.on486(): sending ACK for 486", 2)
		self.writeMessageToNetwork(Message=ack)
		Log.logTest("received 486 during test, requestion hangup by user before retrying")
		self.userInteraction("The UA is busy. Please hangup and press ENTER when ready to proceed", cancel=False)
		self.reTry(message.request)

	def getParsedHeaderInstance(self, name):
		"""Returns an empty instance of the given header field if a parser
		could be importet from the header field handler directory. In case
		no parser is present for the given 'name' None will be returned.
		"""
		return Helper.createClassInstance(Helper.getMappedHFH(name))

	def reTry(self, message):
		"""Tries to re-send the given message but with a new dialog and/or
		transaction if required. Will be called by the default on486 method.
		"""
		if message is None:
			Log.logDebug("TestCase.reTry(): ERROR: called with None as message!", 1)
			return
		elif not message.isRequest:
			Log.logDebug("TestCase.reTry(): ERROR: nothing to do for a reply!", 1)
			return
		elif (message.method == "ACK") or (message.method == "CANCEL"):
			Log.logDebug("TestCase.reTry(): ERROR: nothing to do for a " + str(message.method) + "!", 1)
			return
		new_mes = copy.deepcopy(message)
		new_mes.transaction = None
		dia = self.newDialog()
		ci = new_mes.getParsedHeaderValue("Call-ID")
		ci.str = str(id(dia))
		new_mes.setHeaderValue("Call-ID", ci.create())
		via = new_mes.getParsedHeaderValue("Via")
		via.branch = None
		cs = new_mes.getParsedHeaderValue("CSeq")
		Config.LOCAL_CSEQ = Config.LOCAL_CSEQ + 1
		cs.number = Config.LOCAL_CSEQ
		new_mes.setHeaderValue("CSeq", cs.create())
		new_mes.createEvent()
		self.addMessage(new_mes, dia)
		Log.logDebug("TestCase.reTry(): retrying same request with new Call-ID and CSeq", 2)
		self.writeMessageToNetwork(message.event.rawEvent, new_mes)
