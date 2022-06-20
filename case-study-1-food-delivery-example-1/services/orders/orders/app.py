from http.client import responses
from flask import Flask, jsonify
from werkzeug.exceptions import ServiceUnavailable
import requests
import os
import sys
import json

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.append(examples_path)

import helper
helper = helper.Helper("case-study-1-food-delivery-example-1")

app = Flask(__name__)

## Instrument using filibuster

sys.path.append(os.path.dirname(examples_path))

from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="orders", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="orders", filibuster_url=helper.get_service_url('filibuster'))

#the get_auth method checks to see if an order is authorized, by requesting authorization 
#from the auth service and returning the auth service's response to the calling method

# filibuster requires a health check app to ensure service is running
@app.route("/health-check", methods=['GET'])
def foo_health_check():
    return jsonify({ "status": "OK" })


@app.route("/orders/create", methods=['GET'])
def create():

    #declare a random order (in practice, these details would be passed into the function)
    auth_type = "create"
    order_details = {"id" : 1234, "amount" : 9.99}

    return get_auth(auth_type, order_details) 


@app.route("/orders/update", methods=['GET'])
def update():

    #declare a random order (in practice, these details would be passed into the function)
    auth_type = "update"
    order_details = {"id" : 1234, "amount" : 11.99}

    return get_auth(auth_type, order_details)


@app.route("/orders/delete", methods=['GET'])
def delete():

    #declare a random order (in practice, these details would be passed into the function)
    auth_type = "delete"
    order_details = {"id" : 1234, "amount" : 11.99}

    return get_auth(auth_type, order_details)    
   

# This method communicates with the auth method in the auth app. It handles all authorization requests
# from the create, update, and delete methods
def get_auth(auth_type, order_details):  

    #get the order data from whichever method requests authorization 
    order_data = json.dumps({"auth_type": auth_type, "order_details": order_details})
    
    #send the data in a POST request to the authorization service
    try:
        response = requests.post("{}/auth".format(helper.get_service_url('auth')), timeout=helper.get_timeout('auth'), data=order_data)
    except requests.exceptions.Timeout:
        raise ServiceUnavailable("The authorization service timed out.")


    if response.status_code != 200: 
        raise ServiceUnavailable("The authorization service is malfunctioning.")    
       

    #return the auth service's response in string format    
    return response.text


if __name__ == "__main__":
    app.run(port=helper.get_port('orders'), host="0.0.0.0", debug=helper.get_debug())