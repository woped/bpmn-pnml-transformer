import flask
import functions_framework
from flask import jsonify

from transformer.bpmn.bpmn import BPMN
from transformer.transform_bpmn_to_petrinet.transform import transform_bpmn_to_petrinet


@functions_framework.http
def post_pnmltobpmn(request: flask.Request):
    bpmn_xml_content = request.form["xml"]
    bpmn = BPMN.from_xml(bpmn_xml_content)
    transformed_bpmn = transform_bpmn_to_petrinet(bpmn.process)
    return jsonify({"pnml": transformed_bpmn})
