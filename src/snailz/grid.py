"""Represent 2D grid as Pydantic class."""

from typing import TypeVar, Generic
from pydantic import BaseModel, ConfigDict, Field, model_validator

T = TypeVar("T")


class Point(BaseModel):
    """A 2D point."""

    x: int = Field(description="x coordinate")
    y: int = Field(description="y coordinate")


class Grid(BaseModel, Generic[T]):
    """A 2D grid."""

    width: int = Field(gt=0, description="Width of the grid")
    height: int = Field(gt=0, description="Height of the grid")
    default: T = Field(description="Default value for uninitialized cells")
    data: list[list[T]] | None = Field(default=None, description="Grid values")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def initialize_grid(self):
        if self.data is None:
            self.data = [
                [self.default for _ in range(self.height)] for _ in range(self.width)
            ]
        return self

    def __getitem__(self, key: tuple[int, int]) -> T:
        assert isinstance(self.data, list)
        self._validate_key(key)
        x, y = key
        return self.data[x][y]

    def __setitem__(self, key: tuple[int, int], value: T) -> None:
        assert isinstance(self.data, list)
        self._validate_key(key)
        x, y = key
        self.data[x][y] = value

    def _validate_key(self, key: tuple[int, int]) -> None:
        if not isinstance(key, tuple) or len(key) != 2:
            raise KeyError(f"Key must be a tuple of (x, y), got {key}")

        x, y = key
        if not isinstance(x, int) or not isinstance(y, int):
            raise KeyError(f"Coordinates must be integers, got ({x}, {y})")

        if x < 0 or x >= self.width:
            raise IndexError(f"X coordinate {x} out of range [0, {self.width - 1}]")

        if y < 0 or y >= self.height:
            raise IndexError(f"Y coordinate {y} out of range [0, {self.height - 1}]")

    def __str__(self) -> str:
        return "\n".join(
            ",".join(f"{self[x, y]}" for x in range(self.width))
            for y in range(self.height - 1, -1, -1)
        )
