import uuid
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bond import Bond, MarketSource
from app.models.quote import Quote
from tests.conftest import run_async


class TestAggregatedQuotes:
    def test_multi_source_aggregation_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond: Bond,
        market_sources: list[MarketSource],
        multi_source_quotes: list[Quote],
    ):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["bond"]["id"] == str(test_bond.id)
        assert data["bond"]["code"] == test_bond.code
        assert data["bond"]["name"] == test_bond.name
        assert data["total_quotes"] == 6

        source_names = {s["source_name"] for s in data["sources"]}
        expected_sources = {"银行间xBond", "中诚宝捷思", "平安利顺", "上交所"}
        assert source_names == expected_sources
        assert len(data["sources"]) == 4

        for source in data["sources"]:
            if source["source_name"] == "银行间xBond":
                assert source["quote_count"] == 2
                assert source["best_bid_price"] == 100.28
                assert source["best_ask_price"] == 100.32
            elif source["source_name"] == "中诚宝捷思":
                assert source["quote_count"] == 2
                assert source["best_bid_price"] == 100.30
                assert source["best_ask_price"] == 100.38
            elif source["source_name"] == "平安利顺":
                assert source["quote_count"] == 1
                assert source["best_bid_price"] == 100.20
                assert source["best_ask_price"] == 100.30
            elif source["source_name"] == "上交所":
                assert source["quote_count"] == 1
                assert source["best_bid_price"] == 100.27
                assert source["best_ask_price"] == 100.33

    def test_single_source_aggregation(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond: Bond,
        market_sources: list[MarketSource],
        single_source_quotes: list[Quote],
    ):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert len(data["sources"]) == 1
        assert data["sources"][0]["source_name"] == "银行间xBond"
        assert data["sources"][0]["quote_count"] == 3
        assert data["total_quotes"] == 3

    def test_source_aggregation_includes_type(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond: Bond,
        market_sources: list[MarketSource],
        single_source_quotes: list[Quote],
    ):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["sources"][0]["source_type"] == "xbond"

    def test_unauthorized_access(self, client: TestClient, test_bond: Bond):
        response = client.get(f"/api/bonds/{test_bond.id}/aggregated")
        assert response.status_code == 401

    def test_invalid_token(self, client: TestClient, test_bond: Bond):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401


class TestBestPriceDetermination:
    def test_best_bid_price_is_maximum(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond: Bond,
        market_sources: list[MarketSource],
        multi_source_quotes: list[Quote],
    ):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["best_bid_price"] == 100.30

    def test_best_ask_price_is_minimum(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond: Bond,
        market_sources: list[MarketSource],
        multi_source_quotes: list[Quote],
    ):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["best_ask_price"] == 100.30

    def test_best_bid_yield_is_maximum(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond: Bond,
        market_sources: list[MarketSource],
        multi_source_quotes: list[Quote],
    ):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["best_bid_yield"] == 2.27

    def test_best_ask_yield_is_minimum(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond: Bond,
        market_sources: list[MarketSource],
        multi_source_quotes: list[Quote],
    ):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["best_ask_yield"] == 2.21

    def test_spread_calculation(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond: Bond,
        market_sources: list[MarketSource],
        multi_source_quotes: list[Quote],
    ):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        expected_spread = round(100.30 - 100.30, 4)
        assert data["spread"] == expected_spread

    def test_spread_calculation_single_source(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond: Bond,
        market_sources: list[MarketSource],
        single_source_quotes: list[Quote],
    ):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        best_bid = 100.30
        best_ask = 100.30
        expected_spread = round(best_ask - best_bid, 4)
        assert data["best_bid_price"] == best_bid
        assert data["best_ask_price"] == best_ask
        assert data["spread"] == expected_spread

    def test_partial_quotes_best_price(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond: Bond,
        market_sources: list[MarketSource],
        partial_quotes: list[Quote],
    ):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["best_bid_price"] == 100.25
        assert data["best_ask_price"] == 100.35
        assert data["best_bid_yield"] == 2.25
        assert data["best_ask_yield"] == 2.23

        expected_spread = round(100.35 - 100.25, 4)
        assert data["spread"] == expected_spread

    def test_best_prices_from_different_sources(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_bond: Bond,
        market_sources: list[MarketSource],
    ):
        xbond, broker1, broker2, exchange = market_sources
        now = datetime.utcnow()

        async def setup_data():
            quotes = [
                Quote(
                    id=uuid.uuid4(),
                    bond_id=test_bond.id,
                    source_id=xbond.id,
                    bid_price=100.25,
                    ask_price=100.40,
                    bid_yield=2.25,
                    ask_yield=2.20,
                    bid_volume=10000,
                    ask_volume=10000,
                    counterparty=xbond.name,
                    quote_time=now,
                ),
                Quote(
                    id=uuid.uuid4(),
                    bond_id=test_bond.id,
                    source_id=broker1.id,
                    bid_price=100.30,
                    ask_price=100.35,
                    bid_yield=2.24,
                    ask_yield=2.21,
                    bid_volume=10000,
                    ask_volume=10000,
                    counterparty=broker1.name,
                    quote_time=now,
                ),
                Quote(
                    id=uuid.uuid4(),
                    bond_id=test_bond.id,
                    source_id=exchange.id,
                    bid_price=100.28,
                    ask_price=100.32,
                    bid_yield=2.26,
                    ask_yield=2.19,
                    bid_volume=10000,
                    ask_volume=10000,
                    counterparty=exchange.name,
                    quote_time=now,
                ),
            ]
            for q in quotes:
                db_session.add(q)
            await db_session.commit()

        run_async(setup_data())

        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["best_bid_price"] == 100.30
        assert data["best_ask_price"] == 100.32
        assert data["best_bid_yield"] == 2.26
        assert data["best_ask_yield"] == 2.19

        source_best_bid = None
        source_best_ask = None
        for s in data["sources"]:
            if s["source_name"] == "中诚宝捷思":
                source_best_bid = s["best_bid_price"]
            if s["source_name"] == "上交所":
                source_best_ask = s["best_ask_price"]

        assert source_best_bid == 100.30
        assert source_best_ask == 100.32


