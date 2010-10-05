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
# $Id: HeaderFieldHandler.py,v 1.7 2004/03/19 18:38:44 lando Exp $
#
from SCException import SCNotImplemented

class HeaderFieldHandler:
	"""This class provides a generic interface to handle any header field
	in a SIP message. The functions of this class have to be implemented by
	any new header field handler, because they can or will be called if
	such a header field is present in SIP message.
	"""

	def __init__(self, value=None):
		"""__init__ should create an instance for the header field with
		empty (None) values. If value is given the parse function should 
		be called with this parameter.
		"""
		if value is not None:
			self.parse(value)

	def __str__(self):
		"""To make debuging easier this function should be implemented."""
		raise SCNotImplemented("HeaderFieldHandler", "__str__", "not implemented")

	def parse(self, value):
		"""This function will be called with the value of the header field
		as parameter. It should try its best to parse the value and fill
		the attributes of this instance. If an unhandlable error occurse
		a HFHException should be raised.
		"""
		raise SCNotImplemented("HeaderFieldHandler", "parse", "not implemented")

	def create(self):
		"""This function will be called to create the value part of the
		header field instance. The function should only return the value part
		with carriage return and line feed, but without the leading header
		field name and the collon.
		"""
		raise SCNotImplemented("HeaderFieldHandler", "create", "not implemented")

	def verify(self):
		"""This function will be called to check if header field is completely
		correct. It should return a list of test results if anything is not
		correct.
		"""
		raise SCNotImplemented("HeaderFieldHandler", "verify", "not implemented")
