from typing import Callable


def add_department_questions(
        var_adder: Callable,
        rule_adder: Callable
):
    (
        cob,
        la_paz,
        el_alto,
        Trini,
        cochabamba,
        oruro,
        sucre,
        potosi,
        santa_cruz,
        tarija,
        no_city
    ) = var_adder(
        'city',
        '¿En qué ciudad se encuentra el lugar?',
        [
            'Cobija',
            'La Paz',
            'El Alto',
            'Trinidad',
            'Cochabamba',
            'Oruro',
            'Sucre',
            'Potosí',
            'Santa Cruz',
            'Tarija',
        ]
    )

    beni, chu, cocha, la, oru, pan, pot, santa, ta, no_department = var_adder(
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
        'department_latitude',
        '¿Cual es la latitud donde se encuentra el departamento?',
        [
            '11',
            '15',
            '18',
            '17',
            '20',
            '21.5',
            '16.5',
            '18',
            '19.5'
        ]
    )

    pan_lon, beni_lon, santa_lon, cocha_lon, chu_lon, ta_lon, la_lon, oru_lon, pot_lon, no_lon = var_adder(
        'department_longitude',
        '¿Cual es la longitud donde se encuentra el departamento?',
        [
            '-72',
            '-65',
            '-63',
            '-66',
            '-66',
            '-65',
            '-68',
            '-67',
            '66',
        ]
    )

    pan_al, beni_al, santa_al, cocha_al, chu_al, ta_al, la_al, oru_al, pot_al, no_al = var_adder(
        'department_altitude',
        '¿Cual es la altitud del departamento (metros)?',
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

    pan_hsp, beni_hsp, santa_hsp, cocha_hsp, chu_hsp, ta_hsp, la_hsp, oru_hsp, pot_hsp, no_department_hsp = var_adder(
        'department_hsp',
        '¿Cual es el HSP promedio del departamento?',
        [
            '4.8',
            '4.9',
            '4.8',
            '6',
            '4.7',
            '5.8',
            '5.8',
            '6',
            '6.3'
        ]
    )

    (
        pan_temp_min,
        beni_temp_min,
        santa_temp_min,
        cocha_temp_min,
        chu_temp_min,
        ta_temp_min,
        la_temp_min,
        oru_temp_min,
        pot_temp_min,
        no_department_temp_min
    ) = var_adder(
        'department_min_temp',
        '¿Cual es la temperatura mínima del departamento? (grado centígrados)',
        [
            '6',
            '18',
            '10',
            '4',
            '3',
            '5',
            '- 2',
            '- 5.8',
            '- 3.7'
        ]
    )

    (
        pan_temp_max,
        beni_temp_max,
        santa_temp_max,
        cocha_temp_max,
        chu_temp_max,
        ta_temp_max,
        la_temp_max,
        oru_temp_max,
        pot_temp_max,
        no_department_temp_max
    ) = var_adder(
        'department_max_temp',
        '¿Cual es la temperatura máxima del departamento? (grado centígrados)',
        [
            '28',
            '29',
            '34',
            '26',
            '23',
            '24',
            '15',
            '18.2',
            '17.1'
        ]
    )

    pan_hsd, beni_hsd, santa_hsd, cocha_hsd, chu_hsd, ta_hsd, la_hsd, oru_hsd, pot_hsd, no_department_hsd = var_adder(
        'department_hsd',
        '¿Cuantas son las horas de sol al día?',
        [
            '10',
            '10',
            '10',
            '8',
            '8',
            '8',
            '6',
            '6',
            '6'
        ]
    )

    rule_adder([pan], [pan_lat, pan_lon, pan_al, pan_hsp, pan_temp_min, pan_temp_max, pan_hsd])
    rule_adder([beni], [beni_lat, beni_lon, beni_al, beni_hsp, beni_temp_min, beni_temp_max, beni_hsd])
    rule_adder([santa], [santa_lat, santa_lon, santa_al, santa_hsp, santa_temp_min, santa_temp_max, santa_hsd])
    rule_adder([cocha], [cocha_lat, cocha_lon, cocha_al, cocha_hsp, cocha_temp_min, cocha_temp_max, cocha_hsd])
    rule_adder([chu], [chu_lat, chu_lon, chu_al, chu_hsp, chu_temp_min, chu_temp_max, chu_hsd])
    rule_adder([ta], [ta_lat, ta_lon, ta_al, ta_hsp, ta_temp_min, ta_temp_max, ta_hsd])
    rule_adder([la], [la_lat, la_lon, la_al, la_hsp, la_temp_min, la_temp_max, la_hsd])
    rule_adder([oru], [oru_lat, oru_lon, oru_al, oru_hsp, oru_temp_min, oru_temp_max, oru_hsd])
    rule_adder([pot], [pot_lat, pot_lon, pot_al, pot_hsp, pot_temp_min, pot_temp_max, pot_hsd])
