from functools import partial
from typing import Optional, Callable
from uuid import uuid4

from flask import Blueprint, request

from app.converter import from_table_to_model
from app.engine import infer, get_variables
from app.models import Variable, Inference, Rule, Fact, Value
from app.utils import not_contains
from controllers.controllers_utils import as_json

engine_blueprint = Blueprint('engine', __name__)

inferences: dict[str, Inference] = dict()


def variable_to_dict(variable: Variable) -> dict:
    return {
        'id': variable.id,
        'name': variable.name,
        'options': [{'id': op.id, 'name': op.name} for op in variable.options]
    }


def parse_facts(inference: Inference) -> list[dict[str, str]]:
    return [{'variable_name': f.variable.name, 'value_name': f.value.name} for f in inference.facts]


def finish(identifier: str):
    final_response = as_json({'finished': True, 'conclusions': parse_facts(inferences[identifier])})
    inferences.pop(identifier, None)
    return final_response


@engine_blueprint.route('/inference/start', methods=['POST'])
def inference_start():
    rules, required = from_table_to_model()
    if len(rules) == 0:
        return as_json({'finished': True, 'conclusions': []})
    variable = get_next_no_ignored_var(rules, set())
    identifier = str(uuid4())
    inferences[identifier] = Inference(set(rules), set(), set(), required, variable, False)
    return as_json({'id': identifier, 'finished': False, 'variable': variable_to_dict(variable)})


def is_equal(target_value_id, value: Value) -> bool:
    return target_value_id == value.id


def get_fact(variable: Variable, value_id: int) -> Fact:
    return Fact(variable, next(filter(partial(is_equal, value_id), variable.options)))


def get_valid_var(is_valid: Callable, rule: Rule) -> Optional[Variable]:
    return next(filter(is_valid, get_variables(rule)), None)


def get_next_no_ignored_var(rules: set[Rule], ignored_vars: set[Variable]) -> Optional[Variable]:
    is_valid = partial(not_contains, ignored_vars)
    get_valid = partial(get_valid_var, is_valid)
    return next(map(get_valid, rules), None)


@engine_blueprint.route('/inference/respond', methods=['POST'])
def inference_respond():
    identifier: str = request.json['id']
    inference: Inference = inferences[identifier]
    value_id: Optional[int] = request.json['value_id']
    variable: Variable = inference.current_variable
    if value_id is None:
        inference.ignored_variables.add(variable)
    else:
        rules, new_facts = infer(inference.rules, get_fact(variable, value_id))
        inference.facts |= new_facts
        inference.rules = rules

        if len(inference.rules) == 0:
            return finish(identifier)

    variable = get_next_no_ignored_var(inference.rules, inference.ignored_variables)
    if variable is None and len(inference.required_variables) == 0:
        return finish(identifier)
    if variable is None and len(inference.required_variables) > 0:
        as_json({'finished': False, 'variable': variable_to_dict(inference.required_variables.pop())})
    inference.current_variable = variable
    return as_json({'finished': False, 'variable': variable_to_dict(variable)})
