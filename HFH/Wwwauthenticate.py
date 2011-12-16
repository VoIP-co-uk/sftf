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
# $Id: Wwwauthenticate.py,v 1.3 2004/03/19 18:38:44 lando Exp $
#
from HeaderFieldHandler import HeaderFieldHandler
from SCException import SCNotImplemented, HFHException
from random import Random
import Log, Config

class Wwwauthenticate (HeaderFieldHandler):

	def __init__(self, value=None):
		HeaderFieldHandler.__init__(self)
		self.realm = None
		self.domain = None
		self.nonce = None
		self.algorithm = None
		self.opaque = None
		self.stale = None
		self.qop = None
		self.params = []
		if value is not None:
			self.parse(value)

	def __str__(self):
		return '[realm:\'' + str(self.realm) + '\', ' \
				+ 'domain:\'' + str(self.domain) + '\', ' \
				+ 'nonce:\'' + str(self.nonce) + '\', ' \
				+ 'algorithm:\'' + str(self.algorithm) + '\', ' \
				+ 'opaque:\'' + str(self.opaque) + '\', ' \
				+ 'stale:\'' + str(self.stale) + '\', ' \
				+ 'qop:\'' + str(self.qop) + '\', ' \
				+ 'params:\'' + str(self.params) + '\']'

	def parse(self, value):
		v = value.replace("\r", "").replace("\t", "").strip()
		if (not v.lower().startswith("digest")):
			raise HFHException("WWWAuthenticate", "parse", "unsupported challenge scheme")
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
			if (lq != -1 and (lq < cm or cm == -1)):
				rq = v[lq+1:].find("\"")
				if (rq != -1):
					nameval = v[lq+1:lq+1+rq]
					oldv = v[:lq+1+rq]
					v = v[lq+2+rq:].lstrip()
					if (v.startswith(",")):
						v = v[1:].lstrip()
				else:
					self.params.append(v)
					raise HFHException("WWWAuthenticate", "parse", "quotation not closed")
			elif (eq != -1 and eq < cm):
				nameval = v[eq+1:cm]
				oldv = v[:cm]
				v = v[cm+1:].lstrip()
			elif (eq != -1 and cm == -1):
				nameval = v[eq+1:]
				v = ''
			else:
				self.params.append(v)
				raise HFHException("WWWAuthenticate", "parse", "failed to parse auth token")
			# assign the value
			if (name == "realm"):
				self.realm = nameval
			elif (name == "nonce"):
				self.nonce = nameval
			elif (name == "domain"):
				self.domain = nameval
			elif (name == "algorithm"):
				self.algorithm = nameval
			elif (name == "opaque"):
				self.opaque = nameval
			elif (name == "qop"):
				self.qop = nameval
			elif (name == "stale"):
				self.stale = nameval
			else:
				self.params.append(oldv)
				raise HFHException("WWWAuthenticate", "parse", "unsupported param")
			vlen = len(v)

	def create(self):
		if self.realm is None:
			self.realm = Config.AUTH_REALM
		if self.qop is None:
			self.qop = Config.AUTH_QOP
		resp = 'Digest'
		if self.realm is not None:
			resp = resp + ' realm=\"' + self.realm + '\",'
		if self.domain is not None:
			resp = resp + ' domain=\"' + self.domain + '\",'
		if self.algorithm is not None:
			if self.algorithm != "MD5":
				Log.logDebug("WWWAuthenticate.create(): WARNING: unsupported algorithm", 2)
			resp = resp + ' algorithm=' + self.algorithm + ','
		if self.nonce is not None:
			resp = resp + ' nonce=\"' + self.nonce + '\",'
		else:
			r = Random()
			resp = resp + ' nonce=\"' + 'SipCert'.encode('hex') + str(r.randint(100, 10000)).encode('hex')+ '\",'
		if self.opaque is not None:
			resp = resp + ' opaque=\"' + self.opaque + '\",'
		if self.stale is not None:
			if (self.stale != "true" and self.stale != "false"):
				Log.logDebug("WWWAuthenticate.create(): WARNING: non-RFC stale value", 2)
			resp = resp + ' stale=' + self.stale + ','
		if self.qop is not None:
			if self.qop == True:
				resp = resp + ' qop=\"auth\",'
			elif self.qop != False:
				resp = resp + ' qop=\"' + self.qop + '\",'
		if len(self.params) > 0:
			for i in self.params:
				resp = resp + ' ' + i + ','
		return resp[:len(resp)-1] + '\r\n'

	def verify(self):
		raise SCNotImplemented("WWWAuthenticate", "verify", "not implemented")
