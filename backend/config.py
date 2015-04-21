# RESTAPI SERVER SPECIFIC CONSTANTS
run_api_test = False
URL = 'http://localhost:8080'
urls = ('/(.*)', 'RestAPIServer')
server_alive_for = -120  # Use negative value for infinite life

# SCANNER SPECIFIC CONSTANTS
run_basic_test = True
ICMP_REACHABLE_TYPE = ["echo-reply"]
SERVER_URL = 'http://172.24.22.113:8080'