class TestBondNotFound:
    def test_nonexistent_bond_returns_404(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        fake_id = uuid.uuid4()
        response = client.get(
            f"/api/bonds/{fake_id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "债券不存在"

    def test_invalid_bond_id_format(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        response = client.get(
            "/api/bonds/invalid-uuid-format/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestNoQuotesScenario:
    def test_bond_without_quotes_returns_empty_sources(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond_no_quotes: Bond,
    ):
        response = client.get(
            f"/api/bonds/{test_bond_no_quotes.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["bond"]["id"] == str(test_bond_no_quotes.id)
        assert data["bond"]["code"] == test_bond_no_quotes.code
        assert data["sources"] == []
        assert data["total_quotes"] == 0
        assert data["best_bid_price"] is None
        assert data["best_ask_price"] is None
        assert data["best_bid_yield"] is None
        assert data["best_ask_yield"] is None
        assert data["spread"] is None

    def test_bond_without_quotes_spread_is_none(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond_no_quotes: Bond,
    ):
        response = client.get(
            f"/api/bonds/{test_bond_no_quotes.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["spread"] is None

    def test_bond_with_only_bid_no_ask(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_bond: Bond,
        market_sources: list[MarketSource],
    ):
        xbond = market_sources[0]
        now = datetime.utcnow()

        async def setup_data():
            quote = Quote(
                id=uuid.uuid4(),
                bond_id=test_bond.id,
                source_id=xbond.id,
                bid_price=100.25,
                ask_price=None,
                bid_yield=2.25,
                ask_yield=None,
                bid_volume=10000,
                ask_volume=None,
                counterparty=xbond.name,
                quote_time=now,
            )
            db_session.add(quote)
            await db_session.commit()

        run_async(setup_data())

        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["best_bid_price"] == 100.25
        assert data["best_ask_price"] is None
        assert data["spread"] is None
        assert data["total_quotes"] == 1

    def test_bond_with_only_ask_no_bid(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_bond: Bond,
        market_sources: list[MarketSource],
    ):
        xbond = market_sources[0]
        now = datetime.utcnow()

        async def setup_data():
            quote = Quote(
                id=uuid.uuid4(),
                bond_id=test_bond.id,
                source_id=xbond.id,
                bid_price=None,
                ask_price=100.35,
                bid_yield=None,
                ask_yield=2.23,
                bid_volume=None,
                ask_volume=10000,
                counterparty=xbond.name,
                quote_time=now,
            )
            db_session.add(quote)
            await db_session.commit()

        run_async(setup_data())

        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["best_bid_price"] is None
        assert data["best_ask_price"] == 100.35
        assert data["spread"] is None
        assert data["total_quotes"] == 1


class TestSourceQuoteSummary:
    def test_latest_quote_time_per_source(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond: Bond,
        market_sources: list[MarketSource],
        multi_source_quotes: list[Quote],
    ):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        for source in data["sources"]:
            assert "latest_quote_time" in source
            assert source["latest_quote_time"] is not None

    def test_source_summary_best_prices(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond: Bond,
        market_sources: list[MarketSource],
        single_source_quotes: list[Quote],
    ):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        source = data["sources"][0]
        assert source["best_bid_price"] == 100.30
        assert source["best_ask_price"] == 100.30
        assert source["best_bid_yield"] == 2.30
        assert source["best_ask_yield"] == 2.24

    def test_partial_source_quotes_summary(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond: Bond,
        market_sources: list[MarketSource],
        partial_quotes: list[Quote],
    ):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        xbond_source = next(s for s in data["sources"] if s["source_name"] == "银行间xBond")
        broker_source = next(s for s in data["sources"] if s["source_name"] == "中诚宝捷思")

        assert xbond_source["best_bid_price"] == 100.25
        assert xbond_source["best_ask_price"] is None
        assert xbond_source["best_bid_yield"] == 2.25
        assert xbond_source["best_ask_yield"] is None

        assert broker_source["best_bid_price"] is None
        assert broker_source["best_ask_price"] == 100.35
        assert broker_source["best_bid_yield"] is None
        assert broker_source["best_ask_yield"] == 2.23


class TestBondBasicInfo:
    def test_bond_basic_info_complete(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond: Bond,
        market_sources: list[MarketSource],
        multi_source_quotes: list[Quote],
    ):
        response = client.get(
            f"/api/bonds/{test_bond.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        bond_info = data["bond"]
        assert bond_info["id"] == str(test_bond.id)
        assert bond_info["code"] == test_bond.code
        assert bond_info["name"] == test_bond.name
        assert bond_info["bond_type"] == test_bond.bond_type
        assert bond_info["coupon_rate"] == float(test_bond.coupon_rate)
        assert bond_info["remaining_term"] == float(test_bond.remaining_term)

    def test_bond_basic_info_no_quotes(
        self,
        client: TestClient,
        auth_headers: dict,
        test_bond_no_quotes: Bond,
    ):
        response = client.get(
            f"/api/bonds/{test_bond_no_quotes.id}/aggregated",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        bond_info = data["bond"]
        assert bond_info["id"] == str(test_bond_no_quotes.id)
        assert bond_info["code"] == test_bond_no_quotes.code
        assert bond_info["name"] == test_bond_no_quotes.name
        assert bond_info["bond_type"] == test_bond_no_quotes.bond_type
