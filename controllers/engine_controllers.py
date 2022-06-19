from functools import partial
from operator import not_, contains
from typing import Optional, Callable, Iterable
from uuid import uuid4

from flask import Blueprint, request

from app.basic import get_premises_variables, get_variable
from app.converter import from_table_to_model, premises_contains_variable
from app.custom_functions import reduce_ior
from app.engine import infer
from app.models import Variable, Inference, Rule, Fact, Value
from app.utils import not_in, compose
from controllers.controllers_utils import as_json

engine_blueprint = Blueprint('engine', __name__)

inferences: dict[str, Inference] = dict()


def variable_to_dict(variable: Variable) -> dict:
    return {
        'id': variable.id,
        'name': variable.name,
        'options': [
            {'id': op.id, 'name': op.name, 'order': op.order}
            for op in variable.options
        ]
    }


def parse_facts(inference: Inference) -> list[dict[str, str]]:
    return [{'variable_name': f.variable.name, 'value_name': f.value.name} for f in inference.facts]


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


def is_equal(target_value_id, value: Value) -> bool:
    return target_value_id == value.id


def get_fact(variable: Variable, value_id: int) -> Fact:
    return Fact(variable, next(filter(partial(is_equal, value_id), variable.options)))


def get_valid_var(is_valid: Callable, rule: Rule) -> Optional[Variable]:
    return next(filter(is_valid, get_premises_variables(rule)), None)


def get_next_no_ignored_var(rules: set[Rule], ignored_vars: set[Variable]) -> Optional[Variable]:
    is_valid = partial(not_in, ignored_vars)
    get_valid = partial(get_valid_var, is_valid)
    return next(map(get_valid, rules), None)


def is_orphan_by_rules(rules: set[Rule], variable: Variable) -> bool:
    return len(list(filter(partial(premises_contains_variable, variable), rules))) == 0


@engine_blueprint.route('/inference/respond', methods=['POST'])
def inference_respond() -> tuple:
    if request.json is None:
        return ()
    identifier: str = request.json['id']
    inference: Inference = inferences[identifier]
    value_id: Optional[int] = request.json['value_id']
    variable: Variable = inference.vars.pop(0)
    if value_id is None:
        variable_in_rule = partial(premises_contains_variable, variable)
        target_fathers: Iterable[Rule] = filter(variable_in_rule, inference.rules)
        variable_not_in_rule = compose(variable_in_rule, not_)
        inference.rules = set(filter(variable_not_in_rule, inference.rules))
        is_orphan = partial(is_orphan_by_rules, inference.rules)
        brothers: set[Variable] = reduce_ior(map(get_premises_variables, target_fathers))
        is_brother = partial(contains, brothers)

        def is_not_orphan_and_brother(variable_: Variable) -> bool:
            return not (is_orphan(variable_) and is_brother(variable_))

        inference.vars = list(filter(is_not_orphan_and_brother, inference.vars))
    else:
        rules, new_facts = infer(inference.rules, get_fact(variable, value_id))
        inference.facts |= new_facts
        inference.rules = rules
        concluded_vars = map(get_variable, inference.facts)
        inference.vars = list(filter(partial(not_in, concluded_vars), inference.vars))

        if len(inference.vars) == 0:
            return finish(identifier)

    return as_json({'finished': False, 'variable': variable_to_dict(inference.vars[0])})
