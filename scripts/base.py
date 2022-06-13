import pickle
from typing import Set, List

import yaml

from models import Rule, Variable, Value, Fact


def get_rules() -> List[Rule]:
    # with open('base de conocimiento.yaml', 'r') as file:
    #     # rules = yaml.load(file.read(), Loader=yaml.SafeLoader)
    #     rules = pickle.load(file)
    # return rules
    # values
    system_type_list = []
    ON_GRID = Value(0, 'ON GRID')

    system_type_list.append(ON_GRID)
    OFF_GRID = Value(1, 'OFF GRID')
    system_type_list.append(OFF_GRID)
    PUMPING = Value(2, 'PUMPING')
    system_type_list.append(PUMPING)
    DONT_KNOW = Value(3, 'No se')
    system_type_list.append(DONT_KNOW)
    system_type = Variable(0, 'Tipo de systema', frozenset(system_type_list))

    device_list = []
    ON_GRID_DEVICE = Value(4, 'ON GRID DEVICE')
    device_list.append(ON_GRID_DEVICE)
    OFF_GRID_DEVICE = Value(5, 'OFF GRID DEVICE')
    device_list.append(OFF_GRID_DEVICE)
    device_types = Variable(1, 'Tipo de dispositivo', frozenset(device_list))

    return [
        Rule({Fact(system_type, OFF_GRID)}, Fact(device_types, OFF_GRID_DEVICE)),
        Rule({Fact(system_type, ON_GRID)}, Fact(device_types, ON_GRID_DEVICE))
    ]
