"""Test survey generation."""

from datetime import timedelta

from snailz.surveys import SurveyParams, Survey, AllSurveys


def test_generate_surveys_correct_length():
    params = SurveyParams()
    surveys = AllSurveys.generate(params)
    assert len(surveys.items) == params.number
    assert all(s.size == params.size for s in surveys.items)


def test_generate_surveys_correct_dates():
    params = SurveyParams()
    max_date = (
        params.start_date
        + timedelta(days=params.number - 1)
        + timedelta(days=params.number * params.max_interval)
    )
    surveys = AllSurveys.generate(params)
    for s in surveys.items:
        assert params.start_date <= s.start_date
        assert s.start_date <= s.end_date
        assert s.end_date <= max_date


def test_convert_survey_to_csv():
    size = 3
    params = SurveyParams().model_copy(update={"size": size})
    fixture = Survey(
        ident="G000",
        size=size,
        start_date=params.start_date,
        end_date=params.start_date,
    )
    for y in range(size - 1, -1, -1):
        for x in range(size):
            fixture.cells[x, y] = y
    result = fixture.to_csv()
    assert result == "2,2,2\n1,1,1\n0,0,0\n"
