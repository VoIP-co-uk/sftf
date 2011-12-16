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
# $Id: Proxyauthorization.py,v 1.2 2004/03/19 18:38:44 lando Exp $
#
from HeaderFieldHandler import HeaderFieldHandler
from SCException import SCNotImplemented
from Authorization import Authorization
import DigestAuthentication as DA

class Proxyauthorization (Authorization, HeaderFieldHandler):

	# __init__ and parse() are inherited from Authorization

	def respondTo(self, challenge, method, username, password):
		self.realm = challenge.realm
		self.nonce = challenge.nonce
		self.algorithm = challenge.algorithm
		self.username = username
		self.ha1 = DA.HA1(self.username, self.realm, password)
		self.ha2 = DA.HA2(method, self.uri)
		self.response = DA.response(self.ha1, self.nonce, self.ha2, self.nc, self.cnonce, self.qop)

	def create(self):
		return Authorization.create(self)
