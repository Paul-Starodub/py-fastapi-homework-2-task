import math
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import crud
from database import get_db
from schemas import MovieListResponseSchema, MovieListItemSchema

router = APIRouter()


@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_movies(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
):
    offset = (page - 1) * per_page
    movies, total_items = await crud.get_movies_paginated(db=db, limit=per_page, offset=offset)
    if not movies:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No movies found.")
    total_pages = math.ceil(total_items / per_page)
    return MovieListResponseSchema(
        movies=movies,
        prev_page=(f"/api/v1/theater/movies/?page={page - 1}&per_page={per_page}" if page > 1 else None),
        next_page=(f"/api/v1/theater/movies/?page={page + 1}&per_page={per_page}" if page < total_pages else None),
        total_pages=total_pages,
        total_items=total_items,
    )


@router.get("/movies/{movie_id}/", response_model=MovieListItemSchema)
async def get_movie_by_id(movie_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    movie = await crud.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie with the given ID was not found.")
    return movie
