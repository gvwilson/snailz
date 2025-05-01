"""Test machine generation."""

from snailz.machines import MachineParams, Machine, AllMachines


def test_generate_machines_correct_length():
    params = MachineParams()
    machines = AllMachines.generate(params)
    assert len(machines.items) == params.number


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
