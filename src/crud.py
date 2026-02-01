from sqlalchemy import select, Result, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from database import MovieModel
from database.models import GenreModel, ActorModel, LanguageModel, CountryModel
from schemas import MovieDetailSchema


async def get_or_create(db: AsyncSession, model, field: str, value: str):
    stmt = select(model).where(getattr(model, field) == value)
    obj = await db.scalar(stmt)
    if obj:
        return obj
    obj = model(**{field: value})
    db.add(obj)
    await db.flush()
    return obj


async def get_movies_paginated(db: AsyncSession, limit: int, offset: int):
    stmt = select(MovieModel).limit(limit).offset(offset)
    result = await db.execute(stmt)
    movies = result.scalars().all()
    count_stmt = select(func.count()).select_from(MovieModel)
    total_items = await db.scalar(count_stmt)
    return movies, total_items


async def get_movie_by_id(db: AsyncSession, movie_id: int):
    stmt = (
        select(MovieModel)
        .where(MovieModel.id == movie_id)
        .options(
            joinedload(MovieModel.country),
            selectinload(MovieModel.genres),
            selectinload(MovieModel.actors),
            selectinload(MovieModel.languages),
        )
    )
    result: Result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_movie(db: AsyncSession, movie_data: MovieDetailSchema):
    country = await get_or_create(db, CountryModel, "code", movie_data.country)
    movie = MovieModel(
        name=movie_data.name,
        date=movie_data.date,
        score=movie_data.score,
        overview=movie_data.overview,
        status=movie_data.status,
        budget=movie_data.budget,
        revenue=movie_data.revenue,
        country=country,
    )
    movie.genres = [await get_or_create(db, GenreModel, "name", name) for name in movie_data.genres]
    movie.actors = [await get_or_create(db, ActorModel, "name", name) for name in movie_data.actors]
    movie.languages = [await get_or_create(db, LanguageModel, "name", name) for name in movie_data.languages]
    db.add(movie)
    await db.commit()
    stmt = (
        select(MovieModel)
        .options(
            selectinload(MovieModel.country),
            selectinload(MovieModel.genres),
            selectinload(MovieModel.actors),
            selectinload(MovieModel.languages),
        )
        .where(MovieModel.id == movie.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()
