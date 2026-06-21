"""initial migration

Revision ID: 000000000001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '000000000001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BOND_TYPE_ENUM = postgresql.ENUM(
    '国债', '政金债', '企业债', '公司债', '可转债', '地方债', '同业存单',
    name='bond_type_enum', create_type=False,
)
COUPON_TYPE_ENUM = postgresql.ENUM(
    '固定利率', '浮动利率', '零息', '贴现',
    name='coupon_type_enum', create_type=False,
)
SOURCE_TYPE_ENUM = postgresql.ENUM(
    'xbond', 'broker', 'exchange', 'swap', 'futures',
    name='source_type_enum', create_type=False,
)
SOURCE_STATUS_ENUM = postgresql.ENUM(
    'online', 'offline', 'error',
    name='source_status_enum', create_type=False,
)
TRADE_DIRECTION_ENUM = postgresql.ENUM(
    'buy', 'sell',
    name='trade_direction_enum', create_type=False,
)
FUTURES_TYPE_ENUM = postgresql.ENUM(
    'T', 'TF', 'TS',
    name='futures_type_enum', create_type=False,
)
SWAP_DIRECTION_ENUM = postgresql.ENUM(
    'pay_fixed', 'receive_fixed',
    name='swap_direction_enum', create_type=False,
)
USER_ROLE_ENUM = postgresql.ENUM(
    'admin', 'trader', 'viewer',
    name='user_role_enum', create_type=False,
)
RATING_CHANGE_TYPE_ENUM = postgresql.ENUM(
    'upgrade', 'downgrade', 'outlook',
    name='rating_change_type_enum', create_type=False,
)


def upgrade() -> None:
    # asyncpg 不支持在单条 prepared statement 中执行多条 SQL，需逐条执行
    op.execute("CREATE TYPE bond_type_enum AS ENUM ('国债', '政金债', '企业债', '公司债', '可转债', '地方债', '同业存单')")
    op.execute("CREATE TYPE coupon_type_enum AS ENUM ('固定利率', '浮动利率', '零息', '贴现')")
    op.execute("CREATE TYPE source_type_enum AS ENUM ('xbond', 'broker', 'exchange', 'swap', 'futures')")
    op.execute("CREATE TYPE source_status_enum AS ENUM ('online', 'offline', 'error')")
    op.execute("CREATE TYPE trade_direction_enum AS ENUM ('buy', 'sell')")
    op.execute("CREATE TYPE futures_type_enum AS ENUM ('T', 'TF', 'TS')")
    op.execute("CREATE TYPE swap_direction_enum AS ENUM ('pay_fixed', 'receive_fixed')")
    op.execute("CREATE TYPE user_role_enum AS ENUM ('admin', 'trader', 'viewer')")
    op.execute("CREATE TYPE rating_change_type_enum AS ENUM ('upgrade', 'downgrade', 'outlook')")

    op.create_table(
        'bonds',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=True),
        sa.Column('bond_type', BOND_TYPE_ENUM, nullable=False),
        sa.Column('issuer', sa.String(length=200), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('maturity_date', sa.Date(), nullable=True),
        sa.Column('coupon_rate', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('coupon_type', COUPON_TYPE_ENUM, nullable=True),
        sa.Column('face_value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('credit_rating', sa.String(length=10), nullable=True),
        sa.Column('remaining_term', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bonds_code'), 'bonds', ['code'], unique=True)
    op.create_index(op.f('ix_bonds_name'), 'bonds', ['name'], unique=False)

    op.create_table(
        'market_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('source_type', SOURCE_TYPE_ENUM, nullable=False),
        sa.Column('status', SOURCE_STATUS_ENUM, nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=True),
        sa.Column('last_heartbeat', sa.DateTime(), nullable=True),
        sa.Column('avg_latency_ms', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('today_missing_quotes', sa.Integer(), nullable=True),
        sa.Column('today_inverted_spreads', sa.Integer(), nullable=True),
        sa.Column('health_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=50), nullable=False),
        sa.Column('role', USER_ROLE_ENUM, nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('settings', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    op.create_table(
        'futures_quotes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contract_code', sa.String(length=20), nullable=False),
        sa.Column('contract_type', FUTURES_TYPE_ENUM, nullable=False),
        sa.Column('latest_price', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('settlement_price', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('open_price', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('high_price', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('low_price', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('prev_close', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('change_pct', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('volume', sa.Integer(), nullable=True),
        sa.Column('open_interest', sa.Integer(), nullable=True),
        sa.Column('basis', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('quote_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_futures_quotes_contract_code'), 'futures_quotes', ['contract_code'], unique=False)
    op.create_index(op.f('ix_futures_quotes_quote_time'), 'futures_quotes', ['quote_time'], unique=False)

    op.create_table(
        'rating_changes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bond_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agency', sa.String(length=50), nullable=False),
        sa.Column('change_type', RATING_CHANGE_TYPE_ENUM, nullable=False),
        sa.Column('old_rating', sa.String(length=20), nullable=True),
        sa.Column('new_rating', sa.String(length=20), nullable=True),
        sa.Column('old_outlook', sa.String(length=20), nullable=True),
        sa.Column('new_outlook', sa.String(length=20), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['bond_id'], ['bonds.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rating_changes_bond_id'), 'rating_changes', ['bond_id'], unique=False)
    op.create_index(op.f('ix_rating_changes_effective_date'), 'rating_changes', ['effective_date'], unique=False)

    op.create_table(
        'quotes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bond_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('bid_price', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('ask_price', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('bid_yield', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('ask_yield', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('bid_volume', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('ask_volume', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('counterparty', sa.String(length=100), nullable=True),
        sa.Column('quote_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_best', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['bond_id'], ['bonds.id'], ),
        sa.ForeignKeyConstraint(['source_id'], ['market_sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quotes_bond_id'), 'quotes', ['bond_id'], unique=False)
    op.create_index(op.f('ix_quotes_quote_time'), 'quotes', ['quote_time'], unique=False)
    op.create_index(op.f('ix_quotes_source_id'), 'quotes', ['source_id'], unique=False)

    op.create_table(
        'trades',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bond_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('price', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('yield_rate', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('volume', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('direction', TRADE_DIRECTION_ENUM, nullable=False),
        sa.Column('counterparty', sa.String(length=100), nullable=True),
        sa.Column('trade_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['bond_id'], ['bonds.id'], ),
        sa.ForeignKeyConstraint(['source_id'], ['market_sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trades_bond_id'), 'trades', ['bond_id'], unique=False)
    op.create_index(op.f('ix_trades_source_id'), 'trades', ['source_id'], unique=False)
    op.create_index(op.f('ix_trades_trade_time'), 'trades', ['trade_time'], unique=False)

    op.create_table(
        'swap_quotes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bond_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('dealer', sa.String(length=100), nullable=False),
        sa.Column('swap_rate', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('tenor', sa.String(length=20), nullable=False),
        sa.Column('direction', SWAP_DIRECTION_ENUM, nullable=False),
        sa.Column('notional_min', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('quote_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['bond_id'], ['bonds.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_swap_quotes_bond_id'), 'swap_quotes', ['bond_id'], unique=False)
    op.create_index(op.f('ix_swap_quotes_quote_time'), 'swap_quotes', ['quote_time'], unique=False)

    op.create_table(
        'user_favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('bond_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['bond_id'], ['bonds.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'bond_id', name='uq_user_bond')
    )
    op.create_index(op.f('ix_user_favorites_bond_id'), 'user_favorites', ['bond_id'], unique=False)
    op.create_index(op.f('ix_user_favorites_user_id'), 'user_favorites', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_favorites_user_id'), table_name='user_favorites')
    op.drop_index(op.f('ix_user_favorites_bond_id'), table_name='user_favorites')
    op.drop_table('user_favorites')

    op.drop_index(op.f('ix_swap_quotes_quote_time'), table_name='swap_quotes')
    op.drop_index(op.f('ix_swap_quotes_bond_id'), table_name='swap_quotes')
    op.drop_table('swap_quotes')

    op.drop_index(op.f('ix_trades_trade_time'), table_name='trades')
    op.drop_index(op.f('ix_trades_source_id'), table_name='trades')
    op.drop_index(op.f('ix_trades_bond_id'), table_name='trades')
    op.drop_table('trades')

    op.drop_index(op.f('ix_quotes_source_id'), table_name='quotes')
    op.drop_index(op.f('ix_quotes_quote_time'), table_name='quotes')
    op.drop_index(op.f('ix_quotes_bond_id'), table_name='quotes')
    op.drop_table('quotes')

    op.drop_index(op.f('ix_rating_changes_effective_date'), table_name='rating_changes')
    op.drop_index(op.f('ix_rating_changes_bond_id'), table_name='rating_changes')
    op.drop_table('rating_changes')

    op.drop_index(op.f('ix_futures_quotes_quote_time'), table_name='futures_quotes')
    op.drop_index(op.f('ix_futures_quotes_contract_code'), table_name='futures_quotes')
    op.drop_table('futures_quotes')

    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')

    op.drop_table('market_sources')

    op.drop_index(op.f('ix_bonds_name'), table_name='bonds')
    op.drop_index(op.f('ix_bonds_code'), table_name='bonds')
    op.drop_table('bonds')

    op.execute("DROP TYPE IF EXISTS rating_change_type_enum")
    op.execute("DROP TYPE IF EXISTS user_role_enum")
    op.execute("DROP TYPE IF EXISTS swap_direction_enum")
    op.execute("DROP TYPE IF EXISTS futures_type_enum")
    op.execute("DROP TYPE IF EXISTS trade_direction_enum")
    op.execute("DROP TYPE IF EXISTS source_status_enum")
    op.execute("DROP TYPE IF EXISTS source_type_enum")
    op.execute("DROP TYPE IF EXISTS coupon_type_enum")
    op.execute("DROP TYPE IF EXISTS bond_type_enum")
