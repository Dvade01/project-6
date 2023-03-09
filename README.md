# UOCIS322 - Project 6 #

Author: David Moe

Email: dmoe7@uoregon.edu

Brevet time calculator with MongoDB, and a RESTful API!

This project was meant to accomplish the same goals as project-5 using the RESTful API instead of the database related code prior.
This required us to implement several files, model.py, flask_api.py, brevet.py, brevets.py, and a modification to the flask_brevets.py.
We had to remove config, and replace it with PORT and DEBUG values specified in the .env file we created. We removed the mypymongo.py file
and put all the API based stuff in the flask_brevets file which is meant to accomplish the same task. We use the MongoEngine to create a data schema for checkpoints and brevets.
Unfortunately I was unable to properly make this project work as intended, the display button seems to fail to work, and I will try to fix that as soon as possible.