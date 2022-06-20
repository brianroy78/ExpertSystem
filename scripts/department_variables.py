from typing import Callable


def add_department_questions(
        var_adder: Callable,
        rule_adder: Callable
):
    var_adder(
        'departamento',
        [
            'Beni',
            'Chuquisaca',
            'Cochabamba',
            'La Paz',
            'Oruro',
            'Pando',
            'Potosí',
            'Santa Cruz',
            'Tarija',
        ]
    )
