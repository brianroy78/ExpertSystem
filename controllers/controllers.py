from typing import Dict

from flask import Blueprint, request

from controllers.controllers_utils import as_json, return_ok
from database import get_session, Base
from database.serializer import unpack, query_all
from database.tables import (
    VariableTable,
    OptionTable,
    RuleTable,
    ClientTable,
    QuotationTable,
    DeviceTable,
    SelectedOptionTable
)

main_blueprint = Blueprint('main', __name__)

tables: Dict[str, Base] = {
    'variable': VariableTable,
    'value': OptionTable,
    'rule': RuleTable,
    'client': ClientTable,
    'quotation': QuotationTable,
    'device': DeviceTable,
    'selected_option': SelectedOptionTable,
}


@main_blueprint.route('/insert', methods=['POST'])
def insert():
    with get_session() as db:
        obj = unpack(request.json, tables)
        db.add(obj)
        db.commit()
        id_ = obj.id
    return as_json({'id': id_})


@main_blueprint.route('/update', methods=['POST'])
def update():
    with get_session() as db:
        obj = unpack(request.json, tables)
        db.merge(obj)
        db.commit()
    return return_ok()


@main_blueprint.route('/delete', methods=['POST'])
def delete():
    with get_session() as db:
        db.delete(
            db.query(tables[request.json['_type_']]).
            get(request.json['id'])
        )
        db.commit()
    return return_ok()


@main_blueprint.route('/list', methods=['POST'])
def list_rows():
    with get_session() as db:
        base_class = tables[request.json['_type_']]
        base_query = db.query(base_class)
        for filter_ in request.json.get('_filters_', list()):
            attrib, value = filter_
            base_query = base_query.filter(getattr(base_class, attrib) == value)
        result = query_all(
            base_query,
            request.json.get('_relations_', [])
        )
    return as_json(result)
