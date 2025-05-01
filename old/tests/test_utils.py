"""Test utilities."""

from datetime import date, timedelta
import pytest

from pydantic import BaseModel

from snailz.utils import fail, json_dump, report, to_csv, unique_id


class DummyModel(BaseModel):
    top: int
    middle: date
    bottom: str


def test_json_dump_of_special_types():
    fixture = {"key": DummyModel(top=1, middle=date(2025, 1, 1), bottom="text")}
    actual = json_dump(fixture)
    expected = [
        "{",
        '  "key": {',
        '    "top": 1,',
        '    "middle": "2025-01-01",',
        '    "bottom": "text"',
        "  }",
        "}",
    ]
    assert actual == "\n".join(expected)


def test_json_dump_fails_for_unknown_type():
    with pytest.raises(TypeError):
        json_dump(timedelta(days=1))


def test_unique_id_generator_produces_unique_ids():
    gen = unique_id("test", lambda n: f"x{n}")
    values = {gen.send((i,)) for i in range(10)}
    assert len(values) == 10


def test_unique_id_generator_fails_at_limit():
    gen = unique_id("test", lambda: "x", limit=3)
    with pytest.raises(RuntimeError):
        for _ in range(3):
            gen.send(())


def test_fail_prints_message(capsys):
    with pytest.raises(SystemExit) as exc:
        fail("message")
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert captured.err == "message\n"
    assert captured.out == ""


def test_report_with_verbosity_off(capsys):
    report(False, "message")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_report_with_verbosity_on(capsys):
    report(True, "message")
    captured = capsys.readouterr()
    assert captured.out == "message\n"
    assert captured.err == ""


def test_to_csv_generic_conversion():
    rows = [[1, 2], [3, 4]]
    fields = ["left", "right"]

    def func(r):
        return r

    result = to_csv(rows, fields, func)
    assert result == "left,right\n1,2\n3,4\n"
