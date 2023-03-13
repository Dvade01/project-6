"""
Resource: Brevet
"""
from flask import Response, request
from flask_restful import Resource
from database.models import Brevet, Checkpoint


class Brevet(Resource):
    def get(self, _id):

        # Retrieve the Brevet instance with the specified _id from the database and convert to JSON
        json_object = Brevet.objects.get(id=_id).to_json()

        # Return the JSON response with a content type of application/json and a status code of 200
        return Response(json_object, mimetype="application/json", status=200)

    def put(self, _id):

        # Retrieve the JSON payload of the PUT request
        input_json = request.json

        # Update the Brevet instance with the specified _id with the new data from the JSON payload
        Brevet.objects.get(id=_id).update(**input_json)

        # Return an empty response with a status code of 200
        return '', 200

    def delete(self, _id):

        # Delete the Brevet instance with the specified _id from the database
        Brevet.objects.get(id=_id).delete()

        # Return an empty response with a status code of 200
        return '', 200
