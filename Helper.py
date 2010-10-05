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
# $Id: Helper.py,v 1.15 2004/03/19 18:37:25 lando Exp $
#
import sys, imp, time, copy
import Log, Config

def timeDiff(time1, time2):
	"""Returns the difference between the two given datetime or float
	instances as float with seconds before the comma.
	"""
	if time1 > time2:
		tdelta = time1 - time2
	else:
		tdelta = time2 - time1
	if isinstance(tdelta, float):
		return tdelta
	sec = float(tdelta.seconds)
	msec = float("0." + str(tdelta.microseconds))
	return sec + msec

def eventTimeDiff(event1, event2):
	"""Returns the time difference between the two given SIP events as float.
	"""
	return timeDiff(event1.time, event2.time)

def createDummyBody():
	"""Returns a string, which contains an SDP description where the
	remote side will be on-hold.
	"""
	return ['v=0\r\n', \
			'o=' + str(Config.SC_USER_NAME) + ' ' + str(int(time.time())) + ' ' + str(int(time.time())) + ' IN IP4 ' + str(Config.LOCAL_IP) + '\r\n', \
			's=Dummy on hold SDP\r\n', \
			'c=IN IP4 0.0.0.0\r\n', \
			'm=audio 65534 RTP/AVP 0\r\n', \
			'a=rtpmap:0 PCMU/8000\r\n', \
			'a=recvonly\r\n']

def calculateBodyLength(body):
	"""Returns the length of the given body as integer.
	"""
	body_str = ""
	for i in body:
		body_str = body_str + i
	return len(body_str)

# This function maps the short notation of some
# header fields to the name of the supporting module.
# Notes:
#  - it also removes the '-' from the header field names,
#    because they seem to be not allowed in module names.
#  - we map from lower case to be case independent, but
#    the module names are kept as similar as possible (we
#    only remove the -, see above)

def getMappedHFH(hfh):
	"""This function converts the given header field name from short
	notation into full name, removes the - character and capitalizes
	the name.
	"""
	hfh_dict = {'I': 'Callid', \
				'M': 'Contact', \
				'E': 'Contentencoding', \
				'L': 'Contentlength', \
				'C': 'Contenttype', \
				'F': 'From', \
				'R': 'Referto', \
				'S': 'Subject', \
				'K': 'Supported', \
				'T': 'To', \
				'V': 'Via'}
	hfhl = hfh.replace("-", "").capitalize()
	if hfh_dict.has_key(hfhl):
		return hfh_dict[hfh.replace("-", "").capitalize()]
	else:
		return hfhl

def getRevMappedHFH(hfh):
	"""This function returns the reverse mapping of what the getMappedHFH
	function returned. Which means the mapped name (without -, capitalized
	and long notation) to the header name exactly as written in BNF of RFC3261.
	"""
	hfh_dict = {'Accept': 'Accept', \
				'Acceptencoding': 'Accept-Encoding', \
				'Acceptlanguage': 'Accept-Language', \
				'Alertinfo': 'Alert-Info', \
				'Allow': 'Allow', \
				'Authorization': 'Authorization', \
				'Authenticationinfo': 'Authentication-Info', \
				'Callid': 'Call-ID', \
				'I': 'Call-ID', \
				'Callinfo': 'Call-Info', \
				'Contact': 'Contact', \
				'M': 'Contact', \
				'Contentdisposition': 'Content-Disposition', \
				'Contentencoding': 'Content-Encoding', \
				'E': 'Content-Encoding', \
				'Contentlanguage': 'Content-Language', \
				'Contentlength': 'Content-Length', \
				'L': 'Content-Length', \
				'Contenttype': 'Content-Type', \
				'C': 'Content-Type', \
				'Cseq': 'CSeq', \
				'Date': 'Date', \
				'Errorinfo': 'Error-Info', \
				'Expires': 'Expires', \
				'From': 'From', \
				'F': 'From', \
				'Inreplyto': 'In-Reply-To', \
				'Maxforwards': 'Max-Forwards', \
				'Mimeversion': 'MIME-Version', \
				'Minexpires': 'MinExpires', \
				'Organization': 'Organization', \
				'Priority': 'Priority', \
				'Proxyauthenticate': 'Proxy-Authenticate', \
				'Proxyauthorization': 'Proxy-Authorization', \
				'Proxyrequire': 'Proxy-Require', \
				'Recordroute': 'Record-Route', \
				'Referto': 'Refer-To', \
				'Replyto': 'Reply-To', \
				'Require': 'Require', \
				'Retryafter': 'Retry-After', \
				'Route': 'Route', \
				'Server': 'Server', \
				'Subject': 'Subject', \
				'S': 'Subject', \
				'Supported': 'Supported', \
				'K': 'Supported', \
				'Timestamp': 'Timestamp', \
				'To': 'To', \
				'T': 'To', \
				'Unsupported': 'Unsupported', \
				'Useragent': 'User-Agent', \
				'Via': 'Via', \
				'V': 'Via', \
				'Warning': 'Warning', \
				'Wwwauthenticate': 'WWW-Authenticate'}
	hfhl = hfh.replace("-", "").capitalize()
	if hfh_dict.has_key(hfhl):
		return hfh_dict[hfh.replace("-", "").capitalize()]
	else:
		return None

