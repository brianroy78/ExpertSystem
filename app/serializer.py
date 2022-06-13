from typing import Union, List, Dict, Any

from sqlalchemy.orm import Query
from sqlalchemy.orm.collections import InstrumentedList

from database import Base

Target = Dict[str, Any]


def unpack(target: Union[List[Target], Target], tables_dict: Dict[str, Base]) -> Union[List[Base], Base]:
    if type(target) is list:
        return [unpack(sub_target, tables_dict) for sub_target in target]
    type_: Base = tables_dict[target.pop('__type__')]
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


def get_relation(obj: Base, relation_name: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    relation_definition = getattr(obj, relation_name)
    if type(relation_definition) is InstrumentedList:
        return [
            sqlalchemy_object_to_dict(sub_item)
            for sub_item in getattr(obj, relation_name)
        ]


def map_one(obj: Base, relations: List[Dict[str, Any]]) -> Dict:
    result_relations: Dict = dict()
    for relation_data in relations:
        relation_name: str = relation_data['__relation_name__']
        if '__relations__' in relation_data:
            result_relations[relation_name] = [
                map_one(sub_item, relation_data['__relations'])
                for sub_item in getattr(obj, relation_name)
            ]
        else:
            result_relations[relation_name] = get_relation(obj, relation_name)
    item_result: dict = sqlalchemy_object_to_dict(obj)
    item_result.update(result_relations)
    return item_result


def query_all(query: Query, relations: List[Dict[str, Any]]) -> list:
    return [map_one(obj, relations) for obj in query]
