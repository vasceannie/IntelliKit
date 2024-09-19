import sys
import os
from pathlib import Path

# Add the root directory of the project to the PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Add the parent directory to the sys.path to find the backend module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add the backend directory to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app.models import Base  # Import after setting the path
from backend.app.auth.models import User
from backend.app.config import settings
from backend.app.auth.service import pwd_context
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func

# Create engine and session
engine = create_async_engine(settings.DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        async with session.begin():
            # Check if we already have users
            if (await session.execute(select(func.count(User.id)))).scalar() == 0:
                # Create sample users
                admin_user = User(
                    email="travis.vas@gmail.com",
                    hashed_password=pwd_context.hash("$QUirtle123"),
                    is_superuser=True,
                    full_name="Travis Vasceannie"
                )
                session.add(admin_user)

                regular_user = User(
                    email="user@example.com",
                    hashed_password=pwd_context.hash("password123"),
                    full_name="Regular User"
                )
                session.add(regular_user)

                await session.commit()

                print("Sample data has been populated.")
            else:
                print("Database already contains data. Skipping population.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())