import os
from configparser import ConfigParser
from functools import partial
from typing import Callable, Iterable, Optional

from app.constants import EMPTY_VALUE_STR
from database import get_session, set_settings, Base, Data
from database.tables import VariableTable, OptionTable, RuleTable, ClientTable
from scripts.department_variables import add_department_questions
from scripts.roof_variables import add_roof_questions


def insert_var(db, id_: str, question: str, options: list[str], is_scalar: bool = False) -> list[OptionTable]:
    var = VariableTable(
        id=id_,
        question=question,
        is_scalar=is_scalar,
        options=[
            OptionTable(value=op, order=index) for index, op in enumerate(options)
        ])
    var.options.append(OptionTable(value=EMPTY_VALUE_STR, order=len(options)))
    db.add(var)
    return var.options


def insert_rule(db, premises, conclusions, formula: Optional[str] = None):
    db.add(RuleTable(premises=premises, conclusions=conclusions, formula=formula))


def load():
    config = ConfigParser()
    config.read('settings.ini')
    set_settings(config['DEFAULT']['sqlalchemy.url'])
    db_path = config['DEFAULT']['sqlalchemy.url'].split('/')[-1]
    if os.path.exists(db_path):
        os.remove(db_path)
    else:
        print("The db does not exist!")
    Base.metadata.create_all(Data.ENGINE)
    with get_session() as session:
        insert = partial(insert_var, session)
        insert_rule_ = partial(insert_rule, session)
        on_grid, off_grid, _ = insert(
            'system_type',
            '¿Que tipo de sistema és?',
            ['ON GRID', 'OFF GRID']
        )

        yes_on_grid, no_on_grid, _ = insert(
            'is_on_grid',
            '¿El lugar tiene conección a la red eléctica?',
            ['Sí', 'No']
        )

        insert(
            'is_pumping_system',
            '¿Es un sistema de bombeo?',
            ['Sí', 'No']
        )

        insert_rule_([yes_on_grid], [on_grid])
        insert_rule_([no_on_grid], [off_grid])

        # insert(
        #     'consumo eléctrico promedio por día en Primavera/Verano',
        #     [
        #         'Entre 5KWH - 10KWH',
        #         'Entre 10KWH - 15KWH',
        #         'Entre 15KWH - 20KWH',
        #         'Entre 20KWH - 25KWH',
        #         'Entre 25KWH - 30KWH',
        #         'Entre 30KWH - 35KWH',
        #     ]
        # )
        #
        # insert(
        #     'consumo eléctrico promedio por día en Otoño/Invierno',
        #     [
        #         'Entre 5KWH - 10KWH',
        #         'Entre 10KWH - 15KWH',
        #         'Entre 15KWH - 20KWH',
        #         'Entre 20KWH - 25KWH',
        #         'Entre 25KWH - 30KWH',
        #         'Entre 30KWH - 35KWH',
        #     ]
        # )
        cep, empty_cep = insert(
            'average_electrical_consumption',
            '¿Cuanto es el consumo eléctrico promedio al año (KWH)?',
            ['cep'], True
        )

        crep, empty_crep = insert(
            'real_average_electrical_consumption',
            '¿Cuanto es el consumo real eléctrico promedio al año (KWH)?',
            ['crep'], True
        )

        insert_rule_([cep], [crep], 'average_electrical_consumption/2')

        high, medium, low, no_classification = insert(
            'classification_average_electrical_consumption',
            '¿Cual es la clasificacion del eléctrico promedio al año (KWH)?',
            ['Alto', 'Medio', 'Bajo'], True
        )

        insert_rule_([cep], [high], '')


        installation_required, no_installation, skipped_installation = insert(
            'require_installation',
            '¿Require servicio de instalación?',
            ['Sí', 'No']
        )

        add_roof_questions(
            insert,
            insert_rule_,
            no_installation,
            skipped_installation
        )

        add_department_questions(insert, insert_rule_)

        session.add(
            ClientTable(
                name='Test',
                last_name='Name',
                phone_number='12345678',
                email='address@server.com'
            )
        )

        session.commit()
