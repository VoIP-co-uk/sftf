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
# $Id: NetworkEventHandler.py,v 1.23 2004/05/03 21:27:02 lando Exp $
#
from EventHandler import EventHandler
import Log, Config, socket, select, copy
from SCException import SCException, SCNotImplemented
import SipEvent as SE
import time
import re

class NetworkEventHandler (EventHandler):
	"""This class handles all SIP events which are going and comming over
	network connections.
	"""

	NEH_NO_SOCK = 0
	NEH_BOUND = 1
	NEH_LISTEN = 2
	NEH_CONNECTED = 3
	NEH_HALF_CLOSED = 4
	NEH_CLOSED = 5

	def __init__(self, transp=None, host=None, port=None, addResource=True, createSock=True):
		EventHandler.__init__(self)
		self.sock = None
		self.transp = None
		self.ip = None
		self.port = None
		self.remoteip = None
		self.remoteport = None
		self.timeout = None
		self.state = NetworkEventHandler.NEH_NO_SOCK
		self.pkgsize = Config.MAX_PKG_SIZE
		self.data = None
		self.old_data = None
		if transp is None:
			transp = Config.DEFAULT_NETWORK_TRANSPORT
		if (transp.lower() == "udp" or transp.lower() == "tcp"):
			self.setTransport(transp)
		else:
			raise SCException("NetworkEventHandler", "__init__", "unsupported transport type")
		if host is None:
			host = Config.LOCAL_IP
		if port is None:
			port = int(Config.LOCAL_PORT)
		if host.startswith("["):
			host = host[1:]
		if host.endswith("]"):
			host = host[:len(host)-1]
		self.localip = host
		self.localport = port
		# Because we can not return another NEH instance if a new instance for
		# the same triplet (transport, ip, port) was requested, we simply
		# close the existing NEH and the create a new one
		key = str(getTransportNumber(transp)) + str(host) + str(port) + "00"
		if addResource and Config.resources.has_key('NEH') and Config.resources['NEH'].has_key(key):
			Log.logDebug("NetworkEventHandler.init(): closing NEH which uses the same address (key '" + key + "') to prevent bind error", 3)
			Config.resources['NEH'][key].close()
		if createSock:
			self.createSock(transp, host, port)
		if addResource:
			Config.resources['NEH'][key] = self

	def __del__(self):
		if self.sock is not None:
			self.sock.close()

	def __str__(self):
		return '[sock:\'' + str(self.sock) + '\', ' \
				+ 'transp:\'' + str(self.transp) + '\', ' \
				+ 'ip:\'' + str(self.ip) + '\', ' \
				+ 'port:\'' + str(self.port) + '\', ' \
				+ 'remoteip:\'' + str(self.remoteip) + '\', ' \
				+ 'remoteport:\'' + str(self.remoteport) + '\', ' \
				+ 'timeout:\'' + str(self.timeout) + '\', ' \
				+ 'state:\'' + str(self.state) + '\', ' \
				+ 'pkgsize:\'' + str(self.pkgsize) + '\', ' \
				+ 'data:\'' + str(self.data) + '\' ' \
				+ 'old_data:\'' + str(self.old_data) + '\']'

	def copy(self, new=None, sock=None):
		if new is None:
			new = NetworkEventHandler(addResource=False, createSock=False)
		new.transp = copy.copy(self.transp)
		new.ip = copy.copy(self.ip)
		new.port = copy.copy(self.port)
		new.remoteip = copy.copy(self.remoteip)
		new.remoteport = copy.copy(self.remoteport)
		new.timeout = copy.copy(self.timeout)
		new.state = copy.copy(self.state)
		new.pkgsize = copy.copy(self.pkgsize)
		new.data = copy.copy(self.data)
		new.old_data = copy.copy(self.old_data)
		if sock is not None:
			new.sock = sock
		return new
		

	def getTransport(self):
		"""Returns the transport type as string. Returns None if not set.
		"""
		if self.transp == socket.SOCK_DGRAM:
			return "UDP"
		elif self.transp == socket.SOCK_STREAM:
			return "TCP"
		else:
			return None

	def openSock(self):
		"""Sets the socket in any case into the listen or connected state.
		"""
		if self.state == NetworkEventHandler.NEH_NO_SOCK:
			#raise SCException("NetworkEventHandler", "openSock", "called on non-existing socket")
			self.createSock(self.transp, self.ip, self.port)
		if self.state == NetworkEventHandler.NEH_BOUND:
			self.sock.listen(1)
			self.state = NetworkEventHandler.NEH_LISTEN
		if self.state == NetworkEventHandler.NEH_LISTEN:
			return
		elif self.state == NetworkEventHandler.NEH_CONNECTED:
			return
		elif self.state == NetworkEventHandler.NEH_HALF_CLOSED:
			self.closeSock()
		if (self.state == NetworkEventHandler.NEH_CLOSED) or (self.state == NetworkEventHandler.NEH_NO_SOCK):
			self.createSock(self.transp, self.ip, self.port)
			self.sock.listen(1)
			self.state = NetworkEventHandler.NEH_LISTEN

	def closeSock(self):
		"""Closes the socket.
		"""
		if (self.sock is not None) and (self.state != NetworkEventHandler.NEH_CLOSED):
			self.sock.close()
			self.sock = None
			self.state = NetworkEventHandler.NEH_NO_SOCK

	def close(self):
		"""An alias for closeSock().
		"""
		self.closeSock()

	def setTransport(self, _transp):
		"""Sets the transport of the instance if it is not allready set.
		"""
		if (_transp == socket.SOCK_DGRAM) or (_transp == socket.SOCK_STREAM):
			return
		elif hasattr(_transp, "lower") and (_transp.lower() == "udp"):
			self.transp = socket.SOCK_DGRAM
		elif hasattr(_transp, "lower") and (_transp.lower() == "tcp"):
			self.transp = socket.SOCK_STREAM
		else:
			raise SCNotImplemented("NetworkEvent", "createSock", "unsupported transport")

	def createSock(self, _transp, _ip, _port):
		"""Creates and binds a socket and sets the variables of the instance.
		"""
		if (_transp != socket.SOCK_DGRAM) and (_transp != socket.SOCK_STREAM):
			self.setTransport(_transp)
		self.sock = socket.socket(Config.socket_type, self.transp)
		try:
			if Config.ipv6:
				#FIXME: no clue what flowinfo and scopeid are good for
				self.sock.bind((_ip, _port, 0, 1))
			else:
				self.sock.bind((_ip, _port))
		except socket.error, inst:
			Log.logDebug("NetworkEventHandler.createSock(): failed to bind " + str(_transp) + " socket to " + str(_ip) + ":" + str(_port), 1)
			raise inst
		self.state = NetworkEventHandler.NEH_BOUND
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sn = self.sock.getsockname()
		self.ip = sn[0]
		perc = self.ip.find("%")
		if (perc != -1):
			self.ip = self.ip[:perc]
		col = self.ip.find(":")
		if (col != -1):
			if not self.ip.startswith("["):
				self.ip = "[" + self.ip
			if not self.ip.endswith("]"):
				self.ip = self.ip + "]"
		self.port = sn[1]

	def setReadTimeout(self, _timeout):
		"""Sets the timeout value which will be used while reading from this
		instance.
		"""
		self.timeout = float(_timeout)

	def seperateData(self, _event):
		"""Tries to sperate the received data into headers and body.
		Returns True on success, False otherwise.
		"""
		sep = 0
		ret = False
		if self.old_data is not None:
			self.data = self.old_data + self.data
			self.old_data = None
		lines = self.data.splitlines(True)
		# seperate headers and body
		try:
			sep = lines.index("\r\n")
		except ValueError:
			Log.logDebug("NEL.seperateData(): body seperator \\r\\n not found", 4)
			try:
				sep = lines.index("\n")
			except ValueError:
				Log.logDebug("NEL.seperateData(): no body seperator found", 2)
		if (sep > 0):
			hl = lines[:sep]
			if self.transp == socket.SOCK_DGRAM:
				_event.body = lines[sep+1:]
			elif self.transp == socket.SOCK_STREAM:
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
						_event.body = tail[:length].splitlines(True)
						self.old_data = tail[length:]
					else:
						_event.body = lines[sep+1:]
				else:
					_event.body = lines[sep+1:]
			else:
				raise SCNotImplemented("NetworkEventHandler", "readEvent", "unsupported transport")
			# remove line folding in headers
			lines_n = range(0, len(hl))
			lines_n.reverse()
			for i in lines_n:
				if (hl[i].startswith(' ') or hl[i].startswith('\t')):
					hl[i-1] = hl[i-1] + hl[i]
					hl[i:i+1] = []
			_event.headers = hl
			ret = True
		else:
			_event.headers = lines
		return ret

	def readEvent(self):
		"""Reads from the network socket of the instance and returns
		a SIP event or None.
		"""
		if (self.transp == socket.SOCK_DGRAM):
			Log.logDebug("Listening for incoming UDP message on " + str(self.ip) + ":" + str(self.port) + "...", 1)
			event = SE.SipEvent()
			dstAddr = self.sock.getsockname()
			event.dstAddress = (dstAddr[0], dstAddr[1], self.transp)
			if self.timeout is None:
				s_in, s_out, s_exc = select.select([self.sock], [], [])
			else:
				s_in, s_out, s_exc = select.select([self.sock], [], [], self.timeout)
			event.time = time.time()
			if len(s_in) > 0:
				try:
					self.data, srcAddr = s_in[0].recvfrom(self.pkgsize)
				except socket.error, inst:
					Log.logDebug("NetworkEventHandler.readEvent(): failed to read from " + str(self.transp) + ":" + str(self.ip) + ":" + str(self.port) + ": " + str(inst), 1)
					raise inst
			else:
				#Log.logTest("WARNING: network timeout after " + str(self.timeout) + " seconds")
				Log.logDebug("NetworkEventHandler.readEvent(): WARNING: timeout after " + str(self.timeout) + " seconds", 1)
				return None
			event.srcAddress = (srcAddr[0], srcAddr[1], self.transp)
			event.received = True
			self.seperateData(event)
			if Config.LOG_NETWORK_PACKETS:
				Log.logDebug("received:\n" + str(self.data), Config.LOG_NETWORK_PACKETS_LEVEL)
			event.rawEvent = self.copy()
			return event
		elif (self.transp == socket.SOCK_STREAM):
			Log.logDebug("Listening for incoming TCP message on " + str(self.ip) + ":" + str(self.port) + "...", 1)
			if self.state >= NetworkEventHandler.NEH_HALF_CLOSED:
				Log.logDebug("NetworkEventHandler.readEvent(): called on at least half closed socket", 1)
				return None
			event = SE.SipEvent()
			self.openSock()
			dstAddr = self.sock.getsockname()
			event.dstAddress = (dstAddr[0], dstAddr[1], self.transp)
			#if not (self.state == NetworkEventHandler.NEH_LISTEN or self.state == NetworkEventHandler.NEH_CONNECTED):
			#	self.sock.listen(1)
			#	self.state = NetworkEventHandler.NEH_LISTEN
			if self.timeout is None:
				s_in, s_out, s_exc = select.select([self.sock], [], [])
			else:
				s_in, s_out, s_exc = select.select([self.sock], [], [], self.timeout)
			event.time = time.time()
			if len(s_in) > 0:
				if self.state == NetworkEventHandler.NEH_LISTEN:
					#FIXME: what do we get for an allready connected sock here?
					con_sock, srcAddr = s_in[0].accept()
					if not hasattr(Config, "resources"):
						self.sock.close()
					else:
						new_neh = self.copy(sock=self.sock)
						key = str(getTransportNumber(new_neh.transp)) + str(new_neh.ip) + str(new_neh.port) + "00"
						Config.resources['NEH'][key] = new_neh

					self.sock = con_sock
					self.state = NetworkEventHandler.NEH_CONNECTED
					#FIXME: this address can probably also contains IPv6 
					# arctefacts. maybe we need a ip_str_fix function
					self.remoteip = srcAddr[0]
					self.remoteport = srcAddr[1]
					if hasattr(Config, "resources"):
						key = str(getTransportNumber(self.transp)) + str(self.ip) + str(self.port) + str(self.remoteip) + str(self.remoteport)
						Config.resources['NEH'][key] = self
				elif self.state == NetworkEventHandler.NEH_CONNECTED:
					srcAddr = self.sock.getpeername()
				self.data = self.sock.recv(self.pkgsize)
			else:
				#FIXME it is possible that old_data only contains a part
				# of a request and we had to wait for the rest. But i guess
				# we cant do much about that
				if self.old_data is not None:
					Log.logDebug("NetworkEventHandler.readEvent(): using old data from the stream", 5)
					self.data = self.old_data
					self.old_data = None
					srcAddr = self.sock.getpeername()
				else:
					Log.logTest("WARNING: timeout after " + str(self.timeout) + " seconds")
					Log.logDebug("NetworkEventHandler.readEvent(): WARNING: timeout after " + str(self.timeout) + " seconds", 1)
					return None
			if (len(s_in) > 0) and (len(self.data) == 0):
				Log.logDebug("NetworkEventHandler.readEvent(): WARNING: connection half closed by remote side", 3)
				self.state = NetworkEventHandler.NEH_HALF_CLOSED
				return None
			event.srcAddress = (srcAddr[0], srcAddr[1], self.transp)
			event.received = True
			if self.seperateData(event):
				if Config.LOG_NETWORK_PACKETS:
					Log.logDebug("received:\n" + str(self.data), Config.LOG_NETWORK_PACKETS_LEVEL)
				event.rawEvent = self.copy()
				return event
			else:
				#FIXME a loop to read more data?!
				pass
		else:
			raise SCNotImplemented("NetworkEventHandler", "readEvent", "unsupported transport")

	def genDataString(self, event):
		"""Joins the data of a SIP event to a network writeable string.
		"""
		ret = ""
		ret = ret.join(event.headers)
		ret = ret + "\r\n"
		bod = ""
		bod = bod.join(event.body)
		ret = ret + bod
		retlen = len(ret)
		return ret, retlen

	def writeEvent(self, event):
		"""Writes the given SIP event through the socket to the destination
		given in the SIP event. Returns True is everything was written 
		successfull, False otherwise.
		"""
		if (self.sock is None):
			if (self.transp is None):
				raise SCException("NetworkEventHandler", "writeEvent", "no socket and transport given")
			else:
				self.createSock(self.transp, Config.LOCAL_IP, Config.LOCAL_PORT)
		else:
			#SOL_SOCKET = getattr(socket, "SOL_SOCKET")
			#SO_TYPE = getattr(socket, "SO_TYPE")
			self.transp = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
			sn = self.sock.getsockname()
			self.ip = sn[0]
			perc = self.ip.find("%")
			if (perc != -1):
				self.ip = self.ip[:perc]
			col = self.ip.find(":")
			if (col != -1):
				if not self.ip.startswith("["):
					self.ip = "[" + self.ip
				if not self.ip.endswith("]"):
					self.ip = self.ip + "]"
			self.port = sn[1]
		# to prevent conversion at other places
		if isinstance(event.srcAddress[2], str):
			if event.srcAddress[2].lower() == "udp":
				event.srcAddress = (event.srcAddress[0], event.srcAddress[1], socket.SOCK_DGRAM)
			elif event.srcAddress[2].lower() == "tcp":
				event.srcAddress = (event.srcAddress[0], event.srcAddress[1], socket.SOCK_STREAM)
		if (event.srcAddress[0] != "file") and (event.srcAddress[2] != self.transp):
			raise SCException("NetworkEventHandler", "writeEvent", "event transport != socket type")
		self.data, bytes = self.genDataString(event)
		if ((self.ip is None) and (event.dstAddress is None)):
			raise SCException("NetworkEventHandler", "writeEvent", "missing destination")
		elif (self.ip is None and (event.srcAddress is not None)):
			self.ip = event.srcAddress[0]
			self.port = event.srcAddress[1]
		if Config.ipv6:
			dstip = event.dstAddress[0]
			if dstip.startswith("["):
				dstip = dstip[1:]
			if dstip.endswith("]"):
				dstip = dstip[:len(dstip)-1]
			#FIXME no clue about flowinfo and scopeid
			dstAddr = (dstip, event.dstAddress[1], 0, 1)
		else:
			dstAddr = (event.dstAddress[0], event.dstAddress[1])
		if (self.transp == socket.SOCK_DGRAM):
			Log.logDebug("Sending UDP message from " + str(self.ip) + ":" + str(self.port) + " to " + str(dstAddr[0]) + ":" + str(dstAddr[1]) + " ...", 1)
			bytessent = self.sock.sendto(self.data, dstAddr)
		elif (self.transp == socket.SOCK_STREAM):
			if self.state != NetworkEventHandler.NEH_CONNECTED:
				self.sock.connect(dstAddr)
				self.state = NetworkEventHandler.NEH_CONNECTED
				self.remoteip = dstAddr[0]
				self.remoteport = dstAddr[1]
			Log.logDebug("Sending TCP message from " + str(self.ip) + ":" + str(self.port) + " to " + str(self.remoteip) + ":" + str(self.remoteport) + " ...", 1)
			bytessent = self.sock.send(self.data)
		else:
			raise SCNotImplemented("NetworkEventHandler", "writeEvent", "unsupport transport")
		event.time = time.time()
		event.rawEvent = self.copy()
		Log.logDebug("message length = " + str(bytes) + " bytes, sent " + str(bytessent) + " bytes", 4)
		if (bytessent == bytes):
			if Config.LOG_NETWORK_PACKETS:
				Log.logDebug("sent:\n" + str(self.data), Config.LOG_NETWORK_PACKETS_LEVEL)
			return True
		else:
			# FIXME retry?
			return False


def createMediaSockets(ip=None, port=None):
	"""Creates a random UDP socket (for media) and returns the socket,
	the IP and the port of this socket.
	"""
	if ip is None:
		ip = Config.LOCAL_IP
	if port is None:
		port = 0
		port2 = 0
	else:
		port2 = port + 1
	success = False
	while not success:
		sock = socket.socket(Config.socket_type, socket.SOCK_DGRAM)
		sock2 = socket.socket(Config.socket_type, socket.SOCK_DGRAM)
		try:
			print "trying to bind sock"
			sock.bind((ip, port))
			if port2 == 0:
				ret_ip, port = sock.getsockname()
				port2 = port + 1
			try:
				print str(port) + " trying to bind sock2 to " + str(port2)
				sock2.bind((ip, port2))
				if (port % 2 == 0):
					print "sock is even"
					ret_pair = (sock, sock2)
					success = True
				else:
					print "sock is not even"
					sock = socket.socket(Config.socket_type, socket.SOCK_DGRAM)
					port = port + 2
					try:
						print "trying to bind sock to " + str(port)
						sock.bind((ip, port))
						ret_pair = (sock2, sock)
						port = port2
						success = True
					except socket.error:
						print "re-binding of sock failed"
						sock2.close()
						port = port2 + 3
						port2 = port + 1
			except socket.error:
				print "binding of sock2 failed"
				sock.close()
				port = port + 2
				port2 = port + 1
		except socket.error:
			print "binding of sock failed"
			port = port + 1
	return ret_pair, ret_ip, port

