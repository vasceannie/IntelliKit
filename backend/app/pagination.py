from typing import Generic, TypeVar, List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import Query

# Define a type variable T that can be any type. This will be used for generic programming.
T = TypeVar('T')

class Page(BaseModel, Generic[T]):
    """
    A class to represent a paginated response.

    Attributes:
        items (List[T]): A list of items of type T for the current page.
        total (int): The total number of items available across all pages.
        page (int): The current page number.
        size (int): The number of items per page.
        pages (int): The total number of pages available.
    """
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

async def paginate(
    db: AsyncSession,
    model: T,
    page: int = Query(1, ge=1),  # Default to page 1, must be greater than or equal to 1
    size: int = Query(10, ge=1, le=100)  # Default to size 10, must be between 1 and 100
) -> Page[T]:
    """
    Paginate the results from a database query.

    Args:
        db (AsyncSession): The database session to use for the query.
        model (T): The SQLAlchemy model to query.
        page (int, optional): The page number to retrieve. Defaults to 1.
        size (int, optional): The number of items per page. Defaults to 10.

    Returns:
        Page[T]: A Page object containing the items for the current page, total items, 
                  current page number, size, and total pages.

    Raises:
        Exception: Raises an exception if there is an error during the database query.
    """
    # Create a query to select all items from the specified model.
    query = select(model)
    
    # Get the total number of items in the model.
    total = await db.scalar(select(func.count()).select_from(model))
    
    # Calculate the offset for the current page.
    offset = (page - 1) * size
    
    # Execute the query with the specified offset and limit to get the items for the current page.
    items = (await db.execute(query.offset(offset).limit(size))).scalars().all()
    
    # Calculate the total number of pages based on total items and size.
    pages = (total + size - 1) // size
    
    # Return a Page object with the paginated results.
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
