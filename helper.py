from dotenv import load_dotenv
import os
from alembic import command
from alembic.config import Config

load_dotenv()

alembic_cfg = Config("app/alembic.ini")
command.revision(alembic_cfg, autogenerate=True, message="initial")