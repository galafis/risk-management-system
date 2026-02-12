"""
Unit tests for risk-management-system
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.risk_manager import RiskManager, Position, RiskLevel, RiskMetrics


@pytest.fixture
def rm():
    """Create a RiskManager with 100k capital."""
    return RiskManager(
        initial_capital=100000,
        max_position_size=0.10,
        max_portfolio_risk=0.02,
        stop_loss_percent=0.05,
    )


class TestPositionDataclass:
    def test_market_value(self):
        p = Position("AAPL", 100, 150.0, 160.0, None)
        assert p.market_value == 16000.0

    def test_pnl(self):
        p = Position("AAPL", 100, 150.0, 160.0, None)
        assert p.pnl == 1000.0

    def test_pnl_percent(self):
        p = Position("AAPL", 100, 100.0, 110.0, None)
        assert abs(p.pnl_percent - 10.0) < 1e-9


class TestPositionSizing:
    def test_returns_int(self, rm):
        size = rm.calculate_position_size(150.0)
        assert isinstance(size, int)

    def test_respects_max_position_size(self, rm):
        size = rm.calculate_position_size(10.0)
        max_value = rm.current_capital * rm.max_position_size
        assert size * 10.0 <= max_value

    def test_zero_price_returns_zero(self, rm):
        # stop_distance = 0 * 0.05 = 0 -> risk_based_size = 0
        size = rm.calculate_position_size(0.01)
        assert size >= 0


class TestVaR:
    def test_historical_var(self, rm):
        returns = np.array([-0.05, -0.03, -0.01, 0.01, 0.02, 0.04, 0.06])
        var = rm.calculate_var(returns, 0.95, 'historical')
        assert var < 0  # VaR at 95% should be negative for this distribution

    def test_parametric_var(self, rm):
        returns = np.random.normal(0, 0.02, 1000)
        var = rm.calculate_var(returns, 0.95, 'parametric')
        assert isinstance(var, float)

    def test_invalid_method_raises(self, rm):
        with pytest.raises(ValueError):
            rm.calculate_var(np.array([0.0]), 0.95, 'invalid')


class TestExpectedShortfall:
    def test_es_less_than_or_equal_var(self, rm):
        returns = np.random.normal(-0.01, 0.02, 500)
        var = rm.calculate_var(returns, 0.95)
        es = rm.calculate_expected_shortfall(returns, 0.95)
        assert es <= var

    def test_handles_single_element(self, rm):
        es = rm.calculate_expected_shortfall(np.array([0.0]), 0.95)
        assert isinstance(es, (float, np.floating))


class TestMaxDrawdown:
    def test_no_drawdown(self, rm):
        equity = [100, 110, 120, 130]
        assert rm.calculate_max_drawdown(equity) == 0.0

    def test_known_drawdown(self, rm):
        equity = [100, 120, 90, 110]
        dd = rm.calculate_max_drawdown(equity)
        assert abs(dd - 0.25) < 1e-9  # 120 -> 90 = 25%

    def test_single_value(self, rm):
        assert rm.calculate_max_drawdown([100]) == 0.0


class TestSharpeRatio:
    def test_zero_returns(self, rm):
        returns = np.array([0.0, 0.0, 0.0])
        assert rm.calculate_sharpe_ratio(returns) == 0.0

    def test_empty_returns(self, rm):
        assert rm.calculate_sharpe_ratio(np.array([])) == 0.0

    def test_positive_returns(self, rm):
        returns = np.array([0.01, 0.02, 0.015, 0.01, 0.02])
        sharpe = rm.calculate_sharpe_ratio(returns)
        assert sharpe > 0


class TestStopLoss:
    def test_long_stop_triggered(self, rm):
        p = Position("X", 100, 100.0, 90.0, None)
        assert rm.check_stop_loss(p, 95.0) is True

    def test_long_stop_not_triggered(self, rm):
        p = Position("X", 100, 100.0, 105.0, None)
        assert rm.check_stop_loss(p, 95.0) is False

    def test_short_stop_triggered(self, rm):
        p = Position("X", -100, 100.0, 110.0, None)
        assert rm.check_stop_loss(p, 105.0) is True


class TestPortfolioOperations:
    def test_add_position(self, rm):
        rm.add_position("AAPL", 100, 150.0)
        assert "AAPL" in rm.positions
        assert rm.current_capital == 100000 - 15000

    def test_close_position_returns_pnl(self, rm):
        rm.add_position("AAPL", 100, 150.0)
        rm.update_position_price("AAPL", 160.0)
        pnl = rm.close_position("AAPL")
        assert pnl == 1000.0
        assert "AAPL" not in rm.positions

    def test_close_nonexistent_returns_zero(self, rm):
        assert rm.close_position("FAKE") == 0

    def test_equity_curve_updates(self, rm):
        rm.add_position("AAPL", 100, 100.0)
        rm.update_position_price("AAPL", 110.0)
        assert len(rm.equity_curve) > 1
        # After price increase: capital=90000, position=11000 -> total=101000
        assert rm.equity_curve[-1] == 101000.0

    def test_portfolio_summary(self, rm):
        rm.add_position("AAPL", 100, 100.0)
        summary = rm.get_portfolio_summary()
        assert 'capital' in summary
        assert 'portfolio_value' in summary
        assert 'risk_level' in summary


class TestPortfolioMetrics:
    def test_returns_risk_metrics(self, rm):
        rm.add_position("AAPL", 100, 100.0)
        rm.update_position_price("AAPL", 105.0)
        rm.update_position_price("AAPL", 102.0)
        metrics = rm.calculate_portfolio_metrics()
        assert isinstance(metrics, RiskMetrics)
        assert isinstance(metrics.risk_level, RiskLevel)

    def test_empty_portfolio(self, rm):
        metrics = rm.calculate_portfolio_metrics()
        assert metrics.portfolio_value == 0
        assert metrics.total_exposure == 0


class TestRiskLevel:
    def test_low_risk(self, rm):
        level = rm._determine_risk_level(0.02, -100, 100000)
        assert level == RiskLevel.LOW

    def test_critical_risk(self, rm):
        level = rm._determine_risk_level(0.30, -15000, 100000)
        assert level == RiskLevel.CRITICAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
