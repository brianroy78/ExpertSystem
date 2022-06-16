import pickle
from typing import Dict, Set, Optional
from uuid import uuid4

from flask import Blueprint, request

from app.converter import from_table_to_model
from app.engine import infer
from app.models import Rule, Fact, Variable, Inference
from app.utils import first
from controllers.controllers_utils import as_json, return_ok
from database import get_session, Base
from database.serializer import unpack, query_all
from database.tables import VariableTable, ValueTable, RuleTable, FactTable, ClientTable, InferenceTable

main_blueprint = Blueprint('main', __name__)

tables: Dict[str, Base] = {
    'variable': VariableTable,
    'fact': FactTable,
    'value': ValueTable,
    'rule': RuleTable,
    'client': ClientTable,
    'inference': InferenceTable
}

inferences: dict[str, Inference] = dict()


@main_blueprint.route('/insert', methods=['POST'])
def insert():
    with get_session() as session:
        session.add(unpack(request.json, tables))
        session.commit()
    return return_ok()


@main_blueprint.route('/update', methods=['POST'])
def update():
    with get_session() as session:
        obj = unpack(request.json, tables)
        session.merge(obj)
        session.commit()
    return return_ok()


@main_blueprint.route('/list', methods=['POST'])
def list_rows():
    with get_session() as session:
        result = query_all(
            session.query(tables[request.json['_type_']]),
            request.json.get('_relations_', [])
        )
    return as_json(result)


def variable_to_dict(variable: Variable) -> dict:
    return {
        'id': variable.id,
        'name': variable.name,
        'options': [{'id': op.id, 'name': op.name} for op in variable.options]
    }


@main_blueprint.route('/inference/start', methods=['POST'])
def inference_start():
    rules = from_table_to_model()
    if len(rules) == 0:
        return as_json({'finished': True, 'conclusions': []})
    variable = first(first(rules).premises).variable
    inference = Inference(rules, set(), set(), set(), variable)
    identifier = str(uuid4())
    inferences[identifier] = inference
    return as_json({'id': identifier, 'finished': False, 'variable': variable_to_dict(variable)})


def has_ignored_var(rule: Rule, ignored_vars: Set[Variable]) -> bool:
    for premise in rule.premises:
        if premise.variable in ignored_vars:
            return True
    return False


def parse_facts(inference):
    return [f'{fact.variable.name} => {fact.value.name}' for fact in inference.facts]


@main_blueprint.route('/inference/respond', methods=['POST'])
def inference_respond():
    inference: Inference = inferences[request.json['id']]
    actual_value_id: dict = request.json['value_id']
    if actual_value_id is None:
        inference.ignored_vars.add(inference.current_var)
        for rule in set(inference.rules):
            if has_ignored_var(rule, inference.ignored_vars):
                inference.rules.remove(rule)
                inference.ignored_rules.add(rule)
    else:
        actual_value = list(filter(lambda x: x.id == actual_value_id, inference.current_var.options))[0]
        actual_fact = Fact(inference.current_var, actual_value)
        rules, new_facts = infer(set(inference.rules) | inference.ignored_rules, actual_fact)
        inference.facts |= new_facts
        inference.rules = set(rules)

    if len(inference.rules) == 0:
        return as_json({'finished': True, 'conclusions': parse_facts(inference)})
    variable = first(first(inference.rules).premises)
    inference.current_var = variable
    return as_json({'finished': False, 'variable': variable_to_dict(variable)})
