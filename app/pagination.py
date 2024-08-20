from typing import Generic, TypeVar, List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import Query

T = TypeVar('T')

class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

async def paginate(
    db: AsyncSession,
    model: T,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
) -> Page[T]:
    query = select(model)
    total = await db.scalar(select(func.count()).select_from(model))
    
    offset = (page - 1) * size
    items = (await db.execute(query.offset(offset).limit(size))).scalars().all()
    
    pages = (total + size - 1) // size
    
    return Page(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

# Usage example:
# @app.get("/items", response_model=Page[Item])
# async def read_items(
#     db: AsyncSession = Depends(get_db),
#     page: int = Query(1, ge=1),
#     size: int = Query(10, ge=1, le=100)
# ):
#     return await paginate(db, Item, page, size)
