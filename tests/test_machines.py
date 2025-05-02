"""Test machine generation."""

import csv
import io

from snailz.machines import Machine


def test_generate_machines_distinct_and_correct_length():
    length = 5
    machines = Machine.generate(length)
    assert len(machines) == length
    assert len(set(m.id for m in machines)) == length
    assert len(set(m.name for m in machines)) == length


def test_convert_machines_to_csv():
    fixture = [
        Machine(id="abc", name="ABC"),
        Machine(id="def", name="DEF"),
    ]
    stream = io.StringIO()
    Machine.to_csv(csv.writer(stream), fixture)
    expected = "\r\n".join(["id,name", "abc,ABC", "def,DEF"]) + "\r\n"
    assert stream.getvalue() == expected
