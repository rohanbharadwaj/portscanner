# REST-API SERVER SPECIFIC CONSTANTS
LOCAL_SERVICE_PORT = 8080
URL = 'http://localhost:{0}'.format(LOCAL_SERVICE_PORT)
URL_PATTERN_SERVICED = ('/(.*)', 'RestAPIServer')
SERVER_ALIVE_FOR_SECONDS = -120  # Use negative value for infinite life
RUN_API_TEST = False

# SCANNER SPECIFIC CONSTANTS
SERVER_IP = "172.24.30.140"
SERVER_PORT = 8080
SERVER_URL = 'http://{0}:{1}'.format(SERVER_IP, SERVER_PORT)

TIME_IN_SEC_BETWEEN_HEARTBEATS = 5
HEARTBEATS_SKIPPED_BEFORE_REAPING = 2

MAX_THREADS = 500
RUN_BASIC_TEST = False
ICMP_REACHABLE_TYPE = ["echo-reply"]