"""API to transform a given model into a selected direction."""

import flask
import functions_framework
import firebase_admin
from flask import jsonify

from transformer.models.bpmn.bpmn import BPMN
from transformer.models.pnml.pnml import Pnml
from transformer.transform_bpmn_to_petrinet.transform import (
    bpmn_to_st_net,
    bpmn_to_workflow_net,
)
from transformer.transform_petrinet_to_bpmn.transform import pnml_to_bpmn
from firebase_admin import credentials, firestore 

cred = credentials.Certificate("secrets/woped-422510-ff5224739dab.json")
app = firebase_admin.initialize_app(cred)
db = firestore.Client()

def check_tokens():
    """Check if there are tokens available in the Firestore database."""
    if db is None:
        raise Exception("No database available")
    doc_ref = db.collection("api-tokens").document("token-document")
    doc = doc_ref.get()

    if doc.exists:
        tokens = doc.to_dict().get("tokens",0)
        if tokens <= 0:
            raise Exception("No tokens available")
        
        else:
            doc_ref.update({"tokens": tokens-1})

    else:
        raise Exception("No document available")

@functions_framework.http
def post_transform(request: flask.Request):
    """HTTP based model transformation API.

    Process parameters to detect the type of posted model and the
    transformation direction.

    Args:
        request: A request with a parameter "direction" as transformation direction
        and a form with the xml model "bpmn" or "pnml".
    """
    check_tokens()
    
    transform_direction = request.args.get("direction")
    if transform_direction == "bpmntopnml":
        bpmn_xml_content = request.form["bpmn"]
        isTargetWorkflow = (
            request.form.get("isTargetWorkflow", "false").lower() == "true"
        )

        bpmn = BPMN.from_xml(bpmn_xml_content)
        if isTargetWorkflow:
            transformed_pnml = bpmn_to_workflow_net(bpmn)
        else:
            transformed_pnml = bpmn_to_st_net(bpmn)
        return jsonify({"pnml": transformed_pnml.to_string()})
    elif transform_direction == "pnmltobpmn":
        pnml_xml_content = request.form["pnml"]
        pnml = Pnml.from_xml_str(pnml_xml_content)
        transformed_bpmn = pnml_to_bpmn(pnml)
        return jsonify({"bpmn": transformed_bpmn.to_string()})
    else:
        raise Exception("Query params not supported")
