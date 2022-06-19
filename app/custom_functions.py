from functools import reduce
from operator import ior
from typing import TypeVar, Iterable, Union

ValueType = TypeVar('ValueType')
ReturnType = TypeVar('ReturnType')

set_type = Union[set[ValueType], frozenset[ValueType]]


def reduce_ior(elements: Iterable[set_type]) -> set[ValueType]:
    return reduce(ior, elements, set())
