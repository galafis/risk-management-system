"""
Portfolio Risk Management Demo
Demonstrates comprehensive risk management for a trading portfolio
"""

from src.risk_manager import RiskManager
import numpy as np

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def main():
    print_header("Portfolio Risk Management System - Demo")
    
    # Initialize risk manager
    rm = RiskManager(
        initial_capital=100000,
        max_position_size=0.10,     # 10% max per position
        max_portfolio_risk=0.02,    # 2% risk per trade
        stop_loss_percent=0.05      # 5% stop-loss
    )
    
    print(f"Initial Capital: ${rm.initial_capital:,.2f}")
    print(f"Max Position Size: {rm.max_position_size*100:.1f}%")
    print(f"Max Portfolio Risk: {rm.max_portfolio_risk*100:.1f}%")
    print(f"Stop Loss: {rm.stop_loss_percent*100:.1f}%")
    
    # Add positions to portfolio
    print_header("Building Portfolio")
    
    positions = [
        ("AAPL", 100, 150.0, 0.25),
        ("GOOGL", 50, 2800.0, 0.30),
        ("MSFT", 150, 350.0, 0.22),
        ("TSLA", 75, 250.0, 0.45),
        ("NVDA", 80, 450.0, 0.35),
    ]
    
    for symbol, quantity, price, volatility in positions:
        rm.add_position(symbol, quantity, price)
        position_value = quantity * price
        print(f"✓ Added {symbol}: {quantity} shares @ ${price:.2f} = ${position_value:,.2f}")
    
    # Calculate risk metrics
    print_header("Risk Metrics")
    
    metrics = rm.get_risk_metrics()
    
    print(f"Portfolio Value:     ${metrics['portfolio_value']:,.2f}")
    print(f"Total Exposure:      ${metrics['total_exposure']:,.2f}")
    print(f"Cash Available:      ${metrics['cash_available']:,.2f}")
    print(f"Number of Positions: {metrics['num_positions']}")
    print()
    print(f"VaR (95%):          ${metrics['var_95']:,.2f}")
    print(f"VaR (99%):          ${metrics['var_99']:,.2f}")
    print(f"Expected Shortfall:  ${metrics['expected_shortfall']:,.2f}")
    print()
    print(f"Sharpe Ratio:        {metrics['sharpe_ratio']:.2f}")
    print(f"Max Drawdown:        {metrics['max_drawdown']*100:.2f}%")
    print(f"Portfolio Volatility: {metrics['volatility']*100:.2f}%")
    
    # Risk level assessment
    print_header("Risk Assessment")
    
    risk_level = rm.get_risk_level()
    risk_colors = {
        'LOW': '🟢',
        'MEDIUM': '🟡',
        'HIGH': '🟠',
        'CRITICAL': '🔴'
    }
    
    print(f"{risk_colors.get(risk_level, '⚪')} Risk Level: {risk_level}")
    
    if risk_level == 'CRITICAL':
        print("\n⚠️  WARNING: Portfolio risk is CRITICAL!")
        print("   Consider reducing positions or hedging")
    elif risk_level == 'HIGH':
        print("\n⚠️  CAUTION: Portfolio risk is HIGH")
        print("   Monitor closely and consider risk reduction")
    elif risk_level == 'MEDIUM':
        print("\n✓ Portfolio risk is at acceptable levels")
    else:
        print("\n✓ Portfolio risk is LOW - well managed")
    
    # Position sizing example
    print_header("Position Sizing Recommendation")
    
    new_symbol = "AMZN"
    new_price = 180.0
    new_volatility = 0.28
    
    recommended_size = rm.calculate_position_size(new_price, new_volatility)
    recommended_value = recommended_size * new_price
    
    print(f"For new position in {new_symbol}:")
    print(f"  Price: ${new_price:.2f}")
    print(f"  Volatility: {new_volatility*100:.1f}%")
    print(f"  Recommended Size: {recommended_size:.0f} shares")
    print(f"  Position Value: ${recommended_value:,.2f}")
    print(f"  % of Portfolio: {(recommended_value/metrics['portfolio_value'])*100:.2f}%")
    
    # Stop-loss monitoring
    print_header("Stop-Loss Monitoring")
    
    # Simulate price drops
    price_changes = [
        ("TSLA", 250.0, 235.0),  # -6% drop
        ("NVDA", 450.0, 440.0),  # -2.2% drop
    ]
    
    for symbol, old_price, new_price in price_changes:
        change_pct = ((new_price - old_price) / old_price) * 100
        rm.update_position_price(symbol, new_price)
        
        if rm.check_stop_loss(symbol):
            print(f"🔴 STOP-LOSS TRIGGERED: {symbol}")
            print(f"   Price: ${old_price:.2f} → ${new_price:.2f} ({change_pct:+.2f}%)")
            print(f"   Action: Close position immediately")
        else:
            print(f"✓ {symbol}: ${old_price:.2f} → ${new_price:.2f} ({change_pct:+.2f}%)")
    
    # Final summary
    print_header("Portfolio Summary")
    
    final_metrics = rm.get_risk_metrics()
    print(f"Final Portfolio Value: ${final_metrics['portfolio_value']:,.2f}")
    print(f"Total P&L: ${final_metrics['portfolio_value'] - rm.initial_capital:+,.2f}")
    print(f"Return: {((final_metrics['portfolio_value']/rm.initial_capital)-1)*100:+.2f}%")
    
    print("\n" + "="*60)
    print("  Risk Management Demo Complete")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
