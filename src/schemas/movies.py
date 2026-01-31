from datetime import date
from decimal import Decimal
from typing import Annotated, Literal
from pydantic import BaseModel, Field
from database.models import MovieStatusEnum


class CommonBase(BaseModel):
    id: int
    name: Annotated[str, Field(max_length=255)]


class Actor(CommonBase):
    pass


class Genre(CommonBase):
    pass


class Language(CommonBase):
    pass


class Country(BaseModel):
    id: int
    name: Annotated[str, Field(max_length=3)]
    name: Annotated[str, Field(max_length=255)]


class MovieBaseSchema(BaseModel):
    name: Annotated[str, Field(max_length=255)]
    date: date
    score: float
    overview: str


class MovieListResponseSchema(MovieBaseSchema):
    id: int


class MovieListItemSchema(MovieBaseSchema):
    status: Literal[MovieStatusEnum.RELEASED, MovieStatusEnum.POST_PRODUCTION, MovieStatusEnum.IN_PRODUCTION]
    budget: Decimal = Field(max_digits=15, decimal_places=2)
    revenue: float
    country: Country
    genres: list[Genre]
    actors: list[Actor]
    languages: list[Language]


class MovieDetailSchema(MovieListItemSchema):
    pass
