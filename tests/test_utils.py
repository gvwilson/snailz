"""Test utilities."""

from datetime import date
from pathlib import Path
import pytest

from pydantic import BaseModel

from snailz.utils import UniqueIdGenerator, display, to_csv, fail, report


class DummyModel(BaseModel):
    top: int
    middle: date
    bottom: str


def test_unique_id_generator_produces_unique_ids():
    gen = UniqueIdGenerator("test", lambda n: f"x{n}")
    values = {gen.next(i) for i in range(10)}
    assert len(values) == 10


def test_unique_id_generator_fails_at_limit():
    gen = UniqueIdGenerator("test", lambda: "x", limit=3)
    with pytest.raises(RuntimeError):
        for _ in range(3):
            gen.next()


def test_display_to_file(fs):
    json_path = Path("/test.json")
    display(json_path, DummyModel(top=1, middle=date(1970, 1, 1), bottom="two"))
    assert json_path.exists()
    expected = [
        "{",
        '  "top": 1,',
        '  "middle": "1970-01-01",',
        '  "bottom": "two"',
        "}",
    ]
    assert json_path.read_text() == "\n".join(expected)

    str_path = Path("/test.txt")
    str_text = "some text"
    display(str_path, str_text)
    assert str_path.exists()
    assert str_path.read_text() == str_text


def test_display_to_stdout(capsys):
    display(None, "some text")
    captured = capsys.readouterr()
    assert captured.out == "some text\n"


def test_display_fails_for_invalid_data():
    with pytest.raises(TypeError):
        display(None, {"key": Exception("error")})


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
