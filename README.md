# ⚠️ Automated Risk Management System

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.26-orange.svg)](https://numpy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

[English](#english) | [Português](#português)

---

## English

### Overview

Comprehensive automated risk management system for trading portfolios. Calculates VaR, manages position sizing, monitors stop-losses, and provides real-time risk metrics.

### Key Features

- **Value at Risk (VaR)**: Historical and parametric VaR calculation at 95% and 99% confidence
- **Expected Shortfall**: Conditional VaR for tail risk assessment
- **Position Sizing**: Automated calculation based on risk parameters
- **Stop-Loss Management**: Dynamic stop-loss monitoring and alerts
- **Portfolio Metrics**: Sharpe ratio, max drawdown, volatility, beta
- **Risk Levels**: Automatic classification (LOW, MEDIUM, HIGH, CRITICAL)
- **Real-time Monitoring**: Continuous portfolio risk assessment

### Quick Start

```python
from src.risk_manager import RiskManager

# Initialize with $100,000 capital
rm = RiskManager(
    initial_capital=100000,
    max_position_size=0.1,      # 10% max per position
    max_portfolio_risk=0.02,    # 2% risk per trade
    stop_loss_percent=0.05      # 5% stop-loss
)

# Calculate position size
position_size = rm.calculate_position_size(
    price=150.0,
    volatility=0.25
)

# Add positions
rm.add_position("AAPL", 100, 150.0)
rm.update_position_price("AAPL", 155.0)

# Get risk metrics
metrics = rm.calculate_portfolio_metrics()
print(f"VaR (95%): ${metrics.var_95:.2f}")
print(f"Risk Level: {metrics.risk_level.value}")

# Portfolio summary
summary = rm.get_portfolio_summary()
print(f"Total P&L: ${summary['total_pnl']:.2f}")
```

### Risk Metrics

#### Value at Risk (VaR)
Estimates maximum potential loss over a time horizon at a given confidence level.

```python
var_95 = rm.calculate_var(returns, confidence_level=0.95)
var_99 = rm.calculate_var(returns, confidence_level=0.99)
```

#### Expected Shortfall (CVaR)
Average loss in worst-case scenarios beyond VaR threshold.

```python
es = rm.calculate_expected_shortfall(returns, confidence_level=0.95)
```

#### Maximum Drawdown
Largest peak-to-trough decline in portfolio value.

```python
max_dd = rm.calculate_max_drawdown(equity_curve)
```

#### Sharpe Ratio
Risk-adjusted return metric (annualized).

```python
sharpe = rm.calculate_sharpe_ratio(returns, risk_free_rate=0.02)
```

### Position Sizing

Automatically calculates optimal position size based on:
- Maximum position size (% of portfolio)
- Risk per trade (% of capital)
- Stop-loss distance
- Asset volatility

### Risk Levels

| Level | Max Drawdown | VaR (% of Portfolio) |
|-------|--------------|----------------------|
| LOW | < 8% | < 3% |
| MEDIUM | 8-15% | 3-5% |
| HIGH | 15-25% | 5-10% |
| CRITICAL | > 25% | > 10% |

### Use Cases

- **Algorithmic Trading**: Automated risk controls for trading bots
- **Portfolio Management**: Multi-asset risk monitoring
- **Hedge Funds**: Institutional-grade risk management
- **Prop Trading**: Real-time exposure limits
- **Backtesting**: Realistic risk constraints in simulations

### Architecture

```
Portfolio Positions
        ↓
Risk Manager
   ├── Position Sizing
   ├── VaR Calculation
   ├── Stop-Loss Monitoring
   ├── Drawdown Tracking
   └── Risk Level Assessment
        ↓
Risk Metrics & Alerts
```

### API Reference

#### RiskManager

```python
rm = RiskManager(
    initial_capital: float,
    max_position_size: float = 0.1,
    max_portfolio_risk: float = 0.02,
    stop_loss_percent: float = 0.05
)

# Position management
rm.add_position(symbol, quantity, price)
rm.update_position_price(symbol, new_price)
rm.close_position(symbol)

# Risk calculations
metrics = rm.calculate_portfolio_metrics()
var = rm.calculate_var(returns, confidence_level=0.95)
sharpe = rm.calculate_sharpe_ratio(returns)

# Portfolio summary
summary = rm.get_portfolio_summary()
```

### License

MIT License

### Author

**Gabriel Demetrios Lafis**

---

## Português

### Visão Geral

Sistema abrangente de gestão de risco automatizado para portfólios de trading. Calcula VaR, gerencia dimensionamento de posições, monitora stop-losses e fornece métricas de risco em tempo real.

### Características Principais

- **Value at Risk (VaR)**: Cálculo de VaR histórico e paramétrico em 95% e 99% de confiança
- **Expected Shortfall**: VaR condicional para avaliação de risco de cauda
- **Dimensionamento de Posição**: Cálculo automatizado baseado em parâmetros de risco
- **Gestão de Stop-Loss**: Monitoramento dinâmico de stop-loss e alertas
- **Métricas de Portfólio**: Índice de Sharpe, drawdown máximo, volatilidade, beta
- **Níveis de Risco**: Classificação automática (BAIXO, MÉDIO, ALTO, CRÍTICO)
- **Monitoramento em Tempo Real**: Avaliação contínua de risco do portfólio

### Autor

**Gabriel Demetrios Lafis**
