from typing import Union, List, Dict, Any, Callable

from sqlalchemy.orm import Query
from sqlalchemy.orm.collections import InstrumentedList

from app.engine import curry
from database import Base

Target = Dict[str, Any]


def unpack(target: Union[List[Target], Target], tables_dict: Dict[str, Base]) -> Union[List[Base], Base]:
    if type(target) is list:
        return [unpack(sub_target, tables_dict) for sub_target in target]
    type_: Base = tables_dict[target.pop('_type_')]
    target: Target
    relations_key: List[str] = list(filter(lambda key: is_relation(target[key]), target))
    target_flat_attrib = {key: target[key] for key in target if key not in relations_key}
    obj: type_ = type_(**target_flat_attrib)
    for relation_key in relations_key:
        if type(target[relation_key]) is list:
            for sub_target in target[relation_key]:
                sub_target_processed = unpack(sub_target, tables_dict)
                getattr(obj, relation_key).append(sub_target_processed)
        if type(target[relation_key]) is dict:
            setattr(obj, relation_key, unpack(target[relation_key], tables_dict))
    return obj


def is_relation(obj: Any) -> bool:
    return type(obj) in [list, dict]


def sqlalchemy_object_to_dict(obj) -> dict:
    result: dict = obj.__dict__
    if '_sa_instance_state' in result:
        result.pop('_sa_instance_state')
    return result


def get_relation(obj: Base, relation_name: str, transform: Callable) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    relation_definition = getattr(obj, relation_name)
    if type(relation_definition) is InstrumentedList:
        return [
            transform(sub_item)
            for sub_item in relation_definition
        ]
    return transform(relation_definition)


def map_one(relations: List[Dict[str, Any]], obj: Base) -> Dict:
    result_relations: Dict = dict()
    for relation_data in relations:
        relation_name: str = relation_data['_relation_name_']
        transform = curry(map_one,
                          relation_data['_relations_']) if '_relations_' in relation_data else sqlalchemy_object_to_dict
        result_relations[relation_name] = get_relation(obj, relation_name, transform)
    item_result: dict = sqlalchemy_object_to_dict(obj)
    item_result.update(result_relations)
    return item_result


def query_all(query: Query, relations: List[Dict[str, Any]]) -> list:
    return [map_one(relations, obj) for obj in query]
