# import packages
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")
from datetime import datetime, date

# set parameters
ticker = "^GSPC"
start = '2000-01-01'
end = date.today().strftime('%Y-%m-%d')
years = (datetime.strptime(end, '%Y-%m-%d') - datetime.strptime(start, '%Y-%m-%d')).days / 365.25
balance = 1000
trans_cost = 0.001

# download OHLC daily price data
raw_data = yf.download(ticker, start=start, end=end, auto_adjust=True)
raw_data = raw_data.drop(['High', 'Low', 'Volume'], axis=1)
raw_data['Return'] = np.log(raw_data['Close']) - np.log(raw_data['Close'].shift(1))

print("Step 1: Finding optimal SMA x FMA parameter combination...")
print("-" * 60)

# identify optimal SMA x FMA parameter combination
result = {
    'SMA': None,
    'FMA': None,
    'CAGR': -np.inf
}

# prepare arrays for heatmap
sma_range = range(140, 255, 5)
fma_range = range(5, 100, 5)
cagr_matrix = np.full((len(fma_range), len(sma_range)), np.nan)

# loop through all SMA x FMA parameter combinations
for i, sma in enumerate(sma_range):
    for j, fma in enumerate(fma_range):
        if fma >= sma:
            continue

        temp = raw_data.copy()
        temp['SMA'] = temp['Close'].rolling(window=sma).mean()
        temp['FMA'] = temp['Close'].rolling(window=fma).mean()
        temp = temp.dropna()

        if temp.empty:
            continue

        temp['Long'] = temp['FMA'] >= temp['SMA']
        temp['Sys_Return'] = np.where(
            temp['Long'].shift(1),
            temp['Return'],
            0
        )
        temp['Sys_Return'] -= np.where(
            temp['Long'] != temp['Long'].shift(1),
            trans_cost,
            0
        )
        temp['Sys_Balance'] = balance * np.exp(temp['Sys_Return'].cumsum())

        if len(temp) < 2:
            continue

        cagr = (temp['Sys_Balance'].iloc[-1] / temp['Sys_Balance'].iloc[0]) ** (1 / years) - 1

        # store CAGR in matrix for heatmap
        cagr_matrix[j, i] = cagr

        if cagr > result['CAGR']:
            result = {
                'SMA': sma,
                'FMA': fma,
                'CAGR': cagr
            }

print("Optimal Parameters:")
print(f" Slow MA: {result['SMA']}")
print(f" Fast MA: {result['FMA']}")
print(f" CAGR: {result['CAGR']:.2%}")
print()

# create heatmap of CAGR values
plt.figure(figsize=(14, 8))
im = plt.imshow(cagr_matrix, cmap='RdYlGn', aspect='auto', origin='lower')

# set ticks and labels
plt.xticks(range(0, len(sma_range), 2), [sma_range[i] for i in range(0, len(sma_range), 2)])
plt.yticks(range(0, len(fma_range), 2), [fma_range[i] for i in range(0, len(fma_range), 2)])
plt.xlabel('Slow Moving Average (SMA) - Days')
plt.ylabel('Fast Moving Average (FMA) - Days')
plt.title('CAGR Heatmap for SMA x FMA Parameter Combinations')

# add colorbar
cbar = plt.colorbar(im, shrink=0.8)
cbar.set_label('CAGR (%)', rotation=270, labelpad=20)

# format colorbar labels as percentages
import matplotlib.ticker as mticker

cbar.ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:.1%}'))

# mark optimal point
if result['SMA'] and result['FMA']:
    optimal_sma_idx = list(sma_range).index(result['SMA'])
    optimal_fma_idx = list(fma_range).index(result['FMA'])
    plt.plot(optimal_sma_idx, optimal_fma_idx, 'b*', markersize=15,
             markeredgecolor='white', markeredgewidth=2,
             label=f'Optimal: SMA={result["SMA"]}, FMA={result["FMA"]}')
    plt.legend(loc='upper right')

plt.tight_layout()
plt.show()
print()

print("Step 2: Computing performance with optimal parameters...")
print("-" * 60)

# use optimal parameters for final analysis
optimal_sma = result['SMA']
optimal_fma = result['FMA']

# prepare data with optimal parameters
data = raw_data.copy()
data['SMA'] = data['Close'].rolling(window=optimal_sma).mean()
data['FMA'] = data['Close'].rolling(window=optimal_fma).mean()
data = data.dropna()

# compute balance of Buy-and-Hold strategy as benchmark
data['Ben_Balance'] = round(balance * np.exp(data['Return'].cumsum()), 2)

# define long positions for every trading day
data['Long'] = data['FMA'].squeeze() >= data['SMA'].squeeze()

# compute system returns
data['Sys_Return'] = np.where(
    data['Long'].shift(1) == True,
    data['Return'],
    0
)

# deduct transaction costs when position changes
data['Sys_Return'] -= np.where(
    data['Long'] != data['Long'].shift(1),
    trans_cost,
    0
)

# compute system balance
data['Sys_Balance'] = round(balance * np.exp(data['Sys_Return'].cumsum()), 2)


# performance summary function
def performance_summary(data, years):
    summary = pd.DataFrame(index=['Benchmark', 'System'])

    summary['Final Balance'] = [data['Ben_Balance'].iloc[-1], data['Sys_Balance'].iloc[-1]]

    summary['Absolute Return'] = [
        data['Ben_Balance'].iloc[-1] / data['Ben_Balance'].iloc[0] - 1,
        data['Sys_Balance'].iloc[-1] / data['Sys_Balance'].iloc[0] - 1
    ]

    summary['CAGR'] = [
        (data['Ben_Balance'].iloc[-1] / data['Ben_Balance'].iloc[0]) ** (1 / years) - 1,
        (data['Sys_Balance'].iloc[-1] / data['Sys_Balance'].iloc[0]) ** (1 / years) - 1
    ]

    summary['Time in Market (%)'] = [100, data['Long'].mean() * 100]

    return summary


print("Step 3: Performance summary and comparison...")
print("-" * 60)

# generate and display performance summary
summary = performance_summary(data, years)
print(summary.style.format({
    'Final Balance': '${:,.2f}',
    'Absolute Return': '{:.2%}',
    'CAGR': '{:.2%}',
    'Time in Market (%)': '{:.2f}%'
}))

print()
print("Strategy Details:")
print(f"Optimal SMA: {optimal_sma} days")
print(f"Optimal FMA: {optimal_fma} days")
print(f"Transaction Cost: {trans_cost * 100:.1f}% per trade")
print(f"Analysis Period: {start} to {end} ({years:.1f} years)")

# plot benchmark and system balances
plt.figure(figsize=(12, 6))
plt.plot(data.index, data['Ben_Balance'], color="blue", label='Benchmark (Buy & Hold)', linewidth=2)
plt.plot(data.index, data['Sys_Balance'], color="red", label=f'System (SMA={optimal_sma}, FMA={optimal_fma})',
         linewidth=2)
plt.title('Balance Comparison: Benchmark vs. Optimized Moving Average System')
plt.xlabel('Date')
plt.ylabel('Balance ($)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()