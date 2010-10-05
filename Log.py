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
# $Id: Log.py,v 1.5 2004/03/19 18:37:25 lando Exp $
#
import Config, time

SC_LOG_DEBUG = 0
SC_LOG_TESTS = 1

def init():
	global debugLogFile
	global testsLogFile
	if Config.LOG_DEBUG_FILE != "":
		debugLogFile = file (Config.LOG_DEBUG_FILE, "a")
	if Config.LOG_TESTS_FILE != "":
		testsLogFile = file (Config.LOG_TESTS_FILE, "a")

def log(message, level, dest, stdout):
	"""Writes the given message to the given file and standard output if
	the given level is above the configured log level.
	"""
	if dest == SC_LOG_DEBUG:
		if level <= Config.LOG_LEVEL:
			if stdout:
				print time.strftime("%b %d %H:%M:%S", time.localtime()) + ": " + message
			debugLogFile.write(time.strftime("%b %d %H:%M:%S", time.localtime()) + ": " + message + "\n")
	elif dest == SC_LOG_TESTS:
		if stdout:
			print time.strftime("%b %d %H:%M:%S", time.localtime()) + ": " + message
		testsLogFile.write(time.strftime("%b %d %H:%M:%S", time.localtime()) + ": " + message + "\n")
	else:
		print "unknown logging destination!"

def logTest(message):
	"""Writes the message to the test result file and standard out with
	log level 0.
	"""
	log(message, 0, SC_LOG_TESTS, Config.LOG_TESTS_STD_OUT)

def testLog(message):
	"""See logTest.
	"""
	logTest(message)

def logDebug(message, level):
	"""Writes the message to the debug log file and standard output if the
	given log level value is above the configured level.
	"""
	log(message, level, SC_LOG_DEBUG, Config.LOG_DEBUG_STD_OUT)

def debugLog(message, level):
	"""See logDebug.
	"""
	logDebug(message, level)
