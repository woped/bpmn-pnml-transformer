"""App file for starting and routing cloud functions when deploying inside a docker container."""

from flask import Flask, request
from health.main import get_health
from transform.main import post_transform

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_route():
    return get_health(request)

@app.route('/transform', methods=['POST'])
def transform_route():
    return post_transform(request)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
