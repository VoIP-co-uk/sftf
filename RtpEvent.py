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
# $Id: SipEvent.py,v 1.8 2004/03/19 18:37:25 lando Exp $
#

import SCException
import Log
import re


class RtpEvent:
	"""Class instances stores all informations and content of an RTP event."""
	def __init__(self, type=None):
		self.srcAddress = None
		self.dstAddress = None
		self.received = False
		self.time = None
		self.rawEvent = None
		self.data = None
		if type is not None:
			self.initialiseEvent(type)

	def __str__(self):
		return '[srcAddress:\'' + str(self.srcAddress) + '\', ' \
				+ 'dstAddress:\'' + str(self.dstAddress) + '\', ' \
				+ 'received:\'' + str(self.received) + '\', ' \
				+ 'time:\'' + str(self.time) + '\', ' \
				+ 'rawEvent:\'' + str(self.rawEvent) + '\']'

	def genDataString(self):
		"""Joins the data of an RTP event to a network writeable string.
		"""
		ret = self.data
		retlen = len(ret)
		return ret, retlen

	def parseData(self, streamContext, data):
		""" Identifies and parses an RTP message from the data
		"""
		sep = 0
		ret = False
		if streamContext is not None:
			raise SCException.SCNotImplemented('RtpEvent', 'parseData' 'RTP over stream transport not implemented')
		self.data = data
		return None, True
