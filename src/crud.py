from sqlalchemy import select, Result, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from database import MovieModel


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
