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
import SipEvent as SE

def fixCRLF(_input):
	pos = _input.find("\n")
	while pos != -1:
		if _input[pos-1] != "\r":
			_input = _input[:pos] + "\r\n" + _input[pos+1:]
			pos = pos+1
		pos = _input.find("\n", pos+1)
	return _input

class FileEventHandler (EventHandler):
	"""This class implements the EventHandler class for files. It can read in
	SIP messages from files and can write SIP event to a file.
	"""

	def __init__(self, _filename=None, _fixLF=True, addResource=True):
		"""If a filename is given as parameter that file will be opened
		for reading. If the second parameter is True single line-feeds will 
		be replaced	by carriage-return line-feed while reading in and writing
		to a file.
		"""
		EventHandler.__init__(self)
		self.filename = None
		self.fileobj = None
		self.fixLF = _fixLF
		if _filename is not None:
			self.filename = _filename
			self.openFile("r")
			if addResource:
				Config.resources['FEH'][self.filename] = self
	
	def __del__(self):
		if self.fileobj is not None:
			self.fileobj.close()

	def __str__(self):
		return '[filename:\'' + str(self.filename) + '\', ' \
				'fileobj:\'' + str(self.fileobj) + '\']'


	def openFile(self, mode=None):
		"""Trys to open the file in the desired mode.
		"""
		if mode is None:
			mode = "r"
		Log.logDebug("trying to open:\'" + str(self.filename) + '\', mode:\'' + str(mode) + '\'' , 4)
		self.fileobj = file(self.filename, mode)
		Log.logDebug("opened successfully", 4)

	def close(self):
		"""Close the file object if one is still open.
		"""
		if (not self.fileobj is None):
			self.fileobj.close()
			self.fileobj = None

	def readFileLine(self):
		"""Reads and returns a single line from the allready opened file.
		"""
		s = self.fileobj.readline()
		if self.fixLF:
			s = fixCRLF(s)
		if (s == "."):
			return ""
		else:
			return s

	def readBlock(self):
		"""Reads and returns a block from the file. A block is either ended
		by a line which only consist of a newline or carriage-return newline 
		combination or it ends when the file end is reached.
		"""
		empty = 0
		block = []
		while (not empty):
			line = self.readFileLine()
			empty = ((line == "\r\n") or (line == "\n") or (line == ""))
			if (not empty):
				if (line.startswith(' ') or line.startswith('\t')):
					block[len(block)-1] = block[len(block)-1] + line
				else:
					block.append(line)
		return block

	def readEvent(self):
		"""Reads a SIP request from the file and returns it as SIP event.
		The source address will be set to 'file' + filename. The destination
		address will be None.
		"""
		if self.fileobj.closed:
			if self.filename is not None:
				self.openFile("r")
			else:
				raise SCException("FileEventHandler", "readEvent", "missing filename")
		event = SE.SipEvent()
		event.srcAddress = ("file", self.fileobj.name, '')
		event.headers = self.readBlock()
		event.body = self.readBlock()
		self.fileobj.close()
		return event

	def readFile(self, filename):
		"""Sets the filename to the given parameter and reads and returns the
		resulting SIP event from this file.
		"""
		if self.fileobj.closed:
			self.filename = filename
			self.openFile("r")
		return self.readEvent()

	def writeEvent(self, event):
		"""Writes the given SIP event to the file.
		The destination address will be 'file' + filename. The source address
		will be None.
		"""
		if self.fileobj.closed:
			if self.filename is not None:
				self.openFile("w")
			else:
				raise SCException("FileEventHandler", "writeEvent", "missing filename")
		elif self.fileobj.mode != "w":
			self.openFile("w")
		event.dstAddress = ("file", self.fileobj.name, '')
		if self.fixLF:
			self.fileobj.writelines(fixCRLF(event.headers))
		else:
			self.fileobj.writelines(event.headers)
		self.fileobj.write("\r\n")
		if (len(event.body) > 0):
			if self.fixLF:
				self.fileobj.writelines(fixCRLF(event.body))
			else:
				self.fileobj.writelines(event.body)
		self.fileobj.close()
