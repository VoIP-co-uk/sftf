#
# Copyright (C) 2004 SIPfoundry Inc.
# Licensed by SIPfoundry under the GPL license.
#
# Copyright (C) 2004 SIP Forum
# Licensed to SIPfoundry under a Contributor Agreement.
#
#
# This file is part of SIP Forum User Agent Basic Test Suite which
# belongs to the SIP Forum Test Framework.
#
# SIP Forum User Agent Basic Test Suite is free software; you can 
# redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation; either 
# version 2 of the License, or (at your option) any later version.
#
# SIP Forum User Agent Basic Test Suite is distributed in the hope that it 
# will be useful, but WITHOUT ANY WARRANTY; without even the implied 
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SIP Forum User Agent Basic Test Suite; if not, write to the 
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, 
# MA  02111-1307  USA
#
# $Id: case605s.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log
from Helper import eventTimeDiff

class case605s (TestCase):

	def config(self):
		self.name = "Case 605s"
		self.description = "Correct UDP retransmission timing"
		self.isClient = False
		self.transport = "UDP"
		self.interactRequired = True
		self.ignoreRetrans = False
		self.autoReact = False

	def run(self):
		min_percent = 0.9
		max_percent = 1.1

		# creating a network socket is always required
		self.neh = NEH.NetworkEventHandler(self.transport)

		end = False
		received = False
		req_array = []
		
		print "  !!!!  PLEASE CALL ANY NUMBER/USER  !!!!"
		while not end:
			req = self.readRequestFromNetwork(self.neh, 40, TimeoutError=False)
			if req is None:
				if received:
					end = True
				else:
					print "  !!!!  PLEASE CALL ANY NUMBER/USER  !!!!"
			elif req.method == "INVITE":
				if not received:
					received = True
				req_array.append(req)

		# at the end please close the socket again
		self.neh.closeSock()

		# finally check for the results of the test
		passed = True
		req_a_l = len(req_array)
		# check for the correct number of retries
		if req_a_l != 7:
			self.addResult(TestCase.TC_FAILED, "instead of 7 INVITE requests " + str(req_a_l) + " requests have been received")
			passed = False
		if req_a_l > 1:
			time_array = []
			num_len = range(0, req_a_l-1)
			for i in num_len:
				time_array.append(eventTimeDiff(req_array[i].event, req_array[i+1].event))
			# check if T1 is 500ms
			if time_array[0] < (min_percent * 0.5):
				self.addResult(TestCase.TC_FAILED, "timer for first retry (T1=0.5s) is below " + str(min_percent * 0.5) + " (" + str(time_array[0]) + ")")
				passed = False
			elif time_array[0] > (max_percent * 0.5):
				self.addResult(TestCase.TC_FAILED, "timer for first retry (T1=0.5s) is above " + str(max_percent * 0.5) + " (" + str(time_array[0]) + ")")
				passed = False
			num_len2 = range(0, len(time_array)-1)
			# check if T1 is doubled for each retry
			for j in num_len2:
				if time_array[j+1] < 2*time_array[j]*min_percent:
					self.addResult(TestCase.TC_FAILED, "timer for retry " + str(j+1) + " is less then doubled (" + str(time_array[j]) + ", " + str(time_array[j+1]) + ")")
					passed = False
				elif time_array[j+1] > 2*time_array[j]*max_percent:
					self.addResult(TestCase.TC_FAILED, "timer for retry " + str(j+1) + " is more then doubled (" + str(time_array[j]) + ", " + str(time_array[j+1]) + ")")
					passed = False
			t_sum = 0.0
			for k in time_array:
				t_sum = t_sum + k
			# check if last retry was at 63*T1
			if t_sum < (min_percent*63*time_array[0]):
				self.addResult(TestCase.TC_FAILED, "last retry (" + str(t_sum) + ") is below 63*T1 (=" + str(min_percent*63*time_array[0]) + ")")
				passed = False
			elif t_sum > (max_percent*63*time_array[0]):
				self.addResult(TestCase.TC_FAILED, "last retry (" + str(t_sum) + ") is above 63*T1 (=" + str(min_percent*63*time_array[0]) + ")")
				passed = False
			if passed:
				self.addResult(TestCase.TC_PASSED, "UDP request retransmission matches RFC")
