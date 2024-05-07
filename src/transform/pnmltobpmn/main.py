"""."""
import flask
import functions_framework
from flask import jsonify
from transformer.models.pnml.pnml import Pnml
from transformer.transform_petrinet_to_bpmn.transform import pnml_to_bpmn


@functions_framework.http
def post_pnmltobpmn(request: flask.Request):
    """."""
    pnml_xml_content = request.form["pnml"]
    pnml = Pnml.from_xml_str(pnml_xml_content)
    transformed_bpmn = pnml_to_bpmn(pnml)
    return jsonify({"bpmn": transformed_bpmn.to_string()})
