import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Step 1: User-defined stocks
symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
start_date = '2022-01-01'
end_date = '2024-01-01'

# Step 2: Download stock data
raw_data = yf.download(symbols, start=start_date, end=end_date, auto_adjust=True)
data = raw_data['Close']

# Step 3: Calculate returns
daily_returns = data.pct_change().dropna()
cumulative_returns = (1 + daily_returns).cumprod()

# Equal weight portfolio
weights = np.ones(len(symbols)) / len(symbols)
portfolio_returns = daily_returns.dot(weights)
portfolio_cumulative = (1 + portfolio_returns).cumprod()

# Metrics
total_return = (data.iloc[-1] / data.iloc[0]) - 1
volatility = daily_returns.std()
sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
drawdown = cumulative_returns / cumulative_returns.cummax() - 1
max_drawdown = drawdown.min()

# Correlation matrix
correlation = daily_returns.corr()

# Step 4: Get stock info (sector, industry, market cap)
stock_info = []
for symbol in symbols:
    ticker = yf.Ticker(symbol)
    info = ticker.info
    stock_info.append({
        'Symbol': symbol,
        'Company': info.get('shortName', 'N/A'),
        'Sector': info.get('sector', 'N/A'),
        'Industry': info.get('industry', 'N/A'),
        'Market Cap (B)': round(info.get('marketCap', 0) / 1e9, 2)
    })

info_df = pd.DataFrame(stock_info)

# Step 5: Summary table
summary_df = pd.DataFrame({
    'Total Return (%)': (total_return * 100).round(2),
    'Volatility (%)': (volatility * 100).round(2),
    'Sharpe Ratio': sharpe_ratio.round(2),
    'Max Drawdown (%)': (max_drawdown * 100).round(2)
})

# Step 6: Export everything to a single Excel file
with pd.ExcelWriter("Stock_Portfolio_Report.xlsx", engine='openpyxl') as writer:
    summary_df.to_excel(writer, sheet_name='Performance Summary')
    correlation.to_excel(writer, sheet_name='Correlation Matrix')
    info_df.to_excel(writer, sheet_name='Stock Info')

print("✅ Excel Report Generated: Stock_Portfolio_Report.xlsx")

# Step 7: Plots
plt.figure(figsize=(12, 5))
data.plot(title='Stock Prices Over Time')
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 5))
cumulative_returns.plot(title='Cumulative Returns')
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 4))
portfolio_cumulative.plot(title='Portfolio Cumulative Return', color='black')
plt.grid(True)
plt.tight_layout()
plt.show()
