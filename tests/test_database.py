"""Test database functionality."""

import pytest

from snailz.database import make_database


@pytest.fixture
def assays_csv(fs):
    """An assays CSV file."""
    content = """ident,specimen_id,performed,performed_by
123456,AB1234,2023-01-15,jd1234
789012,CD5678,2023-01-16,js5678"""
    path = "/assays.csv"
    fs.create_file(path, contents=content)
    return path


@pytest.fixture
def people_csv(fs):
    """A specimens CSV file."""
    content = """ident,personal,family
jd1234,John,Doe
js5678,Jane,Smith"""
    path = "/people.csv"
    fs.create_file(path, contents=content)
    return path


@pytest.fixture
def specimens_csv(fs):
    """A specimens CSV file."""
    content = """ident,x,y,genome,mass,collected_on,territory
AB1234,1,2,ACGT,1.5,2025-03-10,2.5
CD5678,3,4,CGTA,2.5,2025-03-15,3.7"""
    path = "/specimens.csv"
    fs.create_file(path, contents=content)
    return path


def test_make_database(fs, assays_csv, people_csv, specimens_csv):
    """Test creating a database from CSV files."""
    conn = make_database(assays_csv, people_csv, specimens_csv, None)

    cursor = conn.cursor()
    # Check row counts
    for table in ("assays", "people", "specimens"):
        stmt = f"select count(*) from {table}"
        cursor.execute(stmt)
        assert cursor.fetchone()[0] == 2

    # Specifically test the collected_on field in specimens
    cursor.execute("SELECT ident, collected_on FROM specimens ORDER BY ident")
    results = cursor.fetchall()
    assert len(results) == 2
    assert results[0] == ("AB1234", "2025-03-10")
    assert results[1] == ("CD5678", "2025-03-15")

    conn.close()
