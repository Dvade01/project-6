"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)
"""

import flask
from flask import request, current_app, jsonify, make_response
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
#import config
import datetime

#from mypymongo import brevet_insert, brevet_find
import logging
from flask.views import MethodView
import os
import requests
###
# Globals
###
app = flask.Flask(__name__)
app.debug = True if "DEBUG" not in os.environ else os.environ["DEBUG"]
port_num = True if "PORT" not in os.environ else os.environ["PORT"]




# Get the API address from an environment variable
API_ADDR = os.environ["API_ADDR"]
# Get the API port from an environment variable
API_PORT = os.environ["API_PORT"]
# Construct the API URL by concatenating the address and port obtained above
API_URL = f"http://{API_ADDR}:{API_PORT}/api"

# Define a function to insert a new brevet into the database
def brevet_insert(brevet, start, control_pts):
    # Make an HTTP POST request to the API to insert a new brevet
    _id = requests.post(f"{API_URL}/brevets",json={"start": start,"brevet": brevet,"control_pts": control_pts}).json()
    # Return the ID of the new brevet that was inserted
    return _id

# Define a function to find the most recent brevet in the database
def brevet_find():
    # Make an HTTP GET request to the API to get a list of all brevets in the database
    lists = requests.get(f"{API_URL}/brevets").json()
    # Get the most recent brevet from the list
    brevet = lists[-1]
    # Return a tuple containing the start time, brevet distance, and control points of the most recent brevet
    return ["start"], brevet["brevet"], brevet["control_pts"]

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############

# Importing required modules
@app.route("/insert_brevet", methods=["POST"])
def insert_brevet():
    """Handles POST requests to insert brevet data into a database table

    Returns:
        A JSON response containing the status of the insertion and any error messages
    """

    input_json = request.json

    # A list of keys that must be in the JSON input data
    required_keys = ["brevet", "start", "control_pts"]

    # A dictionary mapping keys to their expected data types
    required_types = {"brevet": str, "start": str, "control_pts": list}

    # A helper function that generates error messages for missing or invalid data
    def generate_error_messages():
        for key in required_keys:
            if key not in input_json:
                yield f"Missing required key: {key}"
        for key, value_type in required_types.items():
            if key in input_json and not isinstance(input_json[key], value_type):
                yield f"{key} should be of type {value_type.name}"
        for i, control_pt in enumerate(input_json.get("control_pts", [])):
            if not isinstance(control_pt, dict):
                yield f"control_pt {i} should be a dict"

    # Call the error message generator and store the results in a list
    errors = list(generate_error_messages())

    # If there are any errors, return a JSON response with the error message
    if errors:
        error_message = ", ".join(errors)
        return flask.jsonify(data_content={}, response="Input Error", status=0, mongo_id='None', errors=error_message)

    # Call a function to insert the data into a database table and store the table ID
    table_id = brevet_insert(input_json["brevet"], input_json["start"], input_json["control_pts"])

    # Return a JSON response indicating success and the table ID
    return flask.jsonify(data_content={}, response="Inserted!", status=1, mongo_id=table_id)





@app.route("/_calc_times")
def _calc_times():
    # Log request
    app.logger.debug("Got a JSON request")

    # Retrieve request parameters
    km = request.args.get('km', 999, type=float)
    brev_km_dist = request.args.get('brev_km_dist', default=None, type=int)
    if brev_km_dist is None:
        # If 'brev_km_dist' is not provided or is not a valid integer, raise an HTTPException with a 400 Bad Request status code
        raise BadRequest("Missing or invalid 'brev_km_dist' parameter")
    brev_start = request.args.get('brev_start_date', default=None, type=str)
    if brev_start is None:
        # If 'brev_start_date' is not provided or is not a valid string, raise an HTTPException with a 400 Bad Request status code
        raise BadRequest("Missing or invalid 'brev_start_date' parameter")

    # Convert start date to Arrow object for calculations
    start_time = arrow.get(brev_start)

    # Log parameters for debugging purposes
    app.logger.debug("km={}".format(km))
    app.logger.debug("brev_dist={}".format(brev_km_dist))
    app.logger.debug("brev_start={}".format(brev_start))

    # Calculate open and close times based on input parameters
    open_time = acp_times.open_time(km, brev_km_dist, start_time)  # calculate open time
    open_time_str = open_time.format('YYYY-MM-DDTHH:mm')  # Removed isoformat for readability

    close_time = acp_times.close_time(km, brev_km_dist, start_time)  # calculate close time
    close_time_str = close_time.format('YYYY-MM-DDTHH:mm')  # Removed isoformat for readability

    data_content = {"open": open_time_str, "close": close_time_str}
    return flask.jsonify(data_content=data_content)





class FetchBrevetAPI(MethodView):
    """Class-based view to handle GET requests to fetch brevet data from an API endpoint"""

    def get(self):
        """Handles GET requests to fetch brevet data from an API endpoint

        Returns:
            A JSON response containing the fetched data and a status message
        """

        # Log a debug message
        app.logger.debug('Got a JSON request: FETCH')

        # Call brevet_find function to get brevet, start, and control_pts data
        brevet, start, control_pts = brevet_find()

        # Create a response dictionary containing data_content, status, and response
        response = {
            'data_content': {'brevet': brevet, 'start': start, 'control_pts': control_pts},
            'status': 1 if brevet and start and control_pts else 0,
            'response': 'Successfully fetched a table!' if brevet and start and control_pts else "Something went wrong, couldn't fetch any tables!"
        }

        # Return the response in JSON format
        return jsonify(**response)


# Add a URL rule to map the /fetch_brevet endpoint to the FetchBrevetAPI view
app.add_url_rule('/fetch_brevet', view_func=FetchBrevetAPI.as_view('fetch_brevet'))
#############

app.debug = os.environ["DEBUG"] # removed config because no use of it.


if __name__ == "__main__":
    app.run(port=os.environ["PORT"], host="0.0.0.0")
