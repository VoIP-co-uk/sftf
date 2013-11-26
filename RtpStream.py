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
import RtpEvent
from NetworkEventHandler import NetworkEventHandler
from TestCase import TestCase
import re
import struct

G711A_Test = 1
G711U_Test = 2

_payloads = {
	G711A_Test: '\x55'*160,
	G711U_Test: '\xFF'*160
	}


class RtpStream:
	""" Details of a stream of RTP, defined by our local NEH and the remote SDP """
	def __init__(self, tc, sockTuple):
		self.tc = tc
		sockets, ip, rtpPort = sockTuple

		self.neh = NetworkEventHandler('udp', ip, rtpPort, createSock=False, eventType=RtpEvent.RtpEvent)
		self.rtcpNeh = NetworkEventHandler('udp', ip, rtpPort+1, createSock=False, eventType=RtpEvent.RtpEvent)

		self.neh.addSock(sockets[0])
		self.rtcpNeh.addSock(sockets[1])
 
		self.peerSdp = None
		self.srcAddr = (ip, rtpPort, self.neh.transp)
		self.srcRTCP = (ip, rtpPort+1, self.neh.transp)
		self.pt = 8
		self.timestamp = 1234567890
		self.seqno = 0
		self.ssrc = 0xDEADBEEF

	def setPeerSdp(self, peerSdp):
		""" During renegotiation, the peer SDP may change """
		self.peerSdp = peerSdp
		if len(peerSdp.media) > 0:
			peerIp = peerSdp.media[0].c[2] if peerSdp.media[0].c else peerSdp.connection[2]
			self.dstAddr = (peerIp, int(peerSdp.media[0].m[1]), 'udp')
			self.dstRTCP = (peerIp, int(peerSdp.media[0].m[1])+1, 'udp')

	def sendTest(self, type):
		if self.peerSdp is None:
			return False
		pkt = RtpEvent.RtpEvent()
		pkt.srcAddress = self.srcAddr
		pkt.dstAddress = self.dstAddr
		if self.seqno == 0:
			mark = self.pt | 0x80
		else:
			mark = self.pt
		pkt.data = struct.pack('!BBHLL', 0x80, mark, self.seqno, self.timestamp, self.ssrc)
		if type in _payloads:
			pkt.data += _payloads[type]
			self.timestamp+=len(_payloads[type])
		self.seqno+=1
		self.neh.writeEvent(pkt)
		return True

	def sendRTCP(self):
		if self.peerSdp is None:
			return False
		pkt = RtpEvent.RtpEvent()
		pkt.srcAddress = self.srcRTCP
		pkt.dstAddress = self.dstRTCP
		pkt.data = struct.pack('!BBHLL', 0x80, 12, self.seqno, self.timestamp, self.ssrc)
		self.rtcpNeh.writeEvent(pkt)
		return True

	def recvPacket(self):
		self.neh.setReadTimeout(0.2)	# 100ms is ample for audio
		return self.neh.readEvent()

	def recvRTCPPacket(self):
		self.rtcpNeh.setReadTimeout(5)	# Longer interval for rtcp
		return self.rtcpNeh.readEvent()

	def verifyTestPacket(self, type, pkt):
		payload = pkt.data[12:]	# Fixme - parse out the header properly
		if type in _payloads:
			if payload == _payloads[type]:
				return True
		return False

	def expect(self, type=G711A_Test):
		pkt = self.recvPacket()
		if pkt is None:
			self.tc.addResult(TestCase.TC_FAILED, "No media packet received")
			return False
		elif not self.verifyTestPacket(type, pkt):
			self.tc.addResult(TestCase.TC_FAILED, "len" + str(len(pkt.data)))
			self.tc.addResult(TestCase.TC_FAILED, "Incorrect media packet")
			return False
		return True

	def expectRTCP(self):
		pkt = self.recvRTCPPacket()
		if pkt is None:
			self.tc.addResult(TestCase.TC_FAILED, "No RTCP packet received")
			return False
		return True