multiple_headers = ['Accept', 'Acceptencoding', 'Acceptlanguage', \
	'Alertinfo', 'Allow', 'Authenticationinfo','Callinfo','Contact', \
	'Contentencoding', 'Contentlanguage', 'Errorinfo', 'Inreplyto', \
	'Proxyrequire', 'Recordroute', 'Require', 'Route', 'Supported', \
	'Unsupported', 'Via', 'Warning']

rfc_bfn_headers = ['Accept', 'Accept-Encoding', 'Accept-Language', \
	'Alert-Info', 'Allow', 'Authorization', 'Authentication-Info', \
	'Call-ID', 'Call-Info', 'Contact', 'Content-Disposition', \
	'Content-Encoding', 'Content-Language', 'Content-Length', 'Content-Type', \
	'CSeq', 'Date', 'Error-Info', 'Expires', 'From', 'In-Reply-To', \
	'Max-Forwards', 'MIME-Version', 'MinExpires', 'Organization', 'Priority', \
	'Proxy-Authenticate', 'Proxy-Authorization', 'Proxy-Require', \
	'Record-Route', 'Reply-To', 'Require', 'Retry-After', 'Route', 'Server', \
	'Subject', 'Supported', 'Timestamp', 'To', 'Unsupported', 'User-Agent', \
	'Via', 'Warning', 'WWW-Authenticate']

rfc_headers = ['accept', 'accept-encoding', 'accept-language', \
	'alert-info', 'allow', 'authorization', 'authentication-info', \
	'call-id', 'call-info', 'contact', 'content-disposition', \
	'content-encoding', 'content-language', 'content-length', 'content-type', \
	'cseq', 'date', 'error-info', 'expires', 'from', 'in-reply-to', \
	'max-forwards', 'mime-version', 'minexpires', 'organization', 'priority', \
	'proxy-authenticate', 'proxy-authorization', 'proxy-require', \
	'record-route', 'reply-to', 'require', 'retry-after', 'route', 'server', \
	'subject', 'supported', 'timestamp', 'to', 'unsupported', 'user-agent', \
	'via', 'warning', 'www-authenticate']

def get_rpl_hfh_dict(code):
	"""Returns a sequence of the required header field names for a given reply
	code number.
	"""
	man_rpl_hfh = ['Via', 'From', 'To', 'Call-ID', 'CSeq']
	rpl_hfh_dict = { 100: man_rpl_hfh, \
					200: man_rpl_hfh, \
					300: man_rpl_hfh, \
					400: man_rpl_hfh, \
					500: man_rpl_hfh, \
					600: man_rpl_hfh}
	if rpl_hfh_dict.has_key(code):
		return rpl_hfh_dict[code]
	else:
		return None

def get_req_hfh_dict(method):
	"""Returns a sequence of the required header filed names for the given
	SIP method. Only RFC3261 are known yet.
	"""
	man_req_hfh = ['Call-ID', 'CSeq', 'Content-Length', 'Max-Forwards', 'From',\
					'To', 'Via']
	req_hfh_dict = {'invite': ['Call-ID', 'CSeq', 'Contact', 'Content-Length',\
								'From', 'Max-Forwards', 'Supported', 'To',\
								'Via', ], \
					'ack': man_req_hfh, \
					'bye': man_req_hfh, \
					'register': man_req_hfh, \
					'cancel': man_req_hfh, \
					'options': ['Accept', 'Call-ID' , 'Content-Length', 'CSeq',\
							'From', 'Max-Forwards', 'To', 'Via'], \
					'refer': ['Allow', 'Call-ID', 'Contact', 'CSeq', 'From', \
							'Max-Forwards', 'To', 'Via']}
	if req_hfh_dict.has_key(method.lower()):
		return req_hfh_dict[method.lower()]
	else:
		return None

