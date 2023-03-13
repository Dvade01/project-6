"""
Resource: Brevets
"""
from flask import Response, request
from flask_restful import Resource
from database.models import Brevet, Checkpoint


class Brevets(Resource):
    def get(self):
        # Query the database for all instances of the Brevet class and convert to JSON
        json_object = Brevet.objects().to_json()

        # Return the JSON response with a content type of application/json and a status code of 200
        return Response(json_object, mimetype="application/json", status=200)

    def post(self):
        # Retrieve the JSON payload of the POST request
        input_json = request.json

        # Create a new instance of the Brevet class using the JSON payload as constructor arguments
        # and save it to the database
        result = Brevet(**input_json).save()

        # Return a JSON response containing the _id of the newly created instance, with a status code of 200
        return {'_id': str(result.id)}, 200