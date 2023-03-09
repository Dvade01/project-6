"""
Resource: Brevets
"""
from flask import Response, request
from flask_restful import Resource

# Import the Brevet model from database/models.py
from database.models import Brevet

class Brevets(Resource):
    def get(self):
        # Get all Brevets from the database and convert to JSON
        json_object = Brevet.objects().to_json()
        
        # Return the JSON data with a 200 status code and application/json mimetype
        return Response(json_object, mimetype="application/json", status=200)

    def post(self):
        # Get the input data from the request as JSON
        input_json = request.json
        
        # Save the Brevet to the database and get the resulting ID
        result = Brevet(**input_json).save()
        
        # Return the ID of the saved Brevet with a 200 status code
        return {'_id': str(result.id)}, 200
