"""admin features

Revision ID: 0584687d44f7
Revises: 0bbe67b11a96
Create Date: 2025-09-22 19:53:24.148059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0584687d44f7'
down_revision: Union[str, Sequence[str], None] = '0bbe67b11a96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('perfumes', schema=None) as batch_op:
        #batch_op.drop_constraint(None, type_='unique')
        #batch_op.drop_constraint('uq_perfume_sig', type_='unique')
        batch_op.create_unique_constraint('uq_perfume_sig', ['sig'])

def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('perfumes', schema=None) as batch_op:
        batch_op.drop_constraint('uq_perfume_sig', type_='unique')
        # si vols, pots re-crear la versió antiga (amb nom automàtic)
        batch_op.create_unique_constraint(None, ['sig'])
