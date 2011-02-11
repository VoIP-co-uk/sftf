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

import Log
import re

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

	def genDataString(self):
		"""Joins the data of a SIP event to a network writeable string.
		"""
		ret = ""
		ret = ret.join(self.headers)
		ret = ret + "\r\n"
		bod = ""
		bod = bod.join(self.body)
		ret = ret + bod
		retlen = len(ret)
		return ret, retlen

	def parseData(self, streamContext, data):
		""" Identifies and parses a SIP message from the data
		    streamContext contains any previously received and unparsed
		    data that may exist in a stream-based transport.  It is None
		    for non-stream based transports.
		    If there is extra data after the message, return it and it
		    will be passed in again as streamContext for interpretation
		    as part of the next message
		"""
		sep = 0
		ret = False
		if streamContext is not None:
			data = streamContext + data
			streamContext = []

		lines = data.splitlines(True)
		# separate headers and body
		try:
			sep = lines.index("\r\n")
		except ValueError:
			Log.logDebug("SipEvent.parseData(): body separator \\r\\n not found", 4)
			try:
				sep = lines.index("\n")
			except ValueError:
				Log.logDebug("SipEvent.parseData(): no body separator found", 2)
		if (sep > 0):
			hl = lines[:sep]
			if streamContext is not None:
				self.body = lines[sep+1:]
			else:
				co = re.compile("^content-length", re.IGNORECASE)
				length = None
				for i in hl:
					match = co.match(i)
					if match is not None:
						length = int(i[15:].replace(":", "").replace("\t", "").strip())
						Log.logDebug("found content length = " + str(length), 5)
				if length is not None:
					tail = ""
					tail = tail.join(lines[sep+1:])
					if len(tail) > length:
						self.body = tail[:length].splitlines(True)
						streamContext = tail[length:]
					else:
						self.body = lines[sep+1:]
				else:
					self.body = lines[sep+1:]
			# remove line folding in headers
			lines_n = range(0, len(hl))
			lines_n.reverse()
			for i in lines_n:
				if (hl[i].startswith(' ') or hl[i].startswith('\t')):
					hl[i-1] = hl[i-1] + hl[i]
					hl[i:i+1] = []
			self.headers = hl
			ret = True
		else:
			self.headers = lines
		return streamContext,ret

