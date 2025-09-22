"""remove duplicate unique index on perfumes.sig

Revision ID: bc91bb77c83a
Revises: 0584687d44f7
Create Date: 2025-09-22 20:25:13.421691

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc91bb77c83a'
down_revision: Union[str, Sequence[str], None] = '0584687d44f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    with op.batch_alter_table('perfumes', schema=None) as batch_op:
        pass

def downgrade():
    with op.batch_alter_table('perfumes', schema=None) as batch_op:
        pass
