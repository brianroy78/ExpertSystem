from app.models import Variable, Value, Rule, Fact
from database import get_session
from database.tables import VariableTable, ValueTable, RuleTable, FactTable


def to_fact(fact: FactTable, variables: dict[int, Variable], values: dict[int, Value]) -> Fact:
    return Fact(
        variables[fact.variable.id],
        values[fact.value.id]
    )


def to_variable(variable: VariableTable, values: dict[int, Value]) -> Variable:
    return Variable(
        variable.id,
        variable.name,
        frozenset([values[v.id] for v in variable.options])
    )


def is_required(variable: VariableTable) -> bool:
    return variable.required


def from_table_to_model() -> tuple[set[Rule], set[Variable]]:
    with get_session() as session:
        values = {v.id: Value(v.id, v.name) for v in session.query(ValueTable)}
        variables = {v.id: to_variable(v, values) for v in session.query(VariableTable)}
        rules: set = {
            Rule(
                frozenset([to_fact(p, variables, values) for p in r.premises]),
                frozenset([to_fact(c, variables, values) for c in r.conclusions])
            )
            for r in session.query(RuleTable)
        }
        ids_ = [v.id for v in session.query(VariableTable).filter(VariableTable.required)]
        return rules, {variables[id_] for id_ in ids_}
