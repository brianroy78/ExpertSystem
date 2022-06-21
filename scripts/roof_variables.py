from typing import Callable


def add_roof_questions(
        var_adder: Callable,
        rule_adder: Callable,
        no_installation,
        skipped_installation
):
    flat, flat1, regular, tilted, no_roof = var_adder(
        'forma del techo',
        [
            'Plano',
            'Casi Plano (15º)',
            'Regular (30º)',
            'Inclinado (45º)'
        ]
    )

    north, east, south, west, no_direction = var_adder(
        'dirección del techo con relación al sol',
        [
            'Norte (0º)',
            'Este (90º)',
            'Sur (180º)',
            'Oeste (270º)'
        ]
    )

    small_roof, medium_roof, large_roof, no_size_roof = var_adder(
        'superficie base del techo/constucción',
        [
            'menos de 80 mtrs2 (8m x 10)',
            'menos de 150 mtrs2 (10m x 15m)',
            'más 150 mtrs2 (10m x 15m) '
        ]
    )

    tiles, calamine, brick, no_material_roof = var_adder(
        'material del techo',
        [
            'Tejas',
            'Calamina',
            'Ladrillo/Loza'
        ]
    )

    rule_adder([flat], [no_direction])

    _, _, _, no_shadow = var_adder(
        'Sombra en el techo',
        [
            'Sin Sombra',
            'Alguna Sombra',
            'Mucha Sombra'
        ]
    )

    rule_adder([no_installation], [no_roof, no_direction, no_shadow, no_size_roof, no_material_roof])
    rule_adder([skipped_installation], [no_roof, no_direction, no_shadow, no_size_roof, no_material_roof])
