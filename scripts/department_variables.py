from typing import Callable


def add_department_questions(
        var_adder: Callable,
        rule_adder: Callable
):
    var_adder(
        'department',
        '¿En qué departamento se encuentra el lugar?',
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
