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
# $Id: DigestAuthentication.py,v 1.4 2004/03/19 18:37:25 lando Exp $
#
import md5

def HA1(username, realm, password):
	"""Calculates the hash of the A1 string (HA1) which consists of
	the username, the realm and password as parameters.
	"""
	a1 = username + ':' + realm + ':' + password
	m = md5.md5(a1)
	return m.hexdigest()

def HA2(method, uri):
	"""Caculates the hast of the A2 string (HA2) which requires the
	request method and the uri.
	"""
	a2 = method + ':' + uri
	m = md5.md5(a2)
	return m.hexdigest()

def response(ha1, nonce, ha2, nc=None, cnonce=None, qop=None):
	"""Calculates the complete digest authentication response hash value out
	of the given HA1, nonce value and the HA2. If nonce count, client nonce
	and qop are given, the response qith qop will be returned.
	"""
	if (nc is not None and cnonce is not None and qop is not None):
		resp = ha1 + ':' + nonce + ':' + str(nc) + ':' + cnonce + ':' + qop + ':' + ha2
	else:
		resp = ha1 + ':' + nonce + ':' + ha2
	m = md5.md5(resp)
	return m.hexdigest()
