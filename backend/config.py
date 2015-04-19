URL = 'http://localhost:8080'
urls = ('/(.*)', 'RestAPIServer')
server_alive_for = 120 # Use negative value for infinite life
run_api_test = False
run_basic_test = False

ICMP_REACHABLE_TYPE = ["echo-reply"]