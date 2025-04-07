"""Test machine generation."""

import pytest

from snailz.machines import Machine, AllMachines, machines_generate


def test_generate_machines_correct_length():
    machines = machines_generate(3)
    assert len(machines.items) == 3


def test_convert_machines_to_csv():
    fixture = AllMachines(
        items=[
            Machine(ident="abc", name="ABC"),
            Machine(ident="def", name="DEF"),
        ]
    )
    result = fixture.to_csv()
    expected = "\n".join(["ident,name", "abc,ABC", "def,DEF"]) + "\n"
    assert result == expected
