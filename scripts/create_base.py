import pickle
from typing import List

import yaml

from base import get_rules
from main import present_var
from models import Variable, Value, Fact, Rule


def present_variables(variables: List[Variable]) -> Fact:
    print(f'Seleccionar una Variable')
    options: dict = {}
    for index, variable in enumerate(variables):
        print(f'({index}) {variable.name}')
        options[index] = variable
    selected_var: Variable = options.get(int(input('respuesta: ')))
    value: Value = present_var(selected_var)
    return Fact(selected_var, value)


def main():
    variables = []
    id_counter = 0
    while True:
        var_name = input('Nombre de la variable: ')
        if var_name == 'xxx':
            break
        options = list()
        while True:
            option = input('Nombre de la opcion: ')
            if option == 'xxx':
                break
            options.append(Value(id_counter, option))
            id_counter += 1
        variables.append(Variable(id_counter, var_name, frozenset(options)))
        id_counter += 1
    print('Creando Reglas ...')
    rules = []
    while True:
        propositions = list()
        while True:
            proposition: Fact = present_variables(variables)
            propositions.append(proposition)
            response = input('Añadir nueva premisa? (Y, N): ')
            if response != 'Y':
                break
        print('creando declaracion ...')
        statement: Fact = present_variables(variables)
        rules.append(Rule(set(propositions), statement))
        response = input('Añadir nueva Regla? (Y, N): ')
        if response != 'Y':
            break

    for r in rules:
        print(r)
    with open('base de conocimiento.yaml', 'w+') as file:
        # text = yaml.dump(rules, Dumper=yaml.CDumper)
        text = pickle.dump(rules)
        print(text)
        file.write(text)


def test():
    rules = get_rules()
    with open('base de conocimiento', 'wb') as file:
        # text = yaml.dump(rules, Dumper=yaml.SafeDumper)
        pickle.dump(rules, file)


if __name__ == '__main__':
    # main()
    test()
