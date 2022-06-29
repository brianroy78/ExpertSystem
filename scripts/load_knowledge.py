import os
from configparser import ConfigParser
from functools import partial
from typing import Callable, Iterable, Optional

from app.constants import EMPTY_VALUE_STR
from database import get_session, set_settings, Base, Data
from database.tables import VariableTable, OptionTable, RuleTable, ClientTable
from scripts.department_variables import add_department_questions
from scripts.insert_devices import insert_devices
from scripts.roof_variables import add_roof_questions


def insert_variable(db, id_: str, question: str, options: list[str], is_scalar: bool = False) -> list[OptionTable]:
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


def insert_rule_using(db, premises, conclusions, formula: Optional[str] = None):
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
        insert_var = partial(insert_variable, session)
        insert_rule = partial(insert_rule_using, session)
        on_grid, off_grid, _ = insert_var(
            'system_type',
            '¿Que tipo de sistema és?',
            ['ON GRID', 'OFF GRID']
        )

        yes_on_grid, no_on_grid, _ = insert_var(
            'is_on_grid',
            '¿El lugar tiene conección a la red eléctica?',
            ['Sí', 'No']
        )

        insert_var(
            'is_pumping_system',
            '¿Es un sistema de bombeo?',
            ['Sí', 'No']
        )

        insert_rule([yes_on_grid], [on_grid])
        insert_rule([no_on_grid], [off_grid])

        cep, empty_cep = insert_var(
            'average_electrical_consumption',
            '¿Cuanto es el consumo eléctrico promedio al año (KWH)?',
            ['cep'], True
        )

        high, medium, low, no_classification = insert_var(
            'classification_average_electrical_consumption',
            '¿Cual es la clasificacion del eléctrico promedio al año (KWH)?',
            ['Alto', 'Medio', 'Bajo']
        )

        insert_rule([cep], [high], f''' \
        "{low.value}" if 10 < average_electrical_consumption < 50 else \
        "{medium.value}" if 50 < average_electrical_consumption < 100 else \
        "{high.value}"
        ''')

        insert_rule([off_grid], [empty_cep, no_classification])

        installation_required, no_installation, skipped_installation = insert_var(
            'require_installation',
            '¿Require servicio de instalación?',
            ['Sí', 'No']
        )

        add_roof_questions(
            insert_var,
            insert_rule,
            no_installation,
            skipped_installation
        )

        add_department_questions(insert_var, insert_rule)

        session.add(
            ClientTable(
                name='Test',
                last_name='Name',
                phone_number='12345678',
                email='address@server.com'
            )
        )

        session.add(
            ClientTable(
                name='Pedro',
                last_name='Yupanki',
                phone_number='12345678',
                email='address@server.com'
            )
        )

        session.add(
            ClientTable(
                name='Jasmani',
                last_name='Campos',
                phone_number='12345678',
                email='address@server.com'
            )
        )
        insert_devices(session)
        session.commit()
