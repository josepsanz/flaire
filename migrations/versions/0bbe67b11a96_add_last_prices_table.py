"""add last_prices table

Revision ID: 0bbe67b11a96
Revises: 9d4515772289
Create Date: 2025-09-22 13:53:00.500349

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0bbe67b11a96'
down_revision: Union[str, Sequence[str], None] = '9d4515772289'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_table(
        'last_prices',
        sa.Column(
            'price_id',
            sa.Integer(),
            sa.ForeignKey('prices.id', ondelete='CASCADE'),
            primary_key=True,
            nullable=False
        )
    )

def downgrade():
    op.drop_table('last_prices')
