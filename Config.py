# the local IP
LOCAL_HOSTNAME = ""
LOCAL_IP = ""

# the local port
LOCAL_PORT = 5060

# the name or IP of the UA
TEST_HOST = "192.168.0.134"

# the port at the UA
TEST_HOST_PORT = 5060

# the name of the user at the UA
TEST_USER_NAME = "abc"

# the password of the user at the UA
TEST_USER_PASSWORD = "abc"

# the path to the directory for the test cases
TEST_CASE_PATH = "./UserAgentBasicTestSuite"

# a list of the directories seperated by semicolon for the parser modules
PARSER_PATH = "./HFH;./BodyParser"

# log level [0..5]
LOG_LEVEL = 5

# should debug be logged to stdout additionally to files
LOG_DEBUG_STD_OUT = True

# should all received and send packets be logged to debug
LOG_NETWORK_PACKETS = True

# at which log level packets should be logged
LOG_NETWORK_PACKETS_LEVEL = 5

# should tests be logged to stdout additionally to files
LOG_TESTS_STD_OUT = True

# the file for the debuging output
LOG_DEBUG_FILE = "debug.log"

# the file for test case output
LOG_TESTS_FILE = "sftf.log"

# the default file read in by FileEventListener
DEF_SIP_FILE= "test_in.sip"

# the maximum packet size read from network
MAX_PKG_SIZE = 8192

# the name of the user within SC
# (which has to be called)
SC_USER_NAME = "sc"

# the default realm value for authentication
AUTH_REALM = "SFTF"

# should qop be used by default for authentication
AUTH_QOP = False

# the starting number for the local CSeq number
LOCAL_CSEQ = 1

# the default expires value for the 200 OK on a REGISTER
# if the UAC omitted the expires value
DEFAULT_EXPIRES = 3600

# if a read from the network was not successfull after this
# amount of time a network timeout will be raised.
# Set this to an higher value if your are for example testing
# a media gateway with higher delays (e.g. PSTN or GSM).
DEFAULT_NETWORK_TIMEOUT = 5.0

# if no transport protocol is given within the test itself
# the following default will be used instead to transport
# the SIP requests
DEFAULT_NETWORK_TRANSPORT = "UDP"

# if set to True for each test run a XML file will be
# created which is named like the test itself, and which
# can be viewed with the sipviewer
# !! beta status !!
LOG_SIPVIEWER_XML = False

# should the GUI be used for interaction with user
# NOTE: not implemented yet !!!
USE_GUI = False
