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
# $Id: EventHandler.py,v 1.4 2004/03/19 18:37:25 lando Exp $
#
from SCException import SCNotImplemented

class EventHandler:
	"""An abstract class for SIP event handling classes."""

	def __init__(self):
		pass

	def readEvent(self):
		"""This function will be called to get a SIP event as return value.
		"""
		raise SCNotImplemented("EventHandler", "readEvent", "not implemented")

	def writeEvent(self, event):
		"""This function will be called to write the given SIP event to the
		destination.
		"""
		raise SCNotImplemented("EventHandler", "writeEvent", "not implemented")
