"""App file for cloudfunctions when deploying inside a docker container."""

from flask import Flask, request
from health.main import get_health
from transform.main import post_transform
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
