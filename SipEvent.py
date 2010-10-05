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
class SipEvent:
	"""Class instances stores all informations and content of a SIP event."""

	def __init__(self):
		self.srcAddress = None
		self.dstAddress = None
		self.received = False
		self.time = None
		self.headers = []
		self.body = []
		self.rawEvent = None

	def __str__(self):
		return '[srcAddress:\'' + str(self.srcAddress) + '\', ' \
				+ 'dstAddress:\'' + str(self.dstAddress) + '\', ' \
				+ 'received:\'' + str(self.received) + '\', ' \
				+ 'time:\'' + str(self.time) + '\', ' \
				+ 'headers:\'' + str(self.headers) + '\', ' \
				+ 'body:\'' + str(self.body) + '\' ' \
				+ 'rawEvent:\'' + str(self.rawEvent) + '\']'
