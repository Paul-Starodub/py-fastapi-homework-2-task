from datetime import date
from decimal import Decimal
from typing import Annotated, Optional
from pydantic import BaseModel, Field, ConfigDict
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
    code: Annotated[str, Field(max_length=3)]
    name: Annotated[str | None, Field(max_length=255)] = None


class MovieStatusSchema(BaseModel):
    status: MovieStatusEnum


class MovieBaseSchema(BaseModel):
    name: Annotated[str, Field(max_length=255)]
    date: date
    score: float
    overview: str

    model_config = ConfigDict(from_attributes=True, json_encoders={Decimal: float})


class MovieBase(MovieBaseSchema):
    id: int


class MovieListResponseSchema(BaseModel):
    movies: list[MovieBase]
    prev_page: str | None
    next_page: str | None
    total_pages: int
    total_items: int


class MovieListItemSchema(MovieBase, MovieStatusSchema):
    budget: Decimal = Field(max_digits=15, decimal_places=2)
    revenue: float
    country: Country
    genres: list[Genre]
    actors: list[Actor]
    languages: list[Language]


class MovieDetailSchema(MovieBaseSchema, MovieStatusSchema):
    budget: Decimal = Field(max_digits=15, decimal_places=2)
    revenue: float
    country: str
    genres: list[str]
    actors: list[str]
    languages: list[str]


class MovieUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    date: Optional[date] = None
    score: Optional[float] = None
    overview: Optional[str] = None
    status: Optional[MovieStatusEnum] = None
    budget: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    revenue: Optional[float] = None
    country: Optional[str] = None
    genres: Optional[list[str]] = None
    actors: Optional[list[str]] = None
    languages: Optional[list[str]] = None
