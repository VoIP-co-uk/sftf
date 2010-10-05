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
# $Id: name_addr.py,v 1.6 2004/03/30 21:52:36 lando Exp $
#
def parse(v):
		displayname = None
		uristr = None
		rem = ""
		params = []
		brackets = False
		if (v is None) or (len(v) == 0):
			return displayname, uristr, params, brackets
		lq = v.find("\"")
		if (lq != -1):
			rq = v[lq+1:].find("\"")
		lb = v.find("<")
		if (lb != -1):
			rb = v[lb+1:].find(">")
			brackets = True
		if (lq > lb):
			lq = -1
			rq = -1
		if (lq != -1 and lb != -1 and lq < lb):
			displayname = v[lq+1:lq+1+rq]
			uristr = v[lb+1:lb+1+rb]
			rem = v[lb+2+rb:]
		elif (lq == -1 and lb != -1):
			displayname = v[:lb].rstrip()
			uristr = v[lb+1:lb+1+rb]
			rem = v[lb+2+rb:]
		elif (lq == -1 and lb == -1):
			# ; would introduce header parameters, but we can not
			# distinguish between header and URI parameters here, so
			# we just signal if we found brackets and the caller of
			# this function needs to take care of the rest
			uristr = v
			rem = ""
		semi = rem.find(";")
		if (semi != -1):
			params = rem[semi+1:].split(";")
		elif len(rem) > 0:
			params.append(rem)
		if (displayname is not None and len(displayname) == 0):
			displayname = None
		return displayname, uristr, params, brackets
