from typing import Dict

from flask import Blueprint, request

from controllers.controllers_utils import as_json, return_ok
from database import get_session, Base
from database.serializer import unpack, query_all
from database.tables import VariableTable, OptionTable, RuleTable, ClientTable, QuotationTable, DeviceTable

main_blueprint = Blueprint('main', __name__)

tables: Dict[str, Base] = {
    'variable': VariableTable,
    'value': OptionTable,
    'rule': RuleTable,
    'client': ClientTable,
    'quotation': QuotationTable,
    'device': DeviceTable,
}


@main_blueprint.route('/insert', methods=['POST'])
def insert():
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
        base_class = tables[request.json['_type_']]
        base_query = session.query(base_class)
        for filter_ in request.json.get('_filters_', list()):
            attrib, value = filter_
            base_query.filter(getattr(base_class, attrib) == value)
        result = query_all(
            base_query,
            request.json.get('_relations_', [])
        )
    return as_json(result)