def compareHostNames(name1, name2):
	"""Compares the both given hostnames (DNS names or IPs) and
	returns True if they are equal (except DNS aliases), False otherwise.
	"""
	#FIXME IPs of aliases could be detected as not equal
	# the result lists should be compared each one by one
	if (name1 is None) or (name2 is None):
		return False
	try:
		list1 = socket.getaddrinfo(name1, 0, socket.AF_UNSPEC)
		ip1 = list1[0][4][0]
	except socket.gaierror:
		ip1 = name1
	try:
		list2 = socket.getaddrinfo(name2, 0, socket.AF_UNSPEC)
		ip2 = list2[0][4][0]
	except socket.gaierror:
		ip2 = name2
	if ip1 == ip2:
		return True
	else:
		return False

def getHostNameIP():
	"""Tries to determine the hostname and the IP of the local host.
	Returns name and IP if successfull, otherwise both will be None.
	"""
	hn, al, ip = socket.gethostbyaddr(socket.gethostname())
	if len(ip) > 1:
		print "Multiple IPs per interface detected ('" + str(ip) + "').\r\nPlease specify the desired IP in Config.py"
		return None, None
	else:
		hn_new = socket.getfqdn(hn)
		num = hn_new.count(".")
		if num < 2:
			print "Hostname detection failed ('" + str(hn_new) + "' does not contain two dots).\r\nPlease specify the desired full qualified domain hostname in Config.py"
			return None, None
		else:
			return hn_new, ip[0]

