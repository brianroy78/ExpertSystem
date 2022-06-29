from typing import Callable


def add_department_questions(
        var_adder: Callable,
        rule_adder: Callable
):
    beni, chu, cocha, la, oru, pan, po, santa, ta, no_department = var_adder(
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

    pan_lat, beni_lat, santa_lat, cocha_lat, chu_lat, ta_lat, la_lat, oru_lat, pot_lat, no_lat = var_adder(
        'department',
        '¿Cual es la Altitud del departamento?',
        [
            '235',
            '155',
            '416',
            '2558',
            '2554',
            '1854',
            '3625',
            '3735',
            '4090'
        ]
    )
