import asyncio
import uuid
from datetime import datetime, date, timedelta
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.database import Base, get_db
from app.main import app
from app.models.bond import Bond, MarketSource
from app.models.quote import Quote
from app.models.user import User
from app.api.auth import create_access_token

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=False, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def run_async(coro):
    loop = asyncio.get_event_loop_policy().get_event_loop()
    return loop.run_until_complete(coro)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        username="testuser",
        password_hash=pwd_context.hash("testpass123"),
        display_name="测试用户",
        role="trader",
        department="测试部门",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user: User) -> dict:
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def test_bond(db_session: AsyncSession) -> Bond:
    bond = Bond(
        id=uuid.uuid4(),
        code="24TEST001.IB",
        name="24测试债01",
        full_name="2024年测试债券第一期",
        bond_type="国债",
        issuer="财政部",
        coupon_rate=2.2850,
        coupon_type="固定利率",
        credit_rating="AAA",
        remaining_term=9.5,
        issue_date=date(2024, 3, 20),
        maturity_date=date(2034, 3, 20),
        face_value=100.0,
    )
    db_session.add(bond)
    await db_session.commit()
    await db_session.refresh(bond)
    return bond


@pytest_asyncio.fixture(scope="function")
async def test_bond_no_quotes(db_session: AsyncSession) -> Bond:
    bond = Bond(
        id=uuid.uuid4(),
        code="24TEST002.IB",
        name="24测试债02",
        full_name="2024年测试债券第二期（无报价）",
        bond_type="国债",
        issuer="财政部",
        coupon_rate=2.5700,
        coupon_type="固定利率",
        credit_rating="AAA",
        remaining_term=5.0,
        issue_date=date(2024, 1, 1),
        maturity_date=date(2029, 1, 1),
        face_value=100.0,
    )
    db_session.add(bond)
    await db_session.commit()
    await db_session.refresh(bond)
    return bond


@pytest_asyncio.fixture(scope="function")
async def market_sources(db_session: AsyncSession) -> list[MarketSource]:
    now = datetime.utcnow()
    sources_data = [
        {"name": "银行间xBond", "source_type": "xbond", "status": "online", "is_enabled": True},
        {"name": "中诚宝捷思", "source_type": "broker", "status": "online", "is_enabled": True},
        {"name": "平安利顺", "source_type": "broker", "status": "online", "is_enabled": True},
        {"name": "上交所", "source_type": "exchange", "status": "online", "is_enabled": True},
    ]
    sources = []
    for s in sources_data:
        source = MarketSource(
            id=uuid.uuid4(),
            **s,
            description=f"{s['name']}数据源",
            last_heartbeat=now,
            avg_latency_ms=10.0,
            health_score=95.0,
        )
        db_session.add(source)
        sources.append(source)
    await db_session.commit()
    for source in sources:
        await db_session.refresh(source)
    return sources


@pytest_asyncio.fixture(scope="function")
async def multi_source_quotes(
    db_session: AsyncSession,
    test_bond: Bond,
    market_sources: list[MarketSource],
) -> list[Quote]:
    now = datetime.utcnow()
    xbond, broker1, broker2, exchange = market_sources

    quotes_data = [
        {"source": xbond, "bid": 100.25, "ask": 100.35, "bid_y": 2.25, "ask_y": 2.23, "time": now - timedelta(minutes=5)},
        {"source": xbond, "bid": 100.28, "ask": 100.32, "bid_y": 2.24, "ask_y": 2.22, "time": now - timedelta(minutes=2)},
        {"source": broker1, "bid": 100.22, "ask": 100.38, "bid_y": 2.26, "ask_y": 2.24, "time": now - timedelta(minutes=10)},
        {"source": broker1, "bid": 100.30, "ask": 100.40, "bid_y": 2.23, "ask_y": 2.21, "time": now - timedelta(minutes=1)},
        {"source": broker2, "bid": 100.20, "ask": 100.30, "bid_y": 2.27, "ask_y": 2.25, "time": now - timedelta(minutes=8)},
        {"source": exchange, "bid": 100.27, "ask": 100.33, "bid_y": 2.245, "ask_y": 2.225, "time": now - timedelta(minutes=3)},
    ]

    quotes = []
    for qd in quotes_data:
        quote = Quote(
            id=uuid.uuid4(),
            bond_id=test_bond.id,
            source_id=qd["source"].id,
            bid_price=qd["bid"],
            ask_price=qd["ask"],
            bid_yield=qd["bid_y"],
            ask_yield=qd["ask_y"],
            bid_volume=10000.0,
            ask_volume=10000.0,
            counterparty=qd["source"].name,
            quote_time=qd["time"],
            is_best=False,
        )
        db_session.add(quote)
        quotes.append(quote)

    await db_session.commit()
    for quote in quotes:
        await db_session.refresh(quote)
    return quotes


@pytest_asyncio.fixture(scope="function")
async def single_source_quotes(
    db_session: AsyncSession,
    test_bond: Bond,
    market_sources: list[MarketSource],
) -> list[Quote]:
    now = datetime.utcnow()
    xbond = market_sources[0]

    quotes = []
    for i in range(3):
        quote = Quote(
            id=uuid.uuid4(),
            bond_id=test_bond.id,
            source_id=xbond.id,
            bid_price=100.20 + i * 0.05,
            ask_price=100.40 - i * 0.05,
            bid_yield=2.30 - i * 0.02,
            ask_yield=2.20 + i * 0.02,
            bid_volume=5000.0,
            ask_volume=5000.0,
            counterparty=xbond.name,
            quote_time=now - timedelta(minutes=i),
            is_best=(i == 0),
        )
        db_session.add(quote)
        quotes.append(quote)

    await db_session.commit()
    for quote in quotes:
        await db_session.refresh(quote)
    return quotes


@pytest_asyncio.fixture(scope="function")
async def partial_quotes(
    db_session: AsyncSession,
    test_bond: Bond,
    market_sources: list[MarketSource],
) -> list[Quote]:
    now = datetime.utcnow()
    xbond, broker1, *_ = market_sources

    quotes_data = [
        {"source": xbond, "bid": 100.25, "ask": None, "bid_y": 2.25, "ask_y": None},
        {"source": broker1, "bid": None, "ask": 100.35, "bid_y": None, "ask_y": 2.23},
    ]

    quotes = []
    for qd in quotes_data:
        quote = Quote(
            id=uuid.uuid4(),
            bond_id=test_bond.id,
            source_id=qd["source"].id,
            bid_price=qd["bid"],
            ask_price=qd["ask"],
            bid_yield=qd["bid_y"],
            ask_yield=qd["ask_y"],
            bid_volume=10000.0 if qd["bid"] else None,
            ask_volume=10000.0 if qd["ask"] else None,
            counterparty=qd["source"].name,
            quote_time=now,
            is_best=True,
        )
        db_session.add(quote)
        quotes.append(quote)

    await db_session.commit()
    for quote in quotes:
        await db_session.refresh(quote)
    return quotes
