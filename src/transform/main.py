"""API to transform a given model into a selected direction."""
import requests

import os
import flask
import functions_framework
from flask import jsonify

from transformer.models.bpmn.bpmn import BPMN
from transformer.models.pnml.pnml import Pnml
from transformer.transform_bpmn_to_petrinet.transform import (
    bpmn_to_st_net,
    bpmn_to_workflow_net,
)
from transformer.transform_petrinet_to_bpmn.transform import pnml_to_bpmn

CHECK_TOKEN_URL = 'https://europe-west3-woped-422510.cloudfunctions.net/checkTokens'
        
is_force_std_xml_active = os.getenv("FORCE_STD_XML")
if is_force_std_xml_active is None:
    raise Exception("Env variable is_force_std_xml_active not set!")


@functions_framework.http
def post_transform(request: flask.Request):
    """HTTP based model transformation API.

    Process parameters to detect the type of posted model and the
    transformation direction.

    Args:
        request: A request with a parameter "direction" as transformation direction
        and a form with the xml model "bpmn" or "pnml".
    """    
    try:
        response = requests.get(CHECK_TOKEN_URL)
        if response.status_code == 400:
            raise Exception("Token check not successful")
    except Exception:
        return jsonify({"error": "Token check not successful"}), 400
   
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
