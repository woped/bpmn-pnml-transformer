"""Implements the 'get_health' HTTP Cloud Function.

This module defines a Google Cloud Function for responding to HTTP requests
with the health status of the service, indicating if it's operational.
"""

import functions_framework
from flask import jsonify

@functions_framework.http
def get_health(request):
    """HTTP Cloud Function.

    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    health_status = {
        "healthy" : True
    }

    if request and request.args:
        if "message" in request.args:
            health_status["message"] = request.args["message"]
        else:
            error = {
                "code" : 400,
                "message": "Invalid parameter provided.",
            }
            return jsonify(error), error["code"]


    return jsonify(health_status)
