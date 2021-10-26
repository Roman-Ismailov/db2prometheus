"""v1.0.0

Revision ID: 82597dc4f5f1
Revises: 
Create Date: 2021-10-26 02:17:35.186887

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82597dc4f5f1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('base_metrics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.Column('metric_name', sa.String(length=64), nullable=False),
    sa.Column('last_update_date', sa.DateTime(), nullable=False),
    sa.Column('description', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__base_metrics'))
    )
    op.create_table('histograms',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('metric_name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__histograms'))
    )
    op.create_table('buckets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('histogram_id', sa.Integer(), nullable=True),
    sa.Column('bucket_value', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['histogram_id'], ['histograms.id'], name=op.f('fk__buckets__histogram_id__histograms')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__buckets'))
    )
    op.create_table('gauges',
    sa.Column('id', sa.Integer(), sa.Identity(always=False, start=1), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['base_metrics.id'], name=op.f('fk__gauges__id__base_metrics')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__gauges'))
    )
    op.create_table('labels',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('metric_id', sa.Integer(), nullable=True),
    sa.Column('label_name', sa.String(length=64), nullable=False),
    sa.Column('label_value', sa.String(length=64), nullable=False),
    sa.ForeignKeyConstraint(['metric_id'], ['base_metrics.id'], name=op.f('fk__labels__metric_id__base_metrics')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__labels'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('labels')
    op.drop_table('gauges')
    op.drop_table('buckets')
    op.drop_table('histograms')
    op.drop_table('base_metrics')
    # ### end Alembic commands ###