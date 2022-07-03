from functools import partial
from operator import contains, not_
from typing import Optional
from uuid import uuid4

from flask import Blueprint, request

from app.basic import get_variable, copy_rule, get_variable_id, copy_inference
from app.constants import EMPTY_VALUE_STR
from app.converter import from_table_to_model, to_option, cut_branch
from app.engine import infer
from app.models import Variable, Inference, Option, Rule
from app.utils import not_in, compose
from controllers.controllers_utils import as_json, return_ok
from database import get_session
from database.tables import QuotationTable, SelectedOptionTable, OptionTable

engine_blueprint = Blueprint('engine', __name__)

inferences: dict[str, list[Inference]] = dict()


def variable_to_dict(variable: Variable) -> dict:
    return {
        'id': variable.id,
        'question': variable.question,
        'isScalar': variable.is_scalar,
        'options': [
            {'value': op.value, 'order': op.order}
            for op in variable.options
        ]
    }


def parse_facts(inference: Inference) -> list[dict[str, str]]:
    return [
        {
            'variable_name': f.variable.question,
            'value_name': f.value if not f.variable.is_scalar else str(f.scalar)
        } for f in inference.facts
    ]


def finish(identifier: str):
    final_response = as_json({'finished': True, 'conclusions': parse_facts(inferences[identifier][-1])})
    inferences.pop(identifier, None)
    return final_response


@engine_blueprint.route('/inference/start', methods=['POST'])
def inference_start():
    quotation_id: str = request.json['quotation_id']
    rules, variables = from_table_to_model()
    if len(rules) == 0:
        return as_json({'finished': True, 'conclusions': []})
    identifier = str(uuid4())
    inferences[identifier] = [Inference(rules, set(), variables, quotation_id)]
    return as_json({'id': identifier, 'finished': False, 'variable': variable_to_dict(variables[0])})


def equal_var_id(target_var_id: str, variable: Variable) -> bool:
    return variable.id == target_var_id


def get_selected_option_order(selected_option: SelectedOptionTable) -> int:
    return selected_option.order


def forward_to(inference: Inference, selected_option_id: int) -> Inference:
    cloned_rules: set[Rule] = set(map(copy_rule, inference.rules))
    with get_session() as db:
        quotation: QuotationTable = db.query(QuotationTable).get(inference.quotation_id)
        sorted_options = sorted(quotation.selected_options, key=get_selected_option_order)
        branch: Optional[Variable] = None
        for stored_option in sorted_options:
            option_table: OptionTable = stored_option.option
            variable_id: str = option_table.variable.id
            variable: Optional[Variable] = next(filter(partial(equal_var_id, variable_id), inference.vars), None)
            if variable is None:
                continue
            if stored_option.id == selected_option_id:
                branch = variable
            option: Option = to_option(stored_option, option_table, variable)
            rules, new_facts = infer(inference.rules, option)
            inference.rules = rules
            inference.facts |= new_facts
            concluded_vars: set[Variable] = set(map(get_variable, inference.facts))
            inference.vars = list(filter(partial(not_in, concluded_vars), inference.vars))

        if branch is not None:
            new_rules, new_vars = cut_branch(branch, cloned_rules)
            inference.rules.update(new_rules)
            inference.vars = new_vars + inference.vars
            unknowns = compose(get_variable, partial(contains, new_vars), not_)
            inference.facts = set(filter(unknowns, inference.facts))

            variable_ids: set[str] = set(map(get_variable_id, new_vars))
            option_ids: set[int] = {i[0] for i in
                                    db.query(OptionTable.id).filter(OptionTable.parent_id.in_(variable_ids))}
            db.query(SelectedOptionTable). \
                filter(SelectedOptionTable.quotation_id == inference.quotation_id). \
                filter(SelectedOptionTable.option_id.in_(option_ids)).delete()
            db.commit()
    return inference


@engine_blueprint.route('/inference/start/from', methods=['POST'])
def inference_start_from():
    quotation_id: str = request.json['quotation_id']
    selected_option_id: int = request.json['selected_option_id']
    rules, variables = from_table_to_model()
    if len(rules) == 0:
        return as_json({'finished': True, 'conclusions': []})
    identifier = str(uuid4())
    inference = forward_to(Inference(rules, set(), variables, quotation_id), selected_option_id)
    inferences[identifier] = [inference]
    return as_json({'id': identifier, 'finished': False, 'variable': variable_to_dict(inference.vars[0])})


def is_equal_name(target_value_name, value: Option) -> bool:
    return target_value_name == value.value


def is_equal_scalar(target_scalar, value: Option) -> bool:
    if target_scalar == EMPTY_VALUE_STR == value.value:
        return True
    if target_scalar != EMPTY_VALUE_STR and value.value != EMPTY_VALUE_STR:
        return True
    return False


def save_option(quotation_id: str, option: Option):
    with get_session() as session:
        options: list[tuple] = list(
            session.query(SelectedOptionTable.order).
            filter(SelectedOptionTable.quotation_id == quotation_id).
            order_by(SelectedOptionTable.order.asc())
        )
        for index, op in enumerate(options):
            if index != op[0]:
                order = index
                break
        else:
            order = len(options)

        session.add(SelectedOptionTable(
            order=order,
            scalar=option.scalar,
            quotation_id=quotation_id,
            option_id=option.id
        ))
        session.commit()


@engine_blueprint.route('/inference/respond', methods=['POST'])
def inference_respond() -> tuple:
    if request.json is None:
        return ()
    identifier: str = request.json['id']
    last_inference: Inference = inferences[identifier][-1]
    inference: Inference = copy_inference(last_inference)
    value_name: str = request.json['value_name']
    variable: Variable = inference.vars.pop(0)
    options: set[Option] = variable.options
    compare = is_equal_scalar if variable.is_scalar else is_equal_name
    value: Option = next(filter(partial(compare, value_name), options))
    if variable.is_scalar and value.value != EMPTY_VALUE_STR:
        value.scalar = value_name
    save_option(inference.quotation_id, value)
    new_rules, new_facts = infer(inference.rules, value)
    inference.facts |= new_facts
    concluded_vars: set[Variable] = set(map(get_variable, inference.facts))
    inference.vars = list(filter(partial(not_in, concluded_vars), inference.vars))
    inferences[identifier].append(inference)

    if len(inference.vars) == 0:
        return finish(identifier)

    return as_json({'finished': False, 'variable': variable_to_dict(inference.vars[0])})


@engine_blueprint.route('/inference/back', methods=['POST'])
def back_inference():
    identifier: str = request.json['id']
    versions = inferences[identifier]
    versions.pop()
    if len(versions) == 0:
        return as_json({'empty': True})
    return as_json({'empty': False, 'finished': False, 'variable': variable_to_dict(versions[-1].vars[0])})


@engine_blueprint.route('/inference/delete', methods=['POST'])
def delete_inference():
    if request.json is None:
        return ()
    identifier: str = request.json['id']
    inferences.pop(identifier, None)
    return return_ok()
