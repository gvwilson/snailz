"""Test survey generation."""

from datetime import timedelta

from snailz.surveys import SurveyParams, Survey, surveys_generate


def test_generate_surveys_correct_length():
    params = SurveyParams()
    surveys = surveys_generate(params)
    assert len(surveys.items) == params.number
    for g in surveys.items:
        assert len(g.cells) == params.size
        assert all(len(r) == params.size for r in g.cells)


def test_generate_surveys_correct_dates():
    params = SurveyParams()
    max_date = (
        params.start_date
        + timedelta(days=params.number - 1)
        + timedelta(days=params.number * params.max_interval)
    )
    surveys = surveys_generate(params)
    for g in surveys.items:
        assert params.start_date <= g.start_date
        assert g.start_date <= g.end_date
        assert g.end_date <= max_date


def test_convert_survey_to_csv():
    size = 3
    params = SurveyParams().model_copy(update={"size": size})
    fixture = Survey(
        ident="G000",
        size=size,
        start_date=params.start_date,
        end_date=params.start_date,
        cells=[list(range(size)) for _ in range(size)],
    )
    result = fixture.to_csv()
    assert result == "2,2,2\n1,1,1\n0,0,0\n"
