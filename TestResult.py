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
# $Id: TestResult.py,v 1.3 2004/03/19 18:37:25 lando Exp $
#
from SCException import SCException

def getResultString(res):
	"""Returns the test result number as string."""
	if res == TestResult.TR_INIT:
		return "Initialized"
	elif res == TestResult.TR_PASSED:
		return "Passed"
	elif res == TestResult.TR_FAILED:
		return "Failed"
	elif res == TestResult.TR_WARN:
		return "Warning"
	elif res == TestResult.TR_CAUT:
		return "Caution"
	elif res == TestResult.TR_CANC:
		return "Canceled"
	elif res == TestResult.TR_ERROR:
		return "Error"
	else:
		return "Undefined: " + str(res)

class TestResult:
	"""This class just provides a generic container for test results, with
	an integer as test result and a string as descriptionale reason for
	this result.
	"""

	TR_INIT = 0
	TR_PASSED = 1
	TR_FAILED = 2
	TR_WARN = 4
	TR_CAUT = 8
	TR_CANC = 16
	TR_ERROR = 32

	def __init__(self, res=None, reason=None):
		self.name = None
		self.description = None
		self.result = TestResult.TR_INIT
		self.reason = None
		if res is not None and reason is not None:
			self.setResult(res, reason)

	def __str__(self):
		return "[name:'" + str(self.name) + "', " \
				"description:'" + str(self.description) + "', " \
				"result:'" + getResultString(self.result) + "', " \
				"reason:'" + str(self.reason) + "']"

	def setResult(self, res, reason):
		"""Sets the given result number and reason phrase for the instance."""
		if (res < TestResult.TR_INIT) or (res > TestResult.TR_ERROR):
			raise SCException("TestResult", "setResult", "unknown/unsupported test case result")
		self.result = res
		self.reason = reason

