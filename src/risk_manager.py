"""
Automated Risk Management System
Author: Gabriel Demetrios Lafis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class Position:
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    timestamp: datetime
    
    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price
    
    @property
    def pnl(self) -> float:
        return (self.current_price - self.entry_price) * self.quantity
    
    @property
    def pnl_percent(self) -> float:
        return (self.current_price / self.entry_price - 1) * 100

@dataclass
class RiskMetrics:
    portfolio_value: float
    total_exposure: float
    var_95: float
    var_99: float
    expected_shortfall: float
    max_drawdown: float
    sharpe_ratio: float
    volatility: float
    beta: float
    risk_level: RiskLevel

class RiskManager:
    """
    Comprehensive risk management system for trading portfolios.
    
    Features:
    - Position sizing and exposure limits
    - Value at Risk (VaR) calculation
    - Stop-loss management
    - Portfolio risk metrics
    - Real-time alerts
    """
    
    def __init__(self, 
                 initial_capital: float,
                 max_position_size: float = 0.1,
                 max_portfolio_risk: float = 0.02,
                 stop_loss_percent: float = 0.05):
        """
        Initialize Risk Manager.
        
        Args:
            initial_capital: Starting capital
            max_position_size: Maximum position size as % of portfolio (default 10%)
            max_portfolio_risk: Maximum portfolio risk per trade (default 2%)
            stop_loss_percent: Default stop-loss percentage (default 5%)
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_position_size = max_position_size
        self.max_portfolio_risk = max_portfolio_risk
        self.stop_loss_percent = stop_loss_percent
        
        self.positions: Dict[str, Position] = {}
        self.equity_curve: List[float] = [initial_capital]
        self.returns_history: List[float] = []
        
    def calculate_position_size(self, 
                                price: float, 
                                volatility: float,
                                risk_per_trade: Optional[float] = None) -> int:
        """
        Calculate optimal position size based on risk parameters.
        
        Args:
            price: Current price of asset
            volatility: Historical volatility
            risk_per_trade: Risk per trade (default: max_portfolio_risk)
            
        Returns:
            Number of shares/contracts to trade
        """
        if risk_per_trade is None:
            risk_per_trade = self.max_portfolio_risk
        
        # Maximum position value based on portfolio size
        max_position_value = self.current_capital * self.max_position_size
        
        # Position size based on risk
        risk_amount = self.current_capital * risk_per_trade
        stop_distance = price * self.stop_loss_percent
        risk_based_size = risk_amount / stop_distance if stop_distance > 0 else 0
        
        # Take minimum of both constraints
        max_shares = int(max_position_value / price)
        risk_shares = int(risk_based_size)
        
        return min(max_shares, risk_shares)
    
    def calculate_var(self, 
                     returns: np.ndarray, 
                     confidence_level: float = 0.95,
                     method: str = 'historical') -> float:
        """
        Calculate Value at Risk (VaR).
        
        Args:
            returns: Array of historical returns
            confidence_level: Confidence level (0.95 or 0.99)
            method: 'historical' or 'parametric'
            
        Returns:
            VaR value
        """
        if method == 'historical':
            return np.percentile(returns, (1 - confidence_level) * 100)
        elif method == 'parametric':
            mean = np.mean(returns)
            std = np.std(returns)
            z_score = -1.645 if confidence_level == 0.95 else -2.326
            return mean + z_score * std
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def calculate_expected_shortfall(self, 
                                    returns: np.ndarray, 
                                    confidence_level: float = 0.95) -> float:
        """
        Calculate Expected Shortfall (Conditional VaR).
        
        Args:
            returns: Array of historical returns
            confidence_level: Confidence level
            
        Returns:
            Expected Shortfall value
        """
        var = self.calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()
    
    def calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """
        Calculate maximum drawdown from equity curve.
        
        Args:
            equity_curve: List of portfolio values over time
            
        Returns:
            Maximum drawdown as percentage
        """
        peak = equity_curve[0]
        max_dd = 0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def calculate_sharpe_ratio(self, 
                              returns: np.ndarray, 
                              risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe Ratio.
        
        Args:
            returns: Array of returns
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Sharpe ratio (annualized)
        """
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)
        if np.std(excess_returns) == 0:
            return 0.0
        
        return np.sqrt(252) * np.mean(excess_returns) / np.std(excess_returns)
    
    def check_stop_loss(self, position: Position, stop_loss_price: float) -> bool:
        """
        Check if stop-loss has been triggered.
        
        Args:
            position: Position to check
            stop_loss_price: Stop-loss price level
            
        Returns:
            True if stop-loss triggered
        """
        if position.quantity > 0:  # Long position
            return position.current_price <= stop_loss_price
        else:  # Short position
            return position.current_price >= stop_loss_price
    
    def calculate_portfolio_metrics(self) -> RiskMetrics:
        """
        Calculate comprehensive portfolio risk metrics.
        
        Returns:
            RiskMetrics object with all metrics
        """
        portfolio_value = sum(pos.market_value for pos in self.positions.values())
        total_exposure = sum(abs(pos.market_value) for pos in self.positions.values())
        
        # Calculate returns
        if len(self.equity_curve) > 1:
            returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        else:
            returns = np.array([0.0])
        
        # VaR calculations
        var_95 = self.calculate_var(returns, 0.95) * portfolio_value if len(returns) > 0 else 0
        var_99 = self.calculate_var(returns, 0.99) * portfolio_value if len(returns) > 0 else 0
        
        # Expected Shortfall
        es = self.calculate_expected_shortfall(returns) * portfolio_value if len(returns) > 0 else 0
        
        # Max Drawdown
        max_dd = self.calculate_max_drawdown(self.equity_curve)
        
        # Sharpe Ratio
        sharpe = self.calculate_sharpe_ratio(returns)
        
        # Volatility (annualized)
        volatility = np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0
        
        # Beta (simplified, assuming market return = 0)
        beta = 1.0  # Placeholder
        
        # Determine risk level
        risk_level = self._determine_risk_level(max_dd, var_95, portfolio_value)
        
        return RiskMetrics(
            portfolio_value=portfolio_value,
            total_exposure=total_exposure,
            var_95=var_95,
            var_99=var_99,
            expected_shortfall=es,
            max_drawdown=max_dd,
            sharpe_ratio=sharpe,
            volatility=volatility,
            beta=beta,
            risk_level=risk_level
        )
    
    def _determine_risk_level(self, 
                             max_drawdown: float, 
                             var_95: float, 
                             portfolio_value: float) -> RiskLevel:
        """Determine overall risk level"""
        var_percent = abs(var_95 / portfolio_value) if portfolio_value > 0 else 0
        
        if max_drawdown > 0.25 or var_percent > 0.10:
            return RiskLevel.CRITICAL
        elif max_drawdown > 0.15 or var_percent > 0.05:
            return RiskLevel.HIGH
        elif max_drawdown > 0.08 or var_percent > 0.03:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def add_position(self, symbol: str, quantity: float, price: float):
        """Add new position to portfolio"""
        self.positions[symbol] = Position(
            symbol=symbol,
            quantity=quantity,
            entry_price=price,
            current_price=price,
            timestamp=datetime.now()
        )
        self.current_capital -= quantity * price
    
    def update_position_price(self, symbol: str, new_price: float):
        """Update position with new market price"""
        if symbol in self.positions:
            self.positions[symbol].current_price = new_price
    
    def close_position(self, symbol: str):
        """Close position and realize P&L"""
        if symbol in self.positions:
            pos = self.positions[symbol]
            self.current_capital += pos.market_value
            pnl = pos.pnl
            self.returns_history.append(pnl / self.initial_capital)
            del self.positions[symbol]
            return pnl
        return 0
    
    def get_portfolio_summary(self) -> Dict:
        """Get summary of current portfolio"""
        metrics = self.calculate_portfolio_metrics()
        
        return {
            'capital': self.current_capital,
            'portfolio_value': metrics.portfolio_value,
            'total_value': self.current_capital + metrics.portfolio_value,
            'total_pnl': (self.current_capital + metrics.portfolio_value) - self.initial_capital,
            'num_positions': len(self.positions),
            'risk_level': metrics.risk_level.value,
            'var_95': metrics.var_95,
            'max_drawdown': metrics.max_drawdown,
            'sharpe_ratio': metrics.sharpe_ratio,
            'volatility': metrics.volatility
        }

if __name__ == "__main__":
    # Example usage
    print("=== Risk Management System Demo ===\n")
    
    # Initialize risk manager
    rm = RiskManager(initial_capital=100000, max_position_size=0.1, max_portfolio_risk=0.02)
    
    # Calculate position size
    price = 150.0
    volatility = 0.25
    position_size = rm.calculate_position_size(price, volatility)
    print(f"Recommended position size for ${price}: {position_size} shares")
    
    # Add positions
    rm.add_position("AAPL", 100, 150.0)
    rm.add_position("GOOGL", 50, 2800.0)
    
    # Update prices
    rm.update_position_price("AAPL", 155.0)
    rm.update_position_price("GOOGL", 2750.0)
    
    # Get portfolio summary
    summary = rm.get_portfolio_summary()
    print("\n=== Portfolio Summary ===")
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    # Calculate risk metrics
    metrics = rm.calculate_portfolio_metrics()
    print(f"\nRisk Level: {metrics.risk_level.value}")
    print(f"VaR (95%): ${metrics.var_95:.2f}")
    print(f"Max Drawdown: {metrics.max_drawdown*100:.2f}%")
    
    print("\n✓ Risk management system operational!")
