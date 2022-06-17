from typing import Dict

from flask import Blueprint, request

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


@main_blueprint.route('/insert', methods=['POST'])
def insert():
    id_ = None
    with get_session() as session:
        obj = unpack(request.json, tables)
        session.add(obj)
        session.commit()
        id_ = obj.id
    return as_json({'id': id_})


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
