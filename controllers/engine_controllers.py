from functools import partial
from uuid import uuid4

from flask import Blueprint, request

from app.basic import get_variable
from app.constants import EMPTY_VALUE_STR
from app.converter import from_table_to_model
from app.engine import infer
from app.models import Variable, Inference, Option
from app.utils import not_in
from controllers.controllers_utils import as_json
from database import get_session
from database.tables import QuotationTable, SelectedOptionTable

engine_blueprint = Blueprint('engine', __name__)

inferences: dict[str, Inference] = dict()


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
    final_response = as_json({'finished': True, 'conclusions': parse_facts(inferences[identifier])})
    inferences.pop(identifier, None)
    return final_response


@engine_blueprint.route('/inference/start', methods=['POST'])
def inference_start():
    quotation_id: str = request.json['quotation_id']
    rules, variables = from_table_to_model()
    if len(rules) == 0:
        return as_json({'finished': True, 'conclusions': []})
    identifier = str(uuid4())
    inferences[identifier] = Inference(rules, set(), variables, quotation_id)
    return as_json({'id': identifier, 'finished': False, 'variable': variable_to_dict(variables[0])})


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
        options = list(session.query(SelectedOptionTable). \
                       filter(SelectedOptionTable.quotation_id == quotation_id). \
                       order_by(SelectedOptionTable.order.desc()))
        session.add(SelectedOptionTable(
            order=len(options),
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
    inference: Inference = inferences[identifier]
    value_name: str = request.json['value_name']
    variable: Variable = inference.vars.pop(0)
    options: set[Option] = variable.options
    compare = is_equal_scalar if variable.is_scalar else is_equal_name
    value: Option = next(filter(partial(compare, value_name), options))
    if variable.is_scalar and value.value != EMPTY_VALUE_STR:
        value.scalar = value_name
    save_option(inference.quotation_id, value)
    rules, new_facts = infer(inference.rules, value)
    inference.facts |= new_facts
    inference.rules = rules
    concluded_vars: set[Variable] = set(map(get_variable, inference.facts))
    inference.vars = list(filter(partial(not_in, concluded_vars), inference.vars))

    if len(inference.vars) == 0:
        return finish(identifier)

    return as_json({'finished': False, 'variable': variable_to_dict(inference.vars[0])})
