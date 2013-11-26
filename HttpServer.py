# Copyright (C) 2011 VoIP.co.uk
# Licensed under the GPL license.
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

import SCException
import Log
from TestCase import TestCase
import NetworkEventHandler as NEH
import BaseHTTPServer
import os.path

from BaseHTTPServer import BaseHTTPRequestHandler
import StringIO

class _MyHttpRequest(BaseHTTPRequestHandler):
	def __init__(self):
		pass

	def parseData(self, ctx, data):
		if ctx is not None:
			data = ctx + data
			ctx = None

		if not '\r\n\r\n' in data:
			""" No end of headers marker - keep accumulating data """
			return data, False

		# Emulate normal request so parsing fn works
		self.rfile = StringIO.StringIO(data)
		self.wfile = StringIO.StringIO()

		self.raw_requestline = self.rfile.readline()
		if not self.parse_request():
			print "Can't parse", self.wfile.getvalue()
			return None, False

		bodylen = int(self.headers.get('Content-Length', '0'))
		body = self.rfile.read(bodylen)
		if len(body) < bodylen:
			""" Not enough body data yet - keep accumulating data """
			return data, False

		# Reset the rfile ready for the handler to read
		self.rfile = StringIO.StringIO(body)

		self.client_address = self.dstAddress
		return None, True

	def genDataString(self):
		ret = self.wfile.getvalue()
		return ret, len(ret)


class HttpServer(object):
	def __init__(self, tc, addr, port):
		self.tc = tc
		self.neh = NEH.NetworkEventHandler('tcp', addr, port, eventType = _MyHttpRequest)
		self.neh.openSock()

	def expect(self, method, uri=None, handlercb=None, timeout=5):
		""" Retry for n seconds until event is produced? """
		self.neh.timeout = timeout
		ev = self.neh.readEvent()
		if not ev:
			if method is not None:
				self.tc.addResult(TestCase.TC_FAILED, "HTTP Timeout: Waiting for %s" % (method,))
			else:
				self.tc.addResult(TestCase.TC_PASSED, "HTTP Timeout: Expected after %ss" % (timeout,))
			return ev

		if ev.command != method:
			ev.send_error(501, "Unexpected method (wanted %r)" % (method,))
			self.commitResponse(ev)
			self.tc.addResult(TestCase.TC_FAILED, "HTTP: Waiting for %s, got %s" % (method, ev.command))
			return None
		if uri and uri != ev.path:
			ev.send_error(404, "Unexpected path (not %r)" % (uri,))
			self.commitResponse(ev)
			self.tc.addResult(TestCase.TC_FAILED, "HTTP: Wrong path, expected %s, got %s" % (uri , self.path))
			return None

		if handlercb:
			handlercb(ev)
			self.commitResponse(ev)

		return ev

	def serveFile(self, filename):
		""" Expects a simple GET request for a specified file and responds with the file contents """
		expectBasename = os.path.basename(filename)
		body = open(filename).read()
		return self.serveString(body, expectBasename)

	def serveString(self, body, urlEndsWith=None):
		""" Expects a simple GET request and responds with the specified contents """
		ev = self.expect('GET')
		if ev is None:
			return

		if urlEndsWith and not ev.path.endswith(urlEndsWith):
			ev.send_error(404, "Unexpected path, expected %r" % (urlEndsWith,))
			self.commitResponse(ev)
			self.tc.addResult(TestCase.TC_FAILED, "HTTP: Expected request for %r, got %r" % (urlEndsWith, ev.path))
			return

		ev.send_response(200)
		ev.send_header('Content-Length', len(body))
		ev.end_headers()
		ev.wfile.write(body)
		self.commitResponse(ev)

	def commitResponse(self, req):
		""" Once the request has been responded to normally, use this
		    to ensure the data is actually sent out
		"""
		req.rawEvent.writeEvent(req)
		req.rawEvent.closeSock()

	def close(self):
		self.neh.closeSock()

# vim:noet:
