"""Implements the 'refresh_Tokens' HTTP Cloud Function.

This module defines a Google Cloud Function for Refreshing Tokens of the .
"""
import base64
import firebase_admin
import functions_framework
import json
from firebase_admin import credentials, firestore
from flask import jsonify
import os

GCP_SERVICE_ACCOUNT_CERTIFICATE_BASE64 = os.getenv( "GCP_SERVICE_ACCOUNT_CERTIFICATE" )
if( GCP_SERVICE_ACCOUNT_CERTIFICATE_BASE64 is None ):
    raise KeyError( "Env var GCP_SERVICE_ACCOUNT_CERTIFICATE not found!" )

GCP_SERVICE_ACCOUNT_CERTIFICATE_DECODED_BYTES = \
    base64.b64decode(GCP_SERVICE_ACCOUNT_CERTIFICATE_BASE64)

GCP_SERVICE_ACCOUNT_CERTIFICATE_DECODED_STRING = \
    GCP_SERVICE_ACCOUNT_CERTIFICATE_DECODED_BYTES.decode('utf-8')

cred_dict = json.loads(GCP_SERVICE_ACCOUNT_CERTIFICATE_DECODED_STRING, strict=False)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

@functions_framework.http
def refresh_Tokens(request):
    """Refresh the available tokens in the Firestore database."""
    if db is None:
        return jsonify({"error": "No database available"}), 500
    doc_ref = db.collection("api-tokens").document("token-document")
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({"tokens": 100})
        return jsonify({"Tokens set to 100"}), 200
    else:
        return jsonify({"error": "No document available"}), 404
    
