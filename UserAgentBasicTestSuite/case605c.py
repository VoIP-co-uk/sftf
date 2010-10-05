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
# $Id: case605c.py,v 1.2 2004/05/02 18:57:36 lando Exp $
#
from TestCase import TestCase
import NetworkEventHandler as NEH
import Log
from Helper import eventTimeDiff

class case605c (TestCase):

	def config(self):
		self.name = "Case 605c"
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

		inv = self.createRequest("INVITE")
		re = self.getParsedHeaderInstance("Require")
		re.tags.append("FooBar")
		inv.setHeaderValue("Require", re.create())
		self.writeMessageToNetwork(self.neh, inv)

		end = False
		received = False
		repl_array = []

		while not end:
			repl = self.readReplyFromNetwork(self.neh, 40, TimeoutError=False)
			if repl is None:
				end = True
				if not received:
					self.addResult(TestCase.TC_ERROR, "missing reply on INVITE request")
			elif repl.code == 100:
				Log.logTest("Ignoring 100 for retransmisson timing")
			elif repl.code == 420:
				received = True
				repl_array.append(repl)
			else:
				self.addResult(TestCase.TC_ERROR, "INVITE with Require:FooBar not rejected with 420")
				end = True
				
		# at the end please close the socket again
		self.neh.closeSock()

		# finally check for the results of the test
		passed = True
		repl_a_l = len(repl_array)
		if (repl_a_l != 11) and (repl_a_l > 0):
			self.addResult(TestCase.TC_FAILED, "instead of 11 replies " + str(repl_a_l) + " replies have been received")
			passed = True
		if repl_a_l > 1:
			time_array = []
			num_len = range(0, repl_a_l - 1)
			for i in num_len:
				time_array.append(eventTimeDiff(repl_array[i].event, repl_array[i+1].event))
			if time_array[0] < (min_percent * 0.5):
				self.addResult(TestCase.TC_FAILED, "timer for first retry (T1=0.5s) is below " + str(min_percent * 0.5) + " (" + str(time_array[0]) + ")")
				passed = False
			elif time_array[0] > (max_percent * 0.5):
				self.addResult(TestCase.TC_FAILED, "timer for first retry (T1=0.5s) is above " + str(max_percent * 0.5) + " (" + str(time_array[0]) + ")")
				passed = False
			if len(time_array) > 4:
				f_ran = range(0, 4)
				t_ran = range(4, len(time_array)-1)
				for i in f_ran:
					if time_array[i+1] < 2*time_array[i]*min_percent:
						self.addResult(TestCase.TC_FAILED, "timer for retry " + str(i+1) + " is less than doubled (" + str(time_array[i]) + ", " + str(time_array[i+1]) + ")")
						passed = False
					elif time_array[i+1] > 2*time_array[i]*max_percent:
						self.addResult(TestCase.TC_FAILED, "timer for retry " + str(i+1) + " is more than doubled (" + str(time_array[i]) + ", " + str(time_array[i+1]) + ")")
						passed = False
				for j in t_ran:
					if time_array[j] < 4.0*min_percent:
						self.addResult(TestCase.TC_FAILED, "timer for retry " + str(j+1) + " is less than T2 (=" + str(4.0*min_percent) + "s) (" + str(time_array[j]) + ")")
						passed = False
					elif time_array[j] > 4.0*max_percent:
						self.addResult(TestCase.TC_FAILED, "timer for retry " + str(j+1) + " is more than T2 (=" + str(4.0*max_percent) +  "s) (" + str(time_array[j]) + ")")
						passed = False
			else:
				num_len2 = range(0, len(time_array)-1)
				for i in num_len2:
					if time_array[i+1] < 2*time_array[i]*min_percent:
						self.addResult(TestCase.TC_FAILED, "timer for retry " + str(i+1) + " is less than doubled (" + str(time_array[i]) + ", " + str(time_array[i+1]) + ")")
						passed = False
					elif time_array[i+1] > 2*time_array[i]*max_percent:
						self.addResult(TestCase.TC_FAILED, "timer for retry " + str(i+1) + " is more than doubled (" + str(time_array[i]) + ", " + str(time_array[i+1]) + ")")
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
				self.addResult(TestCase.TC_PASSED, "UDP reply retransmission matches RFC")