def importModule(name):
	"needed because of a bug in python when dynamically loading a python module"

	if (len(name) == 0):
		return None
	if not name[0].isalpha():
		return None

	# Fast path: see if the module has already been imported.
	if sys.modules.has_key(name):
		return sys.modules[name]

	# If any of the following calls raises an exception,
	# there's a problem we can't handle

	# See if it's a built-in module.
	m = imp.init_builtin(name)
	if m:
		return m

	# See if it's a frozen module.
	m = imp.init_frozen(name)
	if m:
		return m

	try:
		# Search the default path (i.e. sys.path).
		fp, pathname, stuff = imp.find_module(name)
	except ImportError, param:
		Log.logDebug("Helper.importModule(): ImportError: " + str(param), 2)
		Log.logDebug("Helper.importModule(): failed to find module " + str(name), 1)
		return None

	# finally try to load the module
	try:
		m = imp.load_module(name, fp, pathname, stuff)
	finally:
		# Since we may exit via an exception, close fp explicitly.
		if fp:
			fp.close()
	# to please pychecker
	if m:
		return m
	else:
		return None

def createClassInstance(name):
	"""Imports the required module and returns a new instance of the request
	class name. Returns None in case of an error.
	"""
	mod = importModule(name)
	if mod:
		try:
			cs = getattr(mod, name)
		except AttributeError, param:
			Log.logDebug("Helper.createClassInstance(): AttributeError: " + str(param), 2)
			Log.logDebug("Helper.createClassInstance(): module '" + name + "' misses class with the same name!", 1)
			return None
		ci = cs()
		return ci
	return None

def usrlocAddContact(aor, co):
	if aor.lower().startswith("sip:"):
		aor = aor[4:]
	elif aor.lower().startwith("sips:"):
		aor = aor[5:]
	now = time.time()
	cco = copy.deepcopy(co)
	co = cco
	while cco is not None:
		if cco.expires is None:
			cco.expires = int(now + int(Config.DEFAULT_EXPIRES))
		else:
			cco.expires = int(now + int(cco.expires))
		cco = cco.next
	if not hasattr(Config, "usrloc"):
		Log.logDebug("Helper.usrlocAddContact(): initiating usrloc dict", 5)
		Config.usrloc = {}
	Log.logDebug("Helper.usrlocAddContact(): adding Contact(s) for AOR '" + str(aor) + "'", 4)
	if Config.usrloc.has_key(aor):
		uco = Config.usrloc[aor]
		ucop = None
		hit = False
		while uco is not None:
			if co.uri == uco.uri:
				Log.logDebug("Helper.usrlocAddContact(): replacing existing Contact in AOR list", 4)
				if ucop is not None:
					ucop.next = co
				co.next = uco.next
				hit = True
				break
			ucop = uco
			uco = uco.next
		if not hit:
			Log.logDebug("Helper.usrlocAddContact(): appending Contact to the AOR list", 4)
			if ucop is not None:
				ucop.next = co
			else:
				raise Exception("Helper.usrlocAddContact(): usrloc previous not set")
	else:
		Log.logDebug("Helper.usrlocAddContact(): adding Contact(s) for new AOR", 4)
		Config.usrloc[aor] = co

def usrlocGetContacts(aor):
	if aor.lower().startswith("sip:"):
		aor = aor[4:]
	elif aor.lower().startwith("sips:"):
		aor = aor[5:]
	if hasattr(Config, "usrloc") and Config.usrloc.has_key(aor):
		co = copy.deepcopy(Config.usrloc[aor])
		cco = co
		now = time.time()
		while cco is not None:
			#FIXME allready expired Contact will be returned 
			#      with negative expires value
			cco.expires = int(int(cco.expires) - now)
			cco = cco.next
		return co
	else:
		return None
