import pickle
from typing import Dict, List, Set

from flask import Blueprint, request

from app.engine import infer
from app.models import Rule, Fact, Variable, Value, Inference
from app.serializer import unpack, query_all
from controllers.controllers_utils import as_json, return_ok
from database import get_session, Base
from database.tables import VariableTable, ValueTable, RuleTable, FactTable

main_blueprint = Blueprint('main', __name__)

tables: Dict[str, Base] = {
    'variable': VariableTable,
    'fact': FactTable,
    'value': ValueTable,
    'rule': RuleTable,
}


@main_blueprint.route('/', methods=['GET'])
def main():
    return '<H1>Hello World</H1>'


@main_blueprint.route('/insert', methods=['POST'])
def insert():
    with get_session() as session:
        obj = unpack(request.json, tables)
        session.add(obj)
        session.commit()
    return return_ok()


@main_blueprint.route('/list', methods=['POST'])
def list_rows():
    with get_session() as session:
        type_: str = request.json['_type_']
        relations = request.json.get('_relations_', [])
        result = query_all(
            session.query(tables[type_]),
            relations
        )
    return as_json(result)


@main_blueprint.route('/inference/get/rules', methods=['POST'])
def inference_get_rules():
    with get_session() as session:
        variables_dict: Dict[int, Variable] = dict()
        values_dict: Dict[int, Value] = dict()
        for variable in session.query(VariableTable):
            variable: VariableTable
            options = list()
            for op in variable.options:
                op: ValueTable
                value = Value(op.id, op.name) if op.id not in values_dict else values_dict[op.id]
                values_dict[op.id] = value
                options.append(value)
            variables_dict[variable.id] = Variable(
                variable.id,
                variable.name,
                frozenset(options)
            )
        rules: List[Rule] = list()
        for rule in session.query(RuleTable):
            rule: RuleTable
            if rule.statement is None:
                continue
            premises = list()
            for premise in rule.premises:
                premise: FactTable
                premises.append(Fact(
                    variables_dict[premise.variable.id],
                    values_dict[premise.value.id]
                ))
            rules.append(Rule(
                set(premises),
                Fact(
                    variables_dict[rule.statement.variable.id],
                    values_dict[rule.statement.value.id]
                )
            ))

    inference = Inference(rules, set(), set(), set(), None)
    serialized = pickle.dumps(inference).decode('latin1')

    return as_json(serialized)


def has_ignored_var(rule: Rule, ignored_vars: Set[Variable]) -> bool:
    for premise in rule.premises:
        if premise.variable in ignored_vars:
            return True
    return False


@main_blueprint.route('/inference/get/variable', methods=['POST'])
def inference_get_variable():
    encoded = request.json.encode('latin1')
    inference: Inference = pickle.loads(encoded)
    if len(inference.rules) == 0:
        return as_json({'state': pickle.dumps(inference).decode('latin1')})

    while len(inference.rules) > 0:
        rule: Rule = inference.rules[-1]
        if has_ignored_var(rule, inference.ignored_vars):
            inference.ignored_rules |= inference.rules.pop()
            continue
        for premise in set(rule.premises):
            variable: Variable = premise.variable
            inference.current_var = variable
            return as_json({
                'state': pickle.dumps(inference).decode('latin1'),
                'variable': {
                    'id': variable.id,
                    'name': variable.name,
                    'options': [{'id': op.id, 'name': op.name} for op in variable.options]
                }
            })
    if len(inference.rules) == 0:
        return {'state': pickle.dumps(inference).decode('latin1')}


@main_blueprint.route('/inference/respond', methods=['POST'])
def inference_respond():
    inference: Inference = pickle.loads(request.json['state'].encode('latin1'))
    actual_value_id: dict = request.json['value_id']
    if actual_value_id is None:
        inference.ignored_vars.add(inference.current_var)
        inference.ignored_rules.add(inference.rules.pop())
        return as_json(pickle.dumps(inference).decode('latin1'))
    actual_value = list(filter(lambda x: x.id == actual_value_id, inference.current_var.options))[0]
    actual_fact = Fact(inference.current_var, actual_value)
    rules, new_facts = infer(inference.rules, actual_fact)
    inference.facts |= new_facts
    inference.rules = rules
    return as_json(pickle.dumps(inference).decode('latin1'))


@main_blueprint.route('/parse/facts', methods=['POST'])
def parse_facts():
    inference: Inference = pickle.loads(request.json.encode('latin1'))
    return as_json([
        f'{fact.variable.name} => {fact.value.name}'
        for fact in inference.facts
    ])
