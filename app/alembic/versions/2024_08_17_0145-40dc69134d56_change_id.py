"""change id

Revision ID: 40dc69134d56
Revises: 7a1a11bc296c
Create Date: 2024-08-17 01:45:29.869306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40dc69134d56'
down_revision: Union[str, None] = '7a1a11bc296c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_id'), table_name='users')
    # ### end Alembic commands ###