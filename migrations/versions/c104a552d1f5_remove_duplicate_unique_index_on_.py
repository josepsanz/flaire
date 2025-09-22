"""remove duplicate unique index on perfumes.sig (bis)

Revision ID: c104a552d1f5
Revises: bc91bb77c83a
Create Date: 2025-09-22 20:31:55.983755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c104a552d1f5'
down_revision: Union[str, Sequence[str], None] = 'bc91bb77c83a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    with op.batch_alter_table("perfumes", schema=None) as batch_op:
        batch_op.alter_column(
            "sig",
            existing_type=sa.String(32),
            nullable=False
        )


def downgrade():
    with op.batch_alter_table("perfumes", schema=None) as batch_op:
        batch_op.alter_column(
            "sig",
            existing_type=sa.String(32),
            nullable=False
        )
