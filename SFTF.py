#!/usr/bin/env python
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
# $Id: SFTF.py,v 1.7 2004/04/27 14:33:44 lando Exp $
#
import Log, Config, Helper
from TestCase import TestCase
from TestResult import TestResult, getResultString
import sys, os, getopt, traceback, socket, py_compile
from NetworkEventHandler import getHostNameIP, getFQDN, checkIPv6Support

def resToCol(res):
	"""Returns the ASCII color code for the given test result.
	"""
	nocol = "\x1b[0;0m"
	if res == TestResult.TR_INIT:
		col = nocol
	elif res == TestResult.TR_PASSED:
		# Green
		col = "\x1b[32;01m"
	elif res == TestResult.TR_FAILED:
		# Red
		col = "\x1b[31;01m"
	elif res == TestResult.TR_WARN:
		# Yellow
		col = "\x1b[33;01m"
	elif res == TestResult.TR_CAUT:
		# ???
		col = "\x1b[35;01m"
	elif res == TestResult.TR_CANC:
		# Blue
		col = "\x1b[34;01m"
	elif res == TestResult.TR_ERROR:
		# Cyan
		col = "\x1b[36;01m"
	else:
		col = nocol
	return col

class SFTF:
	"""This is the main class of the SIP Forum Test Framework. It reads in
	the test cases, provides the extensions and handling of subdirectories,
	initialize all global data and generates the final results screen.
	"""

	def __init__(self):
		self.ver = "0.9.3"
		self.clientOnly = False
		self.serverOnly = False
		self.nonInteractOnly = False
		self.interactOnly = False
		self.nonRegister = False
		self.register = False
		self.colorOutput = True
		self.verboseSummary = True
		self.debug = False
		self.test = []
		self.directories = []
		self.tcdirs = str(Config.TEST_CASE_PATH).split(";")
		for dirs in str(Config.PARSER_PATH).split(';'):
			sys.path.append(dirs)
		# FIXME: currently this just prevents compile time during run time
			hfhl = os.listdir(dirs)
			for i in hfhl:
				if i.endswith(".py"):
					py_compile.compile(dirs + os.sep + i)
					#hfhname = i[:len(i)-3]
					#Helper.importModule(hfhname)

	def addTestCase(self, testcase):
		"""Just add the given test case instance to the list of test to be run.
		"""
		self.test.append(testcase)

	def addDirectory(self, dir):
		"""Just add the given directory name to the list of directories for
		add-ons and test cases.
		"""
		self.directories.append(dir)

	def readInTestCase(self, _tcname):
		"""Tries to load and add the test case with the given name.
		"""
		tc = Helper.createClassInstance(_tcname)
		if tc:
			if isinstance(tc, TestCase):
				self.addTestCase(tc)
			else:
				Log.logDebug("SFTF.readInTestCase(): \'" + str(_tcname) + " has not TestCase as base, skipping", 1)

	def readInTestCases(self):
		"""Reads in all test cases from the test case directory.
		"""
		#tcl = os.listdir(Config.TEST_CASE_PATH)
		for d in self.tcdirs:
			tcl = sorted(os.listdir(d))
			for i in tcl:
				if i.endswith(".py"):
					tcname = i[:len(i)-3]
					self.readInTestCase(tcname)

	def run(self):
		"""The main function of the SFTF class which read in all tests, checks
		if the tests matches the desired characteristics determined by the
		command line arguments and finally prints the result summary.
		"""
		Log.logDebug("======================", 2)
		Log.logDebug("SFTF.run(): v" + str(self.ver) + " started", 4)
		#sys.path.append(Config.TEST_CASE_PATH)
		for d in self.tcdirs:
			sys.path.append(d)
		for p in self.directories:
			sys.path.append(p)
		if len(self.test) > 0:
			tcloadlist = self.test
			self.test = []
			for i in tcloadlist:
				self.readInTestCase(i)
		else:
			self.readInTestCases()
		Log.logDebug("SFTF.run(): read in test cases: " + str(self.test), 4)
		if len(self.test) == 0:
			Log.logDebug("no test cases loaded, nothing to do, exiting...", 1)
			return
		Log.logTest("configuring tests ...")
		final_tests = []
		for i in self.test:
			i.config()
			if (i.name is None) or (i.description is None) or (i.transport is None) or (i.isClient is None):
				Log.logDebug("SFTF.run(): mandatory configuration (name, description, transport and isClient) is incomplete, ignoring " + str(i), 1)
				Log.logTest("ignoring " + str(i) + " because of incomplete configuration")
			else:
				if (not i.isClient) and (not i.interactRequired):
					Log.logDebug("SFTF.run(): WARNING: test " + str(i.name) + " is server and interaction is not required: fixing", 1)
					Log.logTest("WARNING: test " + str(i.name) + " is server and interaction is not required: fixing")
					i.interactRequired = True
				append = True
				if i.isClient and self.serverOnly:
					append = False
				if (not i.isClient) and self.clientOnly:
					append = False
				if i.interactRequired and self.nonInteractOnly:
					append = False
				if (not i.interactRequired) and self.interactOnly:
					append = False
				if i.register and self.nonRegister:
					append = False
				if (not i.register) and self.register:
					append = False
				if (i.minAPIVersion is not None) and (TestCase.TC_API_VERSION < i.minAPIVersion):
					Log.logTest("'" + i.name + "' required minimum API version (" + str(i.minAPIVersion) + ") is above your API version (" + str(TestCase.TC_API_VERSION) + ")")
					Log.logTest("please update the framework if you want to be able to run this test")
					append = False
				if (i.maxAPIVersion is not None) and (TestCase.TC_API_VERSION > i.maxAPIVersion):
					Log.logTest("'" + i.name + "' required maximum API version is below your API version (" + TestCase.TC_API_VERSION + ")")
					Log.logTest("pleasse update the test case to the new API of your framework")
					append = False
				if append:
					final_tests.append(i)
		self.test = final_tests
		if len(self.test) == 0:
			Log.logDebug("no test cases loaded, nothing to do, exiting...", 1)
			return
		if not hasattr(Config, "resources"):
			Config.resources = {'NEH': {}, 'MediaSockets': [], 'FEH': {}, 'XMLEH': {}}
		if Config.LOG_SIPVIEWER_XML:
			try:
				import XMLEventHandler
				Config.XMLEHavailable = True
			except ImportError:
				Log.logDebug("SFTF.run(): SIPVIEWER_XML enabled but XMLEventHandler is missing", 1)
				Config.XMLEHavailable = False
		Log.logDebug("SFTF.run(): running these tests: " + str(self.test), 5)
		for j in self.test:
			if Config.LOG_SIPVIEWER_XML and Config.XMLEHavailable:
				Config.resources['XMLEH'][j.name] = XMLEventHandler.XMLEventHandler(j.name + ".xml")
			Log.logTest("===================")
			Log.logTest("starting test: " + j.name + " ...")
			Log.logDebug("===================", 1)
			Log.logDebug("starting test: " + j.name + " ...", 1)
			try:
				j.run()
			except KeyboardInterrupt:
				Log.logDebug("test run interrupted by user through keyboard => exiting", 1)
				Log.logTest("test run interrupted by user => exiting")
				if self.debug:
					return
				else:
					sys.exit()
			except socket.error, inst:
				if inst[0] == 98:
					print " The address from the above message is allready in use!!!\n Please change the port in Config.py or in the test '" + j.name + "'\n or close the application which uses this address."
				else:
					Log.logDebug("socket.error: " + str(inst), 1)
				sys.exit(3)
			except Exception, inst:
				print "  Caught exception during running '" + j.name + "'"
				traceback.print_exc(file=Log.debugLogFile)
				traceback.print_exc(file=sys.stdout)
				print "  ! Please report this bug as described at the web page !"
				sys.exit(3)
			for k in j.results:
				Log.logTest(getResultString(k.result) + ": " + k.reason)
			Log.logTest("\'" + j.name + "\' result = " + getResultString(j.getOneResult()))
			Log.logTest("===================")
			if Config.resources.has_key('MediaSockets'):
				for sp in Config.resources['MediaSockets']:
					sp[0].close()
					sp[1].close()
				Config.resources['MediaSockets'] = []
			if Config.resources.has_key('XMLEH') and Config.resources['XMLEH'].has_key(j.name):
				Config.resources['XMLEH'][j.name].close()
		for i in Config.resources['NEH']:
			Config.resources['NEH'][i].close()
		for j in Config.resources['FEH']:
			Config.resources['FEH'][j].close()
		for k in Config.resources['MediaSockets']:
			k[0].close()
			k[1].close()
		print "====================\nTest result summary:\n===================="
		if self.colorOutput:
			nocol = "\x1b[0;0m"
		else:
			nocol = ''
		Config.LOG_TESTS_STD_OUT = False
		for i in self.test:
			res = i.getOneResult()
			if self.colorOutput:
				col = resToCol(res)
			else:
				col = nocol
			res_s = "[" + col + getResultString(res) + nocol + "]"
			print i.name + ":\t" + res_s
			res_log = "[" + getResultString(res) + "]"
			Log.logTest(i.name + ":\t" + res_log)
			if self.verboseSummary:
				print "  Description: " + i.description
				Log.logTest("  Description: " + i.description)
				for j in i.results:
					if self.colorOutput:
						col = resToCol(j.result)
					else:
						col = nocol
					print "\t\t[" + col + getResultString(j.result) + nocol + "] : " + j.reason
					Log.logTest("\t\t[" + getResultString(j.result) + "] : " + j.reason)
				print "--------------------------------------------"
				Log.logTest("--------------------------------------------")

	def version(self):
		"""Prints just the version and copyright informations.
		"""
		print "SIP Forum Test Framework v" + str(self.ver) + " by Nils Ohlmeier\n" \
			"  Copyright (C) 2004 SIPfoundry Inc.\n" \
			"  Copyright (C) 2004 SIP Forum"

	def usage(self):
		"""Print the version first and the help screen.
		"""
		self.version()
		print "\nSFTF.py [-acCdhiIrRsSV] [-D directory] [-t testcasename] [testcasename]\n" \
			"  -a                run all tests\n" \
			"  -c                run UAC tests only\n" \
			"  -C                dont use colors on output\n" \
			"  -d                dont exit on keyboard interrupt\n" \
			"  -D directory      add the dir to file search path\n" \
			"  -h                print this help screen\n" \
			"  -i                run non-interactive tests only\n" \
			"  -I                run interactive tests only\n" \
			"  -r                run tests without REGISTER only\n" \
			"  -R                run tests with REGISTER only\n" \
			"  -s                run UAS tests only\n" \
			"  -S                turn off verbose test summary\n" \
			"  -t testcasename   load and run testcasename\n" \
			"                    (can be given multiple times)\n" \
			"  -u directory      override test-suite directory\n" \
			"  -V                print the version information\n"

