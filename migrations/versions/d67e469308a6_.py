"""empty message

Revision ID: d67e469308a6
Revises: bdddc025c95a
Create Date: 2023-07-15 04:35:48.284352

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd67e469308a6'
down_revision = 'bdddc025c95a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('pw_hash', sa.String(length=128), nullable=True),
    sa.Column('join_date', sa.DateTime(), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('oauth', sa.Boolean(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_join_date'), ['join_date'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_last_login'), ['last_login'], unique=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('ix_user_email')
        batch_op.drop_index('ix_user_join_date')
        batch_op.drop_index('ix_user_last_login')

    op.drop_table('user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('first_name', sa.VARCHAR(length=64), nullable=True),
    sa.Column('last_name', sa.VARCHAR(length=64), nullable=True),
    sa.Column('email', sa.VARCHAR(length=64), nullable=True),
    sa.Column('pw_hash', sa.VARCHAR(length=128), nullable=True),
    sa.Column('join_date', sa.DATETIME(), nullable=True),
    sa.Column('last_login', sa.DATETIME(), nullable=True),
    sa.Column('role', sa.VARCHAR(length=64), nullable=True),
    sa.Column('oauth', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index('ix_user_last_login', ['last_login'], unique=False)
        batch_op.create_index('ix_user_join_date', ['join_date'], unique=False)
        batch_op.create_index('ix_user_email', ['email'], unique=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_last_login'))
        batch_op.drop_index(batch_op.f('ix_users_join_date'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    op.drop_table('roles')
    # ### end Alembic commands ###