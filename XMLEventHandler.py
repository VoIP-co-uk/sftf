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
# $Id: FileEventHandler.py,v 1.7 2004/03/19 18:37:25 lando Exp $
#
from EventHandler import EventHandler
import Log, Config
import SCException

class XMLEventHandler (EventHandler):
	"""This class implements the EventHandler class for files. It can read in
	SIP messages from files and can write SIP event to a file.
	"""

	def __init__(self, _filename=None, addResource=True):
		"""If a filename is given as parameter that file will be opened
		for reading. If the second parameter is True single line-feeds will 
		be replaced	by carriage-return line-feed while reading in and writing
		to a file.
		"""
		EventHandler.__init__(self)
		self.filename = None
		self.fileobj = None
		self.framenr = 0
		if _filename is not None:
			self.filename = _filename
			self.openFile(mode="w")
			if addResource:
				if self.filename.endswith('.xml'):
					fn = self.filename[:len(self.filename)-4]
				else:
					fn = self.filename
				Config.resources['XMLEH'][fn] = self
	
	def __del__(self):
		if self.fileobj is not None:
			self.fileobj.close()

	def __str__(self):
		return '[filename:\'' + str(self.filename) + '\', ' \
				'fileobj:\'' + str(self.fileobj) + '\', ' \
				'framenr:\'' + str(self.framenr) + '\']'


	def openFile(self, filename=None, mode=None):
		"""Trys to open the file in the desired mode.
		"""
		if (filename is not None) and (filename != self.filename) and (self.fileobj is not None):
			self.close()
			self.filename = filename
		if mode is None:
			mode = "w"
		Log.logDebug("trying to open:\'" + str(self.filename) + '\', mode:\'' + str(mode) + '\'' , 4)
		self.fileobj = file(self.filename, mode)
		Log.logDebug("opened successfully", 4)
		self.fileobj.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n")
		self.fileobj.write("<sipTrace>\n")
		Log.logDebug("wrote XML header successfully", 4)

	def close(self):
		"""Close the file object if one is still open.
		"""
		if (not self.fileobj is None):
			self.fileobj.write("</sipTrace>\n")
			self.framenr = 0
			self.fileobj.close()
			self.fileobj = None


	def writeMessage(self, message):
		"""Writes the given SIP event to the file.
		The destination address will be 'file' + filename. The source address
		will be None.
		"""
		if self.fileobj.closed:
			if self.filename is not None:
				self.openFile(mode="w")
			else:
				raise SCException("XMLEventHandler", "writeEvent", "missing filename")
		elif self.fileobj.mode != "w":
			self.openFile(mode="w")

		self.fileobj.write("\t<branchNode>\n")
		self.fileobj.write("\t\t<branchIdSet>\n")
		if message.hasParsedHeaderField("Via"):
			via = message.getParsedHeaderValue("Via")
			while via is not None:
				if via.branch is not None:
					self.fileobj.write("\t\t\t<branchId>" + str(via.branch) + "</branchId>\n")
				via = via.next
		self.fileobj.write("\t\t</branchIdSet>\n")

		if message.event.time is not None:
			self.fileobj.write("\t\t<time>" + str(message.event.time) + "</time>\n")

		if len(message.event.srcAddress) == 3:
			srcip, srcport, trp = message.event.srcAddress
		else:
			srcip, srcport = message.event.srcAddress
		srcadr = str(srcip) + ":" + str(srcport)
		if len(message.event.dstAddress) == 3:
			dstip, dstport, trp = message.event.dstAddress
		else:
			dstip, dstport = message.event.dstAddress
		dstadr = str(dstip) + ":" + str(dstport)
		self.fileobj.write("\t\t<source>" + str(srcadr) + "</source>\n")
		self.fileobj.write("\t\t<destination>" + str(dstadr) + "</destination>\n")
		self.fileobj.write("\t\t<sourceAddress>" + str(srcadr) + "</sourceAddress>\n")
		self.fileobj.write("\t\t<destinationAddress>" + str(dstadr) + "</destinationAddress>\n")

		tid = ""
		if message.hasParsedHeaderField("CSeq") and message.getParsedHeaderValue("CSeq").number is not None:
			tid += str(message.getParsedHeaderValue("CSeq").number)
		tid += ","
		if message.hasParsedHeaderField("CallID") and message.getParsedHeaderValue("CallID").str is not None:
			tid += str(message.getParsedHeaderValue("CallID").str)
		tid += ","
		if message.hasParsedHeaderField("From") and message.getParsedHeaderValue("From").tag is not None:
			tid += str(message.getParsedHeaderValue("From").tag)
		tid += ","
		if message.hasParsedHeaderField("To") and message.getParsedHeaderValue("To").tag is not None:
			tid += str(message.getParsedHeaderValue("To").tag)
		self.fileobj.write("\t\t<transactionId>" + str(tid) + "</transactionId>\n")

		if message.isRequest:
			self.fileobj.write("\t\t<method>" + str(message.method) + "</method>\n")
		else:
			self.fileobj.write("\t\t<responseCode>" + str(message.code) + "</responseCode>\n")
			self.fileobj.write("\t\t<responseText>" + str(message.reason) + "</responseText>\n")

		self.fileobj.write("\t\t<frameId>" + str(self.framenr) + "</frameId>\n")
		self.framenr += 1

		self.fileobj.write("\t\t<message><![CDATA[")
		self.fileobj.writelines(message.event.headers)
		self.fileobj.write("\r\n")
		if (len(message.event.body) > 0):
			self.fileobj.writelines(message.event.body)
		self.fileobj.write("]]></message>\n")

		self.fileobj.write("\t</branchNode>\n")

	def readEvent(self):
		raise SCException("XMLEventHandler", "readEvent", "reading from XML not implemented yet")
