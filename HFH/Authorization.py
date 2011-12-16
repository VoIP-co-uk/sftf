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
# $Id: Authorization.py,v 1.14 2004/03/30 21:52:36 lando Exp $
#
from HeaderFieldHandler import HeaderFieldHandler
import Log
from SCException import SCNotImplemented, HFHException
from TestCase import TestResult

class Authorization (HeaderFieldHandler):

	def __init__(self, value=None):
		HeaderFieldHandler.__init__(self)
		self.username = None
		self.realm = None
		self.nonce = None
		self.uri = None
		self.response = None
		self.algorithm = None
		self.cnonce = None
		self.opaque = None
		self.qop = None
		self.nc = None
		self.params = []
		if value is not None:
			self.parse(value)

	def __str__(self):
		return '[username:\'' + str(self.username) + '\', ' \
				+ 'realm:\'' + str(self.realm) + '\', ' \
				+ 'nonce:\'' + str(self.nonce) + '\', ' \
				+ 'uri:\'' + str(self.uri) + '\', ' \
				+ 'response:\'' + str(self.response) + '\', ' \
				+ 'algorithm:\'' + str(self.algorithm) + '\', ' \
				+ 'cnonce:\'' + str(self.cnonce) + '\', ' \
				+ 'opaque:\'' + str(self.opaque) + '\', ' \
				+ 'qop:\'' + str(self.qop) + '\', ' \
				+ 'nc:\'' + str(self.nc) + '\', ' \
				+ 'params:\'' + str(self.params) + '\']'

	def parse(self, value):
		v = value.replace("\r", "").replace("\t", "").strip()
		if not (v[:6].lower() == "digest"):
			raise HFHException("Authorization","parse", "unsupported auth scheme")
		v = v[7:].lstrip()
		vlen = len(v)
		while (vlen > 0):
			eq = v.find("=")
			lq = v.find("\"")
			cm = v.find(",")
			# find the name
			if ((eq != -1 and eq < cm) or (eq != -1 and cm == -1)):
				name = v[:eq]
			else:
				self.params.append(v)
				break
			# find the value
			if ((lq != -1) and ((lq < cm) or (cm == -1))):
				rq = v[lq+1:].find("\"")
				if (rq != -1):
					nameval = v[lq+1:lq+1+rq]
					oldv = v[:lq+1+rq]
					v = v[lq+2+rq:].lstrip()
					if (v.startswith(",")):
						v = v[1:].lstrip()
				else:
					self.params.append(v)
					raise HFHException("Authorization", "parse", "quotation not closed")
			elif ((eq != -1) and ((eq < cm) or (cm == -1))):
				if cm == -1:
					nameval = v[eq+1:]
					oldv = v
					v = ""
				else:
					nameval = v[eq+1:cm]
					oldv = v[:cm]
					v = v[cm+1:].lstrip()
			else:
				self.params.append(v)
				raise HFHException("Authorization", "parse", "failed to parse authorization tokens")
			# assign the value
			if (name.lower() == "username"):
				self.username = nameval
			elif (name.lower() == "realm"):
				self.realm = nameval
			elif (name.lower() == "nonce"):
				self.nonce = nameval
			elif (name.lower() == "uri"):
				self.uri = nameval
			elif (name.lower() == "response"):
				self.response = nameval
			elif (name.lower() == "algorithm"):
				self.algorithm = nameval
			elif (name.lower() == "cnonce"):
				self.cnonce = nameval
			elif (name.lower() == "opaque"):
				self.opaque = nameval
			elif (name.lower() == "qop"):
				self.qop = nameval
			elif (name.lower() == "nc"):
				self.nc = nameval
			else:
				self.params.append(oldv)
				Log.logDebug("Authorization.parse(): unsupported param", 4)
			vlen = len(v)

	def create(self):
		resp = []
		if self.username:
			resp.append('username="'+self.username+'"')
		if self.realm:
			resp.append('realm="'+self.realm+'"')
		if self.nonce:
			resp.append('nonce="'+self.nonce+'"')
		if self.uri:
			resp.append('uri="'+self.uri+'"')
		if self.response:
			resp.append('response="'+self.response+'"')
		if self.algorithm:
			resp.append('algorithm='+self.algorithm)
		if self.cnonce:
			resp.append('cnonce="'+self.cnonce+'"')
		if self.opaque:
			resp.append('opaque="'+self.opaque+'"')
		if self.qop:
			resp.append('qop="'+self.qop+'"')
		if self.nc:
			resp.append('nc='+self.nc)

		return 'Digest ' + ','.join(resp) + '\r\n'

	def verify(self, auth_HF):
		res = []
		if self.username is None:
			res.append(TestResult(TestResult.TR_FAILED, "missing username in Authorization header"))
		if self.realm is None:
			res.append(TestResult(TestResult.TR_FAILED, "missing realm in Authorization header"))
		if self.nonce is None:
			res.append(TestResult(TestResult.TR_FAILED, "missing nonce in Authorization header"))
		if self.uri is None:
			res.append(TestResult(TestResult.TR_FAILED, "missing uri in Authorization header"))
		if self.response is None:
			res.append(TestResult(TestResult.TR_FAILED, "missing response in Authorization header"))
		if self.qop is not None:
			if self.cnonce is None:
				res.append(TestResult(TestResult.TR_FAILED, "missing cnonce in Authorization header"))
			if self.nc is None:
				res.append(TestResult(TestResult.TR_FAILED, "missing nonce-count in Authorization header"))
		if auth_HF is not None:
			v = auth_HF.replace("\r", "").replace("\t", "").strip()
			if not (v[:6] == "Digest"):
				res.append(TestResult(TestResult.TR_CAUT, "Authorization scheme doesnt confirm to BNF in RFC3261"))
			v = v[7:].lstrip()
			vlen = len(v)
			rem = []
			while (vlen > 0):
				eq = v.find("=")
				lq = v.find("\"")
				cm = v.find(",")
				# find the name
				if ((eq != -1 and eq < cm) or (eq != -1 and cm == -1)):
					name = v[:eq]
				else:
					rem.append(v)
					break
				# find the value
				if ((lq != -1) and ((lq < cm) or (cm == -1))):
					rq = v[lq+1:].find("\"")
					if (rq != -1):
						nameval = v[lq:lq+2+rq]
						oldv = v[:lq+1+rq]
						v = v[lq+2+rq:].lstrip()
						if (v.startswith(",")):
							v = v[1:].lstrip()
					else:
						rem.append(v)
				elif ((eq != -1) and ((eq < cm) or (cm == -1))):
					if cm == -1:
						nameval = v[eq+1:]
						oldv = v
						v = ""
					else:
						nameval = v[eq+1:cm]
						oldv = v[:cm]
						v = v[cm+1:].lstrip()
				else:
					rem.append(v)
				# assign the value
				if (name.lower() == "username"):
					if not (name == "username"):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'username' doesnt conform to BNF in RFC3261"))
					if not (nameval.startswith('"') and nameval.endswith('"')):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'username' value is not quoted. This is not BNF conform"))
				elif (name.lower() == "realm"):
					if not (name == "realm"):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'realm' doesnt conform to BNF in RFC3261"))
					if not (nameval.startswith('"') and nameval.endswith('"')):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'realm' value is not quoted. This is not BNF conform"))
				elif (name.lower() == "nonce"):
					if not (name == "nonce"):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'nonce' doesnt conform to BNF in RFC3261"))
					if not (nameval.startswith('"') and nameval.endswith('"')):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'nonce' value is not quoted. This is not BNF conform"))
				elif (name.lower() == "uri"):
					if not (name == "uri"):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'uri' doesnt conform to BNF in RFC3261"))
					if not (nameval.startswith('"') and nameval.endswith('"')):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'uri' value is not quoted. This is not BNF conform"))
				elif (name.lower() == "response"):
					if not (name == "response"):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'response' doesnt conform to BNF in RFC3261"))
					if not (nameval.startswith('"') and nameval.endswith('"')):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'response' value is not quoted. This is not BNF conform"))
				elif (name.lower() == "algorithm"):
					if not (name == "algorithm"):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'algorithm' doesnt conform to BNF in RFC3261"))
					if nameval.startswith('"') and nameval.endswith('"'):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'algorithm' value is qutoed. This is not BNF conform"))
				elif (name.lower() == "cnonce"):
					if not (name == "cnonce"):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'cnonce' doesnt conform to BNF in RFC3261"))
					if not (nameval.startswith('"') and nameval.endswith('"')):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'cnonce' value is not quoted. This is not BNF conform"))
				elif (name.lower() == "opaque"):
					if not (name == "opaque"):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'opaque' doesnt conform to BNF in RFC3261"))
					if not (nameval.startswith('"') and nameval.endswith('"')):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'opaque' value is not quoted. This is not BNF conform"))
				elif (name.lower() == "qop"):
					if not (name == "qop"):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'qop' doesnt conform to BNF in RFC3261"))
					if nameval.startswith('"') and nameval.endswith('"'):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'qop' value is quoted. This is not BNF conform"))
				elif (name.lower() == "nc"):
					if not (name == "nc"):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'nc' doesnt conform to BNF in RFC3261"))
					if nameval.startswith('"') and nameval.endwith('"'):
						res.append(TestResult(TestResult.TR_CAUT, "Authorization parameter 'nc' value is quoted. This is not BNF conform"))
				else:
					rem.append(oldv)
					Log.logDebug("Authorization.parse(): unsupported param", 4)
				vlen = len(v)
		return res
