"""."""
import flask
import functions_framework
from flask import jsonify
from transformer.models.bpmn.bpmn import BPMN
from transformer.transform_bpmn_to_petrinet.transform import (
    bpmn_to_st_net,
    bpmn_to_workflow_net,
)


@functions_framework.http
def post_bpmntopnml(request: flask.Request):
    """."""
    bpmn_xml_content = request.form["bpmn"]
    isTargetWorkflow = request.form.get("isTargetWorkflow", default=False, type=bool)
    bpmn = BPMN.from_xml(bpmn_xml_content)
    if isTargetWorkflow:
        transformed_pnml = bpmn_to_st_net(bpmn)
    else:
        transformed_pnml = bpmn_to_workflow_net(bpmn)
    return jsonify({"pnml": transformed_pnml.to_string()})
