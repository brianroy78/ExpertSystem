import os
from configparser import ConfigParser

from database import get_session, set_settings, Base, Data
from database.tables import VariableTable, ValueTable, RuleTable, FactTable


def insert_var(db, var_name: str, options: list[str], required=False) -> list[FactTable]:
    var = VariableTable(name=var_name, options=[ValueTable(name=op) for op in options], required=required)
    db.add(var)
    return [FactTable(variable=var, value=op) for op in var.options]


def insert_rule(db, premises, conclusions):
    db.add(RuleTable(premises=premises, conclusions=conclusions))


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
        system_type = insert_var(
            session,
            'tipo de sistema',
            ['ON GRID', 'OFF GRID', 'Bombeo']
        )
        on_grid, off_grid, pumping = system_type
        yes_on_grid, no_on_grid = insert_var(
            session,
            'el lugar tiene conección a la red eléctica',
            ['Sí', 'No']
        )

        insert_rule(session, [yes_on_grid], [on_grid])
        insert_rule(session, [no_on_grid], [off_grid])

        hot_days_consumption = insert_var(
            session,
            'consumo eléctrico promedio por día en Primavera/Verano',
            [
                'Entre 5KWH - 10KWH',
                'Entre 10KWH - 15KWH',
                'Entre 15KWH - 20KWH',
                'Entre 20KWH - 25KWH',
                'Entre 25KWH - 30KWH',
                'Entre 30KWH - 35KWH',
            ],
            True
        )

        cold_days_consumption = insert_var(
            session,
            'consumo eléctrico promedio por día en Otoño/Invierno',
            [
                'Entre 5KWH - 10KWH',
                'Entre 10KWH - 15KWH',
                'Entre 15KWH - 20KWH',
                'Entre 20KWH - 25KWH',
                'Entre 25KWH - 30KWH',
                'Entre 30KWH - 35KWH',
            ],
            True
        )

        session.commit()
