from typing import Generic, TypeVar, Callable, Iterable, Union, Dict, Any

ValueType = TypeVar('ValueType')
ReturnType = TypeVar('ReturnType')
Func = Callable[[ValueType], ReturnType]
ListFunc = Callable[[Iterable[ValueType]], ReturnType]


class LF(Generic[ValueType, ReturnType]):
    def __init__(self, value: Iterable[ValueType]):
        self.value: Iterable[ValueType] = value

    def apply(self, func: ListFunc) -> 'LF[ReturnType]':
        return LF(func(self.value))

    def map(self, func: Func) -> 'LF[ReturnType]':
        return LF(map(func, self.value))

    def filter(self, func: Func) -> 'LF[ValueType]':
        return LF(filter(func, self.value))
