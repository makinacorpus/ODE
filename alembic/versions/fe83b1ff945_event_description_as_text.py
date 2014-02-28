"""event description as text

Revision ID: fe83b1ff945
Revises: 55ed9fcb4032
Create Date: 2014-02-28 09:52:02.817686

"""

# revision identifiers, used by Alembic.
revision = 'fe83b1ff945'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('events', 'description',
                    type_=sa.UnicodeText(), existing_type=sa.Unicode())


def downgrade():
    op.alter_column('events', 'description',
                    type_=sa.Unicode(), existing_type=sa.UnicodeText())
