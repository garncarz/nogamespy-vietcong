"""Init.

Revision ID: 435e7055a710
Revises: 
Create Date: 2018-01-04 04:40:13.817406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '435e7055a710'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('map',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('mode',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('mapmode',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('map_id', sa.Integer(), nullable=True),
    sa.Column('mode_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['map_id'], ['map.id'], ),
    sa.ForeignKeyConstraint(['mode_id'], ['mode.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mapmode_map_id'), 'mapmode', ['map_id'], unique=False)
    op.create_index(op.f('ix_mapmode_mode_id'), 'mapmode', ['mode_id'], unique=False)
    op.create_table('server',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ip', sa.String(), nullable=True),
    sa.Column('infoport', sa.Integer(), nullable=True),
    sa.Column('port', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('map_id', sa.Integer(), nullable=True),
    sa.Column('mode_id', sa.Integer(), nullable=True),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('countryname', sa.String(), nullable=True),
    sa.Column('version', sa.String(), nullable=True),
    sa.Column('hradba', sa.String(), nullable=True),
    sa.Column('numplayers', sa.Integer(), nullable=True),
    sa.Column('maxplayers', sa.Integer(), nullable=True),
    sa.Column('password', sa.Boolean(), nullable=True),
    sa.Column('dedic', sa.Boolean(), nullable=True),
    sa.Column('vietnam', sa.Boolean(), nullable=True),
    sa.Column('online', sa.Boolean(), nullable=True),
    sa.Column('onlineSince', sa.DateTime(), nullable=True),
    sa.Column('offlineSince', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['map_id'], ['map.id'], ),
    sa.ForeignKeyConstraint(['mode_id'], ['mode.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_server_map_id'), 'server', ['map_id'], unique=False)
    op.create_index(op.f('ix_server_mode_id'), 'server', ['mode_id'], unique=False)
    op.create_table('player',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('ping', sa.Integer(), nullable=True),
    sa.Column('frags', sa.Integer(), nullable=True),
    sa.Column('server_id', sa.Integer(), nullable=True),
    sa.Column('online', sa.Boolean(), nullable=True),
    sa.Column('onlineSince', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['server_id'], ['server.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_player_server_id'), 'player', ['server_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_player_server_id'), table_name='player')
    op.drop_table('player')
    op.drop_index(op.f('ix_server_mode_id'), table_name='server')
    op.drop_index(op.f('ix_server_map_id'), table_name='server')
    op.drop_table('server')
    op.drop_index(op.f('ix_mapmode_mode_id'), table_name='mapmode')
    op.drop_index(op.f('ix_mapmode_map_id'), table_name='mapmode')
    op.drop_table('mapmode')
    op.drop_table('mode')
    op.drop_table('map')
    # ### end Alembic commands ###