def getFQDN(ip):
	"""Returns the FQDN for the given IP if resolvable, otherwise None.
	"""
	try:
		hn, al, ip = socket.gethostbyaddr(ip)
	except socket.herror, param:
		if param[0] == 1:
			return None
		else:
			raise param
	hn_new = socket.getfqdn(hn)
	num = hn_new.count(".")
	if num < 2:
		return None
	else:
		return hn_new

def getTransportNumber(_transp):
	if _transp.lower() == "udp":
		return socket.SOCK_DGRAM
	elif _transp.lower() == "tcp":
		return socket.SOCK_STREAM
	else:
		raise SCException("NetworkEventHandler", "getTransportNumber", "unsupported transport '"+str(_transp)+"'")

def checkIPv6Support():
	pos = Config.LOCAL_IP.find(":")
	if (pos != -1):
		if hasattr(socket, "has_ipv6"):
			Config.ipv6 = socket.has_ipv6
			if Config.ipv6:
				Config.socket_type = socket.AF_INET6
				if (str(Config.LOCAL_IP).find(":") != -1) and not str(Config.LOCAL_IP).startswith("["):
					Config.LOCAL_IP = "[" + Config.LOCAL_IP + "]"
				if (str(Config.TEST_HOST).find(":") != -1) and not str(Config.TEST_HOST).startswith("["):
					Config.TEST_HOST = "[" + Config.TEST_HOST + "]"
		else:
			Config.ipv6 = True
			Config.socket_type = socket.AF_INET6
	else:
		Config.ipv6 = False
		Config.socket_type = socket.AF_INET
