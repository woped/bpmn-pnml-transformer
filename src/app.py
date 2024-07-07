"""App file for cloudfunctions when deploying inside a docker container."""

from flask import Flask, request
from health.main import get_health
from main import post_transform
from checkTokens.main import check_tokens
from refreshTokens.main import refresh_tokens
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_route():
    """Mapping route for health endpoint."""
    return get_health(request)

@app.route('/transform', methods=['POST'])
def transform_route():
    """Mapping route for transform endpoint."""
    return post_transform(request)

@app.route('/checkTokens', methods=['GET'])
def checkTokens_route():
    """Mapping route for checkTokens endpoint."""
    return check_tokens(request)

@app.route('/refreshTokens', methods=['GET'])
def refreshTokens_route():
    """Mapping route for refreshTokens endpoint."""
    return refresh_tokens(request)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
