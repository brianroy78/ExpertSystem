from functools import partial
from typing import Optional
from uuid import uuid4

from flask import Blueprint, request

from app.converter import from_table_to_model
from app.engine import infer, get_variables
from app.models import Variable, Inference, Rule, Fact, Value
from app.utils import first
from controllers.controllers_utils import as_json

engine_blueprint = Blueprint('engine', __name__)

inferences: dict[str, Inference] = dict()


def variable_to_dict(variable: Variable) -> dict:
    return {
        'id': variable.id,
        'name': variable.name,
        'options': [{'id': op.id, 'name': op.name} for op in variable.options]
    }


def finish(identifier: str):
    final_response = as_json({'finished': True, 'conclusions': parse_facts(inferences[identifier])})
    inferences.pop(identifier, None)
    return final_response


@engine_blueprint.route('/inference/start', methods=['POST'])
def inference_start():
    rules = from_table_to_model()
    if len(rules) == 0:
        return as_json({'finished': True, 'conclusions': []})
    variable = get_next_no_ignored_var(rules, set())
    identifier = str(uuid4())
    inferences[identifier] = Inference(set(rules), set(), set(), variable)
    return as_json({'id': identifier, 'finished': False, 'variable': variable_to_dict(variable)})


def parse_facts(inference: Inference) -> list[dict[str, str]]:
    return [{'variable_name': f.variable.name, 'value_name': f.value.name} for f in inference.facts]


def is_equal(target_value_id, value: Value) -> bool:
    return target_value_id == value.id


def get_fact(variable: Variable, value_id: int) -> Fact:
    return Fact(variable, first(filter(partial(is_equal, value_id), variable.options)))


def get_next_no_ignored_var(rules: set[Rule], ignored_vars: set[Variable]) -> Optional[Variable]:
    for rule in rules:
        for variable in get_variables(rule):
            if variable not in ignored_vars:
                return variable
    return None


@engine_blueprint.route('/inference/respond', methods=['POST'])
def inference_respond():
    identifier: str = request.json['id']
    inference: Inference = inferences[identifier]
    value_id: Optional[int] = request.json['value_id']
    variable: Variable = inference.current_var
    if value_id is None:
        inference.ignored_vars.add(variable)
    else:
        rules, new_facts = infer(inference.rules, get_fact(variable, value_id))
        inference.facts |= new_facts
        inference.rules = set(rules)
        if len(inference.rules) == 0:
            return finish(identifier)

    variable = get_next_no_ignored_var(inference.rules, inference.ignored_vars)
    if variable is None:
        return finish(identifier)
    inference.current_var = variable
    return as_json({'finished': False, 'variable': variable_to_dict(variable)})
