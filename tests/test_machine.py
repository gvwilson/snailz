"""Test machine generation."""

from dataclasses import fields
from snailz import Machine, Parameters
from snailz._utils import UnquotedDatabase


def test_machine_creation_requires_name():
    m = Machine(name="Test Machine")
    assert m.name == "Test Machine"


def test_machine_assigns_ident_on_init():
    m = Machine(name="Test Machine")
    assert m.ident.startswith("M")
    assert m.ident[1:].isdigit()


def test_machine_ident_is_unique():
    m1 = Machine(name="Machine One")
    m2 = Machine(name="Machine Two")
    assert m1.ident != m2.ident


def test_machine_make_creates_correct_number():
    machines = Machine.make(Parameters(num_machines=5))
    assert len(machines) == 5
    assert all(isinstance(m, Machine) for m in machines)


def test_machine_make_names_are_unique():
    machines = Machine.make(Parameters(num_machines=10))
    names = [m.name for m in machines]
    assert len(names) == len(set(names))


def test_machine_persist_to_db():
    db = UnquotedDatabase(memory=True)
    machines = Machine.make(Parameters(num_machines=3))
    Machine.save_db(db, machines)
    rows = list(db[Machine.table_name].rows)
    assert set(r["ident"] for r in rows) == set(p.ident for p in machines)
    field_names = {f.name for f in fields(machines[0])}
    assert all(len(r) == len(field_names) for r in rows)
    assert set(rows[0].keys()) == field_names
