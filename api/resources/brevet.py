# Import required libraries
from flask import Response, request
from flask_restful import Resource

# Import Brevet model from database/models.py
from database.models import Brevet

# Define the Brevet resource
class Brevet(Resource):
    # Define the GET method for retrieving a specific Brevet
    def get(self, id):
        # Retrieve the Brevet object with the given id and convert it to JSON
        brevet = Brevet.objects.get(id=id).to_json()
        # Return a JSON response with the Brevet object and a 200 status code
        return Response(brevet, mimetype="application/json", status=200)

    # Define the PUT method for updating a specific Brevet
    def put(self, id):
        # Get the JSON input from the request body
        input_json = request.json
        # Update the Brevet object with the given id using the input JSON
        Brevet.objects.get(id=id).update(**input_json)
        # Return an empty response with a 200 status code
        return '', 200

    # Define the DELETE method for deleting a specific Brevet
    def delete(self, id):
        # Delete the Brevet object with the given id
        Brevet.objects.get(id=id).delete()
        # Return an empty response with a 200 status code
        return '', 200

# Two options when returning responses:
#
# return Response(json_object, mimetype="application/json", status=200)
# return python_dict, 200
#
# Why would you need both?
# Flask-RESTful's default behavior:
# Return python dictionary and status code,
# it will serialize the dictionary as a JSON.
#
# MongoEngine's objects() has a .to_json() but not a .to_dict(),
# So when you're returning a brevet / brevets, you need to convert
# it from a MongoEngine query object to a JSON and send back the JSON
# directly instead of letting Flask-RESTful attempt to convert it to a
# JSON for you.
