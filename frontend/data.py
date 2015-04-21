from flask import jsonify
import json
import time

def fetch():
	time.sleep(20)
	return json.dumps([{"employees":[
	    {"firstName":"John", "lastName":"Doe"},
	    {"firstName":"Anna", "lastName":"Smith"},
	    {"firstName":"Peter", "lastName":"Jones"}
	]}])
