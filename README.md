# Moving Average Trading Strategy Optimizer

A Python-based trading strategy that optimizes Simple Moving Average (SMA) and Fast Moving Average (FMA) parameters for the S&P 500 index, with comprehensive backtesting and performance analysis.

## Overview

This project implements a systematic approach to finding optimal moving average crossover parameters for trading the S&P 500. The strategy uses a dual moving average system where buy signals are generated when the fast moving average crosses above the slow moving average, and positions are closed when the fast MA falls below the slow MA.

## Features

- **Parameter Optimization**: Systematically tests combinations of SMA (140-250 days) and FMA (5-95 days) parameters
- **Performance Visualization**: Generates heatmaps showing CAGR across all parameter combinations
- **Backtesting Engine**: Comprehensive backtesting with transaction costs and realistic trading simulation
- **Benchmark Comparison**: Compares strategy performance against buy-and-hold approach
- **Risk Metrics**: Calculates CAGR, absolute returns, and time-in-market statistics

## Strategy Logic

1. **Signal Generation**: Long position when FMA ≥ SMA, cash position otherwise
2. **Transaction Costs**: 0.1% cost applied on each position change
3. **Optimization**: Searches for parameter combination maximizing Compound Annual Growth Rate (CAGR)
4. **Analysis Period**: January 1, 2000 to present day

## Requirements

```python
yfinance>=0.1.70
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/justus3003/moving-average-strategy.git
cd moving-average-strategy
```

2. Install required packages:
```bash
pip install yfinance numpy pandas matplotlib
```

## Usage

Run the main script to execute the complete analysis:

```bash
python trading_strategy.py
```

The script will:
1. Download S&P 500 historical data from Yahoo Finance
2. Test all SMA/FMA parameter combinations
3. Display optimization results and heatmap
4. Show performance comparison between strategy and benchmark
5. Generate balance evolution charts

## Output

### Optimization Results
- Optimal SMA and FMA parameters
- Maximum achievable CAGR
- Parameter sensitivity heatmap

### Performance Summary
| Metric | Benchmark | System |
|--------|-----------|---------|
| Final Balance | $X,XXX.XX | $X,XXX.XX |
| Absolute Return | XX.X% | XX.X% |
| CAGR | XX.X% | XX.X% |
| Time in Market | 100.00% | XX.X% |

### Visualizations
1. **CAGR Heatmap**: Color-coded performance across all parameter combinations
2. **Balance Evolution**: Side-by-side comparison of strategy vs. buy-and-hold performance

## Key Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `ticker` | ^GSPC | S&P 500 index symbol |
| `start` | 2000-01-01 | Analysis start date |
| `balance` | $1,000 | Initial investment amount |
| `trans_cost` | 0.1% | Transaction cost per trade |
| `sma_range` | 140-250 days | Slow moving average search range |
| `fma_range` | 5-95 days | Fast moving average search range |

## Algorithm Details

### Data Processing
- Downloads OHLC data using yfinance
- Calculates logarithmic returns for precise compounding
- Removes high/low/volume data to focus on closing prices

### Optimization Process
- Tests all valid FMA < SMA combinations
- Calculates rolling averages for each parameter set
- Simulates trading with transaction costs
- Ranks combinations by CAGR performance

### Performance Calculation
- Uses exponential return compounding: `balance * exp(cumsum(log_returns))`
- Applies transaction costs on position changes
- Calculates annualized metrics using exact day count

## Customization

Modify these variables to test different scenarios:

```python
# Change ticker symbol
ticker = "^IXIC"  # NASDAQ Composite

# Adjust date range
start = '2010-01-01'
end = '2020-12-31'

# Modify search ranges
sma_range = range(100, 300, 10)  # Different SMA range
fma_range = range(10, 50, 5)     # Different FMA range

# Adjust costs
trans_cost = 0.005  # 0.5% transaction cost
```

## Limitations

- **Past Performance**: Historical optimization doesn't guarantee future results
- **Overfitting Risk**: Extensive parameter search may lead to curve-fitted results
- **Market Regime Changes**: Strategy may not adapt to changing market conditions
- **Transaction Costs**: Simplified cost model may not reflect real trading costs
- **Liquidity**: Assumes perfect liquidity for S&P 500 trades

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhancement`)
3. Commit your changes (`git commit -am 'Add enhancement'`)
4. Push to the branch (`git push origin feature/enhancement`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is for educational and research purposes only. It should not be considered as financial advice. Always consult with qualified financial professionals before making investment decisions. Past performance does not guarantee future results.
