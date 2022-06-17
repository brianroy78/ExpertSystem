from functools import partial
from typing import Optional
from uuid import uuid4

from flask import Blueprint, request

from app.converter import from_table_to_model
from app.engine import infer
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


def return_variable(identifier: str, variable: Variable):
    return as_json({'id': identifier, 'finished': False, 'variable': variable})


@engine_blueprint.route('/inference/start', methods=['POST'])
def inference_start():
    rules = from_table_to_model()
    if len(rules) == 0:
        return as_json({'finished': True, 'conclusions': []})
    variable = get_first_variable(rules)
    identifier = str(uuid4())
    inferences[identifier] = Inference(set(rules), set(), set(), set(), variable)
    return as_json({'id': identifier, 'finished': False, 'variable': variable_to_dict(variable)})


def parse_facts(inference: Inference) -> list[dict[str, str]]:
    return [{'variable_name': f.variable.name, 'value_name': f.value.name} for f in inference.facts]


def has_ignored_var(rule: Rule, ignored_vars: set[Variable]) -> bool:
    for premise in rule.premises:
        if premise.variable in ignored_vars:
            return True
    return False


def ignore_variable(inference: Inference) -> Inference:
    for rule in set(inference.rules):
        if has_ignored_var(rule, inference.ignored_vars):
            inference.rules.remove(rule)
            inference.ignored_rules.add(rule)
    return inference


def is_equal(target_value_id, value: Value) -> bool:
    return target_value_id == value.id


def get_fact(variable: Variable, value_id: int) -> Fact:
    return Fact(variable, first(filter(partial(is_equal, value_id), variable.options)))


def all_rules(inference: Inference) -> set[Rule]:
    return inference.rules | inference.ignored_rules


def get_first_variable(rules: set[Rule]) -> Variable:
    return first(first(rules).premises).variable


@engine_blueprint.route('/inference/respond', methods=['POST'])
def inference_respond():
    inference: Inference = inferences[request.json['id']]
    value_id: Optional[int] = request.json['value_id']
    variable: Variable = inference.current_var
    if value_id is None:
        inference.ignored_vars.add(variable)
        inference = ignore_variable(inference)
    else:
        rules, new_facts = infer(all_rules(inference), get_fact(variable, value_id))
        inference.facts |= new_facts
        inference.rules = set(rules)

    if len(inference.rules) == 0:
        return as_json({'finished': True, 'conclusions': parse_facts(inference)})
    variable = get_first_variable(inference.rules)
    inference.current_var = variable
    return as_json({'finished': False, 'variable': variable_to_dict(variable)})
