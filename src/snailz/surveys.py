"""Generate random surveys on grids."""

from datetime import date, timedelta
import io
import random

from pydantic import BaseModel, Field

from .grid import Grid
from .parameters import SurveyParams
from . import model, utils


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
    cells: Grid[int] = Field(
        default_factory=lambda data: model.survey_initialize_grid(data["size"]),
        description="survey cells",
    )

    model_config = {"extra": "forbid"}

    def max_pollution(self) -> float:
        """Maximum pollution value in this survey."""
        assert self.cells is not None  # for type checking
        result = self.cells[0, 0]
        for x in range(self.size):
            for y in range(self.size):
                result = max(result, self.cells[x, y])
        return result

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

    def max_pollution(self) -> float:
        """Maximum cell value of all surveys in this set."""
        return max(survey.max_pollution() for survey in self.items)

    @staticmethod
    def generate(params: SurveyParams) -> "AllSurveys":
        """Generate random surveys.

        Parameters:
            params: Data generation parameters.

        Returns:
            Data model including all surveys.
        """

        gen = utils.unique_id("survey", _survey_id_generator)
        current_date = params.start_date
        items = []
        for _ in range(params.number):
            next_date = current_date + model.days_to_next_survey(params)
            items.append(
                Survey(
                    ident=next(gen),
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
