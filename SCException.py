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
# $Id: SCException.py,v 1.6 2004/03/19 18:37:25 lando Exp $
#
class SCException(Exception):
	"""Generic internal exception class. Consits out of class name, function
	name and the reason phrase.
	"""

	def __init__(self, cls, funct, reason):
		Exception.__init__(self)
		self.cls = cls
		self.funct = funct
		self.reason = reason

	def __str__(self):
		return str(self.cls) + '.' + str(self.funct) + '(): ' + str(self.reason)

class SCNotImplemented (SCException):
	"""See SCException. Called if implementation is missing."""

	def __init__(self, cls, function, reason):
		SCException.__init__(self, cls, function, reason)

class HFHException(SCException):
	"""See SCException. Called for exceptions during parsing header fields."""

	def __init__(self, cls, function, reason):
		SCException.__init__(self, cls, function, reason)
