"""Test database creation."""

from pathlib import Path

from snailz.database import database_generate

ASSAYS = """\
ident,specimen,person,performed,machine
123456,ABCDEF,ab1234,2024-03-01,M0001
987654,GHIJKL,cd5678,2024-03-02,M0002
"""

MACHINES = """\
ident,name
M0001,AeroProbe
M0002,NanoCounter Plus
"""

PERSONS = """\
ident,personal,family
ab1234,Beta,Alpha
cd5678,Delta,Charlie
"""

SPECIMENS = """\
ident,survey,x,y,collected,genome,mass
ABCDEF,S001,1,1,2024-02-01,CGTCCTTACTAGGACGTTTG,12.34
GHIJKL,S001,5,5,2024-02-02,GCCACTTACTAGGACGTTTG,15.67
"""

READING = """\
id,123456,,,
specimen,ABCDEF,,,
date,2024-02-01,,,
by,ab1234,,,
machine,M0001,,,
,A,B,C,D
1,1.0,2.0,3.0,4.0
2,11.0,12.0,13.0,14.0
3,21.0,22.0,23.0,24.0
4,31.0,32.0,33.0,34.0
"""

TREATMENT = """\
id,123456,,,
specimen,ABCDEF,,,
date,2024-02-01,,,
by,ab1234,,,
machine,M0001,,,
,A,B,C,D
1,C,C,C,C
2,C,C,C,C
3,S,S,S,S
4,S,S,S,S
"""

FIXTURE = (
    ("/assays.csv", ASSAYS),
    ("/machines.csv", MACHINES),
    ("/persons.csv", PERSONS),
    ("/specimens.csv", SPECIMENS),
    ("/assays/123456_readings.csv", READING),
    ("/assays/123456_treatments.csv", TREATMENT),
)


def test_database_creation(fs):
    for filename, contents in FIXTURE:
        fs.create_file(filename, contents=contents)
    conn = database_generate(Path("/"), None)
    cursor = conn.cursor()

    cursor.execute("select * from assays")
    assert set(cursor.fetchall()) == {
        ("123456", "ABCDEF", "ab1234", "2024-03-01", "M0001"),
        ("987654", "GHIJKL", "cd5678", "2024-03-02", "M0002"),
    }

    cursor.execute("select * from machines")
    assert set(cursor.fetchall()) == {
        ("M0001", "AeroProbe"),
        ("M0002", "NanoCounter Plus"),
    }

    cursor.execute("select * from persons")
    assert set(cursor.fetchall()) == {
        ("ab1234", "Beta", "Alpha"),
        ("cd5678", "Delta", "Charlie"),
    }

    cursor.execute("select * from specimens")
    assert set(cursor.fetchall()) == {
        ("ABCDEF", "S001", 1, 1, "2024-02-01", "CGTCCTTACTAGGACGTTTG", 12.34),
        ("GHIJKL", "S001", 5, 5, "2024-02-02", "GCCACTTACTAGGACGTTTG", 15.67),
    }

    cursor.execute("select * from readings")
    assert len(cursor.fetchall()) == 16
    cursor.execute("select reading from readings where row = 1 and col = 'A'")
    result = cursor.fetchall()
    assert len(result) == 1
    assert result[0][0] == 1.0

    cursor.execute("select * from treatments")
    assert len(cursor.fetchall()) == 16
    cursor.execute("select treatment from treatments where row = 1 and col = 'A'")
    result = cursor.fetchall()
    assert len(result) == 1
    assert result[0][0] == "C"
