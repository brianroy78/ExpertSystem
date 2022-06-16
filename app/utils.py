from itertools import groupby
from typing import Generic, TypeVar, Callable, Iterable, Union, Any, Mapping

ValueType = TypeVar('ValueType')
ReturnType = TypeVar('ReturnType')
Func = Callable[[ValueType], ReturnType]
ListFunc = Callable[[Iterable[ValueType]], ReturnType]

IterableOrDict = Union[Iterable[ValueType], ValueType]


class LF(Generic[ValueType, ReturnType]):
    def __init__(self, value: IterableOrDict):
        self.value: IterableOrDict = value

    def apply(self, func: ListFunc) -> 'LF[ReturnType]':
        return LF(func(self.value))

    def map(self, func: Func) -> 'LF[ReturnType]':
        return LF(map(func, self.value))

    def filter(self, func: Func) -> 'LF[ValueType]':
        return LF(filter(func, self.value))


def remove_from_frozen(elements: frozenset, element) -> frozenset:
    clone: set = set(elements)
    clone.remove(element)
    return frozenset(clone)


def first(elements: Union[frozenset, set]):
    return next(iter(elements))


def group_by(key: Callable, iterable: Iterable) -> dict:
    result = dict()
    for key, groups in groupby(iterable, key):
        if key not in result:
            result[key] = list()
        result[key].extend(list(groups))
    return result


def compose(*callables: Callable) -> Callable:
    callables_ = list(callables)

    def composed(*args, **kwargs) -> ReturnType:
        result = callables_.pop(0)(*args, **kwargs)
        for func in callables_:
            result = func(result)
        return result

    return composed
