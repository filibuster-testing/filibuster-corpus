from flask import Flask, jsonify, request, json
from werkzeug.exceptions import ServiceUnavailable
import os
import sys


examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.append(examples_path)

import helper
helper = helper.Helper("case-study-1-food-delivery-example-1")

app = Flask(__name__)

## Instrument using filibuster

sys.path.append(os.path.dirname(examples_path))

from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="auth", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="auth", filibuster_url=helper.get_service_url('filibuster'))

# filibuster requires a health check app to ensure service is running
@app.route("/health-check", methods=['GET'])
def baz_health_check():
    return jsonify({ "status": "OK" })

# This method grants authorization to create, update, or delete orders
@app.route("/auth", methods=['POST'])
def authorize():
    
    # get authorization type and order data
    data = json.loads(request.data)       
    auth_type = str(data["auth_type"])    
    order_details = data['order_details']   

    # here a bug is introduced in the logic that checks if an order is create, update, or delete
    # the bugs causes all 'delete' authorizations to be refused, with status 424     
    if auth_type == "create" or auth_type == "update" or auth_type == "delet":
        return jsonify({"status": 200, "authorized": True, "auth_type": auth_type, "order_details": order_details})

    #since "delete" is misspelled above, all "delete" authorization will be refused
    else:        
        return jsonify({"status": 424, "authorized": False, "auth_type": auth_type, "order_details": order_details})            


if __name__ == "__main__":
    app.run(port=helper.get_port('auth'), host="0.0.0.0", debug=helper.get_debug())