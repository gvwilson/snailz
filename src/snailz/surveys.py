"""Generate random surveys on grids."""

from datetime import date, timedelta
import io
import random

from pydantic import BaseModel, Field, model_validator

from .grid import Grid
from . import utils


class SurveyParams(BaseModel):
    """Parameters for survey generation."""

    number: int = Field(default=3, gt=0, description="Number of surveys")
    size: int = Field(
        default=utils.DEFAULT_SURVEY_SIZE, gt=0, description="Survey size"
    )
    start_date: date = Field(
        default=date.fromisoformat("2024-03-01"),
        description="Start date for specimen collection",
    )
    max_interval: int = Field(
        gt=0, default=7, description="Maximum interval between samples"
    )

    model_config = {"extra": "forbid"}


class Survey(BaseModel):
    """A single survey."""

    ident: str = Field(description="survey identifier")
    size: int = Field(description="survey size")
    start_date: date = Field(
        default=date.fromisoformat("2024-03-01"),
        description="Start date for specimen collection",
    )
    end_date: date = Field(
        default=date.fromisoformat("2024-04-30"),
        description="End date for specimen collection",
    )
    cells: Grid[int] | None = Field(default=None, description="survey cells")

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def initialize_grid(self):
        self.cells = Grid(width=self.size, height=self.size, default=0)
        self.fill_cells()
        return self

    def fill_cells(self) -> None:
        """Fill survey grid with fractal of random values."""
        assert isinstance(self.cells, Grid)
        size_1 = self.size - 1
        center = self.size // 2
        moves = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        x, y = center, center
        self.cells[x, y] = 1
        while (x != 0) and (x != size_1) and (y != 0) and (y != size_1):
            self.cells[x, y] += 1
            m = random.choice(moves)
            x += m[0]
            y += m[1]

    def to_csv(self) -> str:
        """Create a CSV representation of a single survey.

        Returns:
            A CSV-formatted string with survey cells.
        """
        assert isinstance(self.cells, Grid)
        output = io.StringIO()
        for y in range(self.size - 1, -1, -1):
            temp = [f"{self.cells[x, y]}" for x in range(self.size)]
            print(",".join(temp), file=output)
        return output.getvalue()


class AllSurveys(BaseModel):
    """A set of generated surveys."""

    items: list[Survey] = Field(description="all surveys")

    model_config = {"extra": "forbid"}


def surveys_generate(params: SurveyParams) -> AllSurveys:
    """Generate random surveys.

    Parameters:
        params: Data generation parameters.

    Returns:
        Data model including all surveys.
    """

    gen = utils.UniqueIdGenerator("survey", _survey_id_generator)
    current_date = params.start_date
    items = []
    for _ in range(params.number):
        next_date = current_date + timedelta(
            days=random.randint(1, params.max_interval)
        )
        items.append(
            Survey(
                ident=gen.next(),
                size=params.size,
                start_date=current_date,
                end_date=next_date,
            )
        )
        current_date = next_date + timedelta(days=1)

    return AllSurveys(items=items)


def _survey_id_generator() -> str:
    """Generate unique ID for a survey.

    Returns:
        Candidate ID 'gNNN'.
    """

    num = random.randint(0, 999)
    return f"S{num:03d}"
