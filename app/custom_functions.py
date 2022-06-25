from functools import reduce
from operator import or_
from typing import TypeVar, Iterable, Union

ValueType = TypeVar('ValueType')
ReturnType = TypeVar('ReturnType')

set_type = Union[set[ValueType], frozenset[ValueType]]


def reduce_or(elements: Iterable[Iterable[ValueType]]) -> set[ValueType]:
    return reduce(or_, elements, set())
