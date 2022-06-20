from functools import partial
from uuid import uuid4

from flask import Blueprint, request

from app.basic import get_variable
from app.converter import from_table_to_model
from app.engine import infer
from app.models import Variable, Inference, Value
from app.utils import not_in
from controllers.controllers_utils import as_json

engine_blueprint = Blueprint('engine', __name__)

inferences: dict[str, Inference] = dict()


def variable_to_dict(variable: Variable) -> dict:
    return {
        'name': variable.name,
        'options': [
            {'name': op.name, 'order': op.order}
            for op in variable.options
        ]
    }


def parse_facts(inference: Inference) -> list[dict[str, str]]:
    return [{'variable_name': f.variable.name, 'value_name': f.name} for f in inference.facts]


def finish(identifier: str):
    final_response = as_json({'finished': True, 'conclusions': parse_facts(inferences[identifier])})
    inferences.pop(identifier, None)
    return final_response


@engine_blueprint.route('/inference/start', methods=['POST'])
def inference_start():
    rules, variables = from_table_to_model()
    if len(rules) == 0:
        return as_json({'finished': True, 'conclusions': []})
    identifier = str(uuid4())
    inferences[identifier] = Inference(rules, set(), variables)
    return as_json({'id': identifier, 'finished': False, 'variable': variable_to_dict(variables[0])})


def is_equal_name(target_value_name, value: Value) -> bool:
    return target_value_name == value.name


@engine_blueprint.route('/inference/respond', methods=['POST'])
def inference_respond() -> tuple:
    if request.json is None:
        return ()
    identifier: str = request.json['id']
    inference: Inference = inferences[identifier]
    value_name: str = request.json['value_name']
    options: set[Value] = inference.vars.pop(0).options
    value: Value = next(filter(partial(is_equal_name, value_name), options))
    rules, new_facts = infer(inference.rules, value)
    inference.facts |= new_facts
    inference.rules = rules
    concluded_vars: set[Variable] = set(map(get_variable, inference.facts))
    inference.vars = list(filter(partial(not_in, concluded_vars), inference.vars))

    if len(inference.vars) == 0:
        return finish(identifier)

    return as_json({'finished': False, 'variable': variable_to_dict(inference.vars[0])})
