from datetime import date
from fastapi import HTTPException, status
from sqlalchemy import select, Result, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from database.models import GenreModel, ActorModel, LanguageModel, CountryModel, MovieModel
from schemas import MovieDetailSchema, MovieUpdateSchema


async def safe_commit(db: AsyncSession, *, movie_name: str | None = None, release_date: date | None = None):
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(f"A movie with the name '{movie_name}' " f"and release date '{release_date}' already exists."),
        )


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
    stmt = select(MovieModel).limit(limit).offset(offset).order_by(MovieModel.id.desc())
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
    await safe_commit(db, movie_name=movie_data.name, release_date=movie_data.date)
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


async def update_movie(db: AsyncSession, movie_id: int, movie_data: MovieUpdateSchema):
    stmt = (
        select(MovieModel)
        .where(MovieModel.id == movie_id)
        .options(
            selectinload(MovieModel.country),
            selectinload(MovieModel.genres),
            selectinload(MovieModel.actors),
            selectinload(MovieModel.languages),
        )
    )
    result = await db.execute(stmt)
    movie = result.scalar_one_or_none()
    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found.",
        )
    update_fields = movie_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(movie, field, value)
    await db.commit()
    await db.refresh(movie)
    return movie


async def delete_movie(db: AsyncSession, movie_id: int) -> None:
    stmt = select(MovieModel).where(MovieModel.id == movie_id)
    result = await db.execute(stmt)
    movie = result.scalar_one_or_none()
    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found.",
        )
    await db.delete(movie)
    await db.commit()
