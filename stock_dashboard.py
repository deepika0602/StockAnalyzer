import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(layout="wide")
st.title("📈 Stock Portfolio Analyzer - Streamlit Version")

# User Inputs
symbols = st.text_input("Enter stock symbols (comma-separated)", "AAPL, MSFT, GOOGL, TSLA, AMZN")
symbols = [s.strip().upper() for s in symbols.split(',') if s.strip()]
start_date = st.date_input("Start Date", pd.to_datetime("2022-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("2024-01-01"))

if st.button("🔍 Analyze Portfolio"):
    try:
        raw_data = yf.download(symbols, start=start_date, end=end_date, auto_adjust=True)
        data = raw_data['Close']

        # Returns and portfolio
        daily_returns = data.pct_change().dropna()
        cumulative_returns = (1 + daily_returns).cumprod()
        weights = np.ones(len(symbols)) / len(symbols)
        portfolio_returns = daily_returns.dot(weights)
        portfolio_cumulative = (1 + portfolio_returns).cumprod()

        # Metrics
        total_return = (data.iloc[-1] / data.iloc[0]) - 1
        volatility = daily_returns.std()
        sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
        drawdown = cumulative_returns / cumulative_returns.cummax() - 1
        max_drawdown = drawdown.min()

        # Summary table
        summary_df = pd.DataFrame({
            'Total Return (%)': (total_return * 100).round(2),
            'Volatility (%)': (volatility * 100).round(2),
            'Sharpe Ratio': sharpe_ratio.round(2),
            'Max Drawdown (%)': (max_drawdown * 100).round(2)
        })

        # Stock Info
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

        # Correlation matrix
        correlation = daily_returns.corr()

        # Display results
        st.subheader("📊 Performance Summary")
        st.dataframe(summary_df)

        st.subheader("🧠 Stock Information")
        st.dataframe(info_df)

        st.subheader("🔗 Correlation Matrix")
        st.dataframe(correlation)

        # Plot 1: Stock Prices
        st.subheader("📈 Stock Price Chart")
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        data.plot(ax=ax1)
        st.pyplot(fig1)

        # Plot 2: Cumulative Returns
        st.subheader("💹 Cumulative Returns of Each Stock")
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        cumulative_returns.plot(ax=ax2)
        st.pyplot(fig2)

        # Plot 3: Portfolio Return
        st.subheader("🧮 Portfolio Cumulative Return")
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        portfolio_cumulative.plot(ax=ax3, color='black')
        st.pyplot(fig3)

        # Export to Excel
        st.subheader("📤 Download Excel Report")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Performance Summary')
            correlation.to_excel(writer, sheet_name='Correlation Matrix')
            info_df.to_excel(writer, sheet_name='Stock Info')
        output.seek(0)

        st.download_button("Download Report", output, file_name="Stock_Portfolio_Report.xlsx")

    except Exception as e:
        st.error(f"❌ Error: {e}")
