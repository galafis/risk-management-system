"""
Portfolio Risk Management Demo
Demonstrates risk management features for a trading portfolio.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.risk_manager import RiskManager


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def main():
    print_header("Portfolio Risk Management System - Demo")

    # Initialize risk manager
    rm = RiskManager(
        initial_capital=100000,
        max_position_size=0.10,
        max_portfolio_risk=0.02,
        stop_loss_percent=0.05,
    )

    print(f"Initial Capital: ${rm.initial_capital:,.2f}")
    print(f"Max Position Size: {rm.max_position_size*100:.1f}%")
    print(f"Max Portfolio Risk: {rm.max_portfolio_risk*100:.1f}%")
    print(f"Stop Loss: {rm.stop_loss_percent*100:.1f}%")

    # Add positions to portfolio
    print_header("Building Portfolio")

    positions = [
        ("AAPL", 100, 150.0),
        ("GOOGL", 20, 2800.0),
        ("MSFT", 150, 350.0),
        ("TSLA", 75, 250.0),
        ("NVDA", 80, 450.0),
    ]

    for symbol, quantity, price in positions:
        rm.add_position(symbol, quantity, price)
        print(f"  Added {symbol}: {quantity} shares @ ${price:.2f} = ${quantity*price:,.2f}")

    # Simulate price changes to build equity curve
    print_header("Simulating Price Changes")

    price_updates = [
        {"AAPL": 152.0, "GOOGL": 2820.0, "MSFT": 355.0, "TSLA": 245.0, "NVDA": 460.0},
        {"AAPL": 155.0, "GOOGL": 2790.0, "MSFT": 348.0, "TSLA": 240.0, "NVDA": 465.0},
        {"AAPL": 153.0, "GOOGL": 2810.0, "MSFT": 352.0, "TSLA": 235.0, "NVDA": 455.0},
    ]

    for i, updates in enumerate(price_updates, 1):
        for symbol, price in updates.items():
            rm.update_position_price(symbol, price)
        total = rm.current_capital + sum(p.market_value for p in rm.positions.values())
        print(f"  Day {i}: portfolio value = ${total:,.2f}")

    # Calculate risk metrics
    print_header("Risk Metrics")

    metrics = rm.calculate_portfolio_metrics()

    print(f"Portfolio Value:      ${metrics.portfolio_value:,.2f}")
    print(f"Total Exposure:       ${metrics.total_exposure:,.2f}")
    print(f"Risk Level:           {metrics.risk_level.value}")
    print()
    print(f"VaR (95%):            ${metrics.var_95:,.2f}")
    print(f"VaR (99%):            ${metrics.var_99:,.2f}")
    print(f"Expected Shortfall:   ${metrics.expected_shortfall:,.2f}")
    print()
    print(f"Max Drawdown:         {metrics.max_drawdown*100:.2f}%")
    print(f"Sharpe Ratio:         {metrics.sharpe_ratio:.4f}")
    print(f"Annualized Volatility:{metrics.volatility*100:.2f}%")

    # Position sizing recommendation
    print_header("Position Sizing Recommendation")

    new_price = 180.0
    recommended_size = rm.calculate_position_size(new_price)
    recommended_value = recommended_size * new_price

    print(f"For a new position at ${new_price:.2f}:")
    print(f"  Recommended Size:  {recommended_size} shares")
    print(f"  Position Value:    ${recommended_value:,.2f}")

    # Stop-loss monitoring
    print_header("Stop-Loss Monitoring")

    for symbol in ["TSLA", "NVDA"]:
        pos = rm.positions[symbol]
        stop_price = pos.entry_price * (1 - rm.stop_loss_percent)
        triggered = rm.check_stop_loss(pos, stop_price)
        status = "TRIGGERED" if triggered else "OK"
        print(f"  {symbol}: current=${pos.current_price:.2f}, "
              f"stop=${stop_price:.2f} -> {status}")

    # Portfolio summary
    print_header("Final Portfolio Summary")

    summary = rm.get_portfolio_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  {key}: {value:,.2f}")
        else:
            print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("  Risk Management Demo Complete")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