def main():
	"""This function will be called first to parse the command line
	arguments, initializes the global data like logging, and finally
	creates one instance of the SFTF class and calls the run method.
	"""
	Log.init()
	sc=SFTF()
	try:
		opts, args = getopt.getopt(sys.argv[1:], "acCdD:hiIrRsSt:u:V", ["all", "client", "debug", "directory", "help", "interactive", "no-color", "non-interactive", "no-register", "no-summary", "register", "server", "testcase=", "test-suite=", "version"])
	except getopt.GetoptError, arg:
		print arg
		sc.usage()
		sys.exit(2)
	if len(opts) == 0 and len(args) == 0:
		sc.usage()
		sys.exit(1)
	for o, a in opts:
		if o in ("-a", "--all"):
			sc.clientOnly = False
			sc.serverOnly = False
			sc.interactOnly = False
			sc.nonInteractOnly = False
			sc.register = False
			sc.nonRegister = False
		if o in ("-c", "--client"):
			sc.clientOnly = True
		if o in ("-C", "--no-color"):
			sc.colorOutput = False
		if o in ("-d", "--debug"):
			sc.debug = True
		if o in ("-D", "--directory"):
			sc.addDirectory(a)
		if o in ("-h", "--help"):
			sc.usage()
			sys.exit()
		if o in ("-i", "--non-interactive"):
			sc.nonInteractOnly = True
		if o in ("-I", "--interactive"):
			sc.interactOnly = True
		if o in ("-r", "--no-register"):
			sc.nonRegister = True
		if o in ("-R", "--register"):
			sc.register = True
		if o in ("-s", "--server"):
			sc.serverOnly = True
		if o in ("-S", "--no-summary"):
			sc.verboseSummary = False
		if o in ("-t", "--testcase"):
			sc.addTestCase(a)
		if o in ("-u", "--test-suite"):
			sc.tcdirs = a.split(";")
		if o in ("-V", "--version"):
			sc.version()
			sys.exit()
	for t in args:
		sc.addTestCase(t)
	if sc.clientOnly and sc.serverOnly:
		print "error: running only client and only server tests is not possible"
		sys.exit(1)
	if sc.interactOnly and sc.nonInteractOnly:
		print "error: running interactive and non-interacitve tests only is not possible"
		sys.exit(1)
	if sc.register and sc.nonRegister:
		print "error: running non-REGISTER and REGISTER tests only is not possible"
		sys.exit(1)
	if (Config.LOCAL_IP == "") and (Config.LOCAL_HOSTNAME == ""):
		hn, ip = getHostNameIP()
		if (hn is None) or (ip is None):
			sys.exit(1)
		else:
			Config.LOCAL_HOSTNAME = hn
			Config.LOCAL_IP = ip
	elif (Config.LOCAL_IP != "") and (Config.LOCAL_HOSTNAME == ""):
		hn = getFQDN(Config.LOCAL_IP)
		if hn is None:
			print "Failed to lookup the hostname for the given IP ('" + str(Config.LOCAL_IP) + "') from Config.py\r\nPlease fix the IP or specify the full qualified domain hostname as LOCAL_HOSTNAME in Config.py"
			sys.exit(1)
		else:
			Config.LOCAL_HOSTNAME = hn
	elif (Config.LOCAL_HOSTNAME != "") and (Config.LOCAL_IP == ""):
		try:
			#Config.LOCAL_IP = socket.gethostbyname(Config.LOCAL_HOSTNAME)
			adrlist = socket.getaddrinfo(Config.LOCAL_HOSTNAME, Config.LOCAL_PORT, socket.AF_UNSPEC, socket.SOCK_DGRAM, 0)
			Config.LOCAL_IP = adrlist[0][4][0]
		except socket.gaierror:
			print "Failed to resolve LOCAL_HOSTNAME ('" + str(Config.LOCAL_HOSTNAME) + "') from Config.py\r\nPlease fix the hostname or specify the IP as LOCAL_IP in Config.py"
			sys.exit(1)
	checkIPv6Support()
	sc.run()
	return sc

if __name__ == "__main__":
	#FIXME SC is just for debuging
	SC = main()
