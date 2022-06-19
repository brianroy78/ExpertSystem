import os
from configparser import ConfigParser

from database import get_session, set_settings, Base, Data
from database.tables import VariableTable, ValueTable, RuleTable


def insert_var(db, var_name: str, options: list[str]) -> list[ValueTable]:
    var = VariableTable(name=var_name, options=[ValueTable(name=op) for op in options])
    db.add(var)
    db.commit()
    return [ValueTable(variable=var, value=op) for op in var.options]


def insert_rule(db, premises, conclusions):
    db.add(RuleTable(premises=premises, conclusions=conclusions))
    db.commit()


def load():
    config = ConfigParser()
    config.read('settings.ini')
    set_settings(config['DEFAULT']['sqlalchemy.url'])
    # db_path = config['DEFAULT']['sqlalchemy.url'].split('/')[-1]
    # if os.path.exists(db_path):
    #     os.remove(db_path)
    # else:
    #     print("The db does not exist!")
    # Base.metadata.create_all(Data.ENGINE)
    with get_session() as session:
        pass
        # nationality_facts = insert_var(
        #     session,
        #     'nacionalidad',
        #     [
        #         'Boliviano',
        #         'Brasilero',
        #         'Peruano'
        #     ]
        # )
        # bolivian, brazilian, peruvian = nationality_facts
        # birth_place_facts = insert_var(
        #     session,
        #     'lugar de nacimiento',
        #     [
        #         'Santa Cruz de la Sierra',
        #         'Rio de Janeiro',
        #         'Lima'
        #     ]
        # )
        #
        # saint, river, lim = birth_place_facts
        #
        # insert_rule(session, [saint], [bolivian])
        # insert_rule(session, [river], [brazilian])
        # insert_rule(session, [lim], [peruvian])
