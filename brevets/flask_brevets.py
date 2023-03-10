"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)
"""

import flask
import os
import requests
from flask import request
import arrow
import acp_times
import logging

app = flask.Flask(__name__)

API_ADDR = os.environ["API_ADDR"]
API_PORT = os.environ["API_PORT"]
API_URL = f"http://{API_ADDR}:{API_PORT}/api"


def brevet_insert(brev_start_date, brev_km_dist, control_pts):
    """
    Function that sends a POST request to the Flask API to insert a new brevet table into the database.
    """
    # Send a POST request to the API with the brevet table data as JSON
    response = requests.post(f"{API_URL}/brevets",
                             json={"brev_start_date": brev_start_date, "brev_km_dist": brev_km_dist,
                                   "control_pts": control_pts}).json()

    # Return the ID of the newly inserted brevet table
    return response


def brevet_find():
    """
    Function that sends a GET request to the Flask API to fetch the latest brevet table from the database.
    """
    # Send a GET request to the API to fetch all brevet tables
    response = requests.get(f"{API_URL}/brevets").json()

    # If there are no brevet tables, return None for all values
    if not response:
        return None, None, None

    # Get the latest brevet table from the response
    brevet = response[-1]

    # Return the brev_start_date, brev_km_dist, and control_pts values of the latest brevet table
    return brevet["brev_start_date"], brevet["brev_km_dist"], brevet["control_pts"]


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


@app.route("/insert_brevet", methods=['POST'])
def insert_brevet():
    """
    Route function that receives a POST request with JSON data in the body. Expects JSON data with the following keys:
    "brev_start_date", "brev_km_dist", and "control_pts". Calls the function brevet_insert to insert the data into a
    database table. Returns a JSON response with a status code, a message, and a table id.

    Returns:
        JSON response with keys "result", "status", "message", and "mongo_id".
    """

    # Get the JSON data from the request body
    input_json = request.get_json(force=True)

    # Set a default response with an error message
    response = {"result": {}, "status": 0, "message": "Invalid input format", "mongo_id": None}

    # Check if the required keys are in the JSON data
    if all(key in input_json for key in ("brev_start_date", "brev_km_dist", "control_pts")):
        # Extract the values for brev_start_date, brev_km_dist, and control_pts
        brev_start_date = input_json["brev_start_date"]
        brev_km_dist = input_json["brev_km_dist"]
        control_pts = input_json["control_pts"]

        # Call the brevet_insert function to insert the data into a database table
        table_id = brevet_insert(brev_start_date, brev_km_dist, control_pts)

        # Update the response with a success message and the table id
        response = {key: {} if key == "result" else None for key in response}
        response["result"] = {}
        response["status"] = 1
        response["message"] = "Insert Success!"
        response["mongo_id"] = table_id

    # Return the response as a JSON object
    return flask.jsonify(response)


@app.route("/_calc_times")
def _calc_times():
    try:
        # Parse request arguments
        km = request.args.get('km', type=float)
        brev_km_dist = request.args.get('brevet_km_dist', type=float)
        brev_start_date = request.args.get('brevet_brev_start_date', type=str)

        # Check for missing arguments
        if any(arg is None for arg in [km, brev_km_dist, brev_start_date]):
            raise ValueError("Missing one or more required parameters")

        # Parse date and time
        brev_start_time = arrow.get(brev_start_date).to('utc')

        # Calculate open and close times
        open_time = acp_times.open_time(km, brev_km_dist, brev_start_time)
        close_time = acp_times.close_time(km, brev_km_dist, brev_start_time)

        # Format results as JSON
        response = {"open": open_time.format('YYYY-MM-DDTHH:mm'),
                    "close": close_time.format('YYYY-MM-DDTHH:mm')}
        return flask.jsonify(result=response)

    except (ValueError, TypeError, arrow.parser.ParserError) as e:
        app.logger.error(f"Error: {e}")
        error_message = {"error": str(e)}
        return flask.jsonify(error_message), 400


@app.route("/fetch_brevet")
def fetch_brevet():
    """
    Route function that fetches the latest brevet table from the database. Calls the function brevet_find to retrieve
    the brev_start_date, brev_km_dist, and control_pts values. Returns a JSON response with a status code, a message,
    and the fetched data.

    Returns:
        JSON response with keys "result", "status", and "message".
    """

    # Call the brevet_find function to retrieve the latest brevet table from the database
    brev_start_date, brev_km_dist, control_pts = brevet_find()

    # Set a default response with an error message
    response = {"result": {}, "status": 0, "message": "Oops, couldn't fetch any tables"}

    # Check if the values for brev_start_date, brev_km_dist, and control_pts were retrieved successfully
    if brev_start_date is not None and brev_km_dist is not None and control_pts is not None:
        # Update the response with the fetched data and a success message
        response["result"] = {"brev_start_date": brev_start_date, "brev_km_dist": brev_km_dist,
                              "control_pts": control_pts}
        response["status"] = 1
        response["message"] = "Table fetched!"

    # Return the response as a JSON object
    return flask.jsonify(response)


#############

app.debug = os.environ["DEBUG"]
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    app.run(port=os.environ["PORT"], host="0.0.0.0")
