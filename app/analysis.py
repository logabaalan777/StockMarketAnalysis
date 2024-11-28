import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyspark.sql import SparkSession
import streamlit as st
from app.charts import create_interactive_chart

def calculate_rsi(data, window):
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def perform_analysis(data):
    spark = SparkSession.builder.appName("StockAnalysis").getOrCreate()
    df = spark.createDataFrame(data)

    st.write("**Summary Statistics**")
    summary_df = df.describe().toPandas()
    st.dataframe(summary_df)

    st.write("**Moving Average Analysis**")
    window_size = st.slider("Select Moving Average Window Size", 5, 50, 20)
    data["Moving Average"] = data["Close"].rolling(window=window_size).mean()
    data = data.dropna(subset=["Moving Average"])  
    create_interactive_chart(data, "Date", "Moving Average", "Moving Average Analysis")

    # st.write("**Daily Returns**")
    data["Daily Returns"] = data["Close"].pct_change()
    data = data.dropna(subset=["Daily Returns"])  
    create_interactive_chart(data, "Date", "Daily Returns", "Daily Returns")

    # st.write("**Volatility Analysis**")
    data["Volatility"] = data["Daily Returns"].rolling(window=window_size).std()
    data = data.dropna(subset=["Volatility"]) 
    create_interactive_chart(data, "Date", "Volatility", "Volatility Analysis")

    # st.write("**Cumulative Returns**")
    data["Cumulative Returns"] = (1 + data["Daily Returns"]).cumprod()
    create_interactive_chart(data, "Date", "Cumulative Returns", "Cumulative Returns")

    # st.write("**Bollinger Bands**")
    data["Rolling Mean"] = data["Close"].rolling(window=window_size).mean()
    data["Upper Band"] = data["Rolling Mean"] + 2 * data["Close"].rolling(window=window_size).std()
    data["Lower Band"] = data["Rolling Mean"] - 2 * data["Close"].rolling(window=window_size).std()
    data = data.dropna(subset=["Upper Band", "Lower Band", "Rolling Mean"])

    fig_bollinger = px.line(data, x="Date", y=["Close", "Upper Band", "Lower Band"], title="Bollinger Bands")
    fig_bollinger.update_layout(hovermode="x unified")
    st.plotly_chart(fig_bollinger)

    # st.write("**Candlestick Analysis**")
    fig_candlestick = go.Figure(data=[go.Candlestick(
        x=data["Date"],
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        increasing_line_color="green",
        decreasing_line_color="red",
        name="Candlestick Chart"
    )])
    fig_candlestick.update_layout(
        title="Candlestick Analysis",
        xaxis_title="Date",
        yaxis_title="Stock Price",
        xaxis_rangeslider_visible=False,
        hovermode="x unified"
    )
    st.plotly_chart(fig_candlestick)

    # st.write("**RSI (Relative Strength Index) Analysis**")
    data["RSI"] = calculate_rsi(data, window=14)
    data = data.dropna(subset=["RSI"])
    fig_rsi = px.line(data, x="Date", y="RSI", title="RSI Analysis")
    fig_rsi.add_hline(y=70, line_dash="dot", line_color="red", annotation_text="Overbought")
    fig_rsi.add_hline(y=30, line_dash="dot", line_color="green", annotation_text="Oversold")
    st.plotly_chart(fig_rsi)

    # st.write("**MACD (Moving Average Convergence Divergence) Analysis**")
    data["EMA12"] = data["Close"].ewm(span=12, adjust=False).mean()
    data["EMA26"] = data["Close"].ewm(span=26, adjust=False).mean()
    data["MACD"] = data["EMA12"] - data["EMA26"]
    data["Signal Line"] = data["MACD"].ewm(span=9, adjust=False).mean()
    fig_macd = px.line(data, x="Date", y=["MACD", "Signal Line"], title="MACD Analysis")
    fig_macd.update_layout(hovermode="x unified")
    st.plotly_chart(fig_macd)

    # st.write("**Volume Analysis**")
    fig_volume = px.bar(data, x="Date", y="Volume", title="Volume Analysis")
    st.plotly_chart(fig_volume)

    st.write("**Price Correlation Analysis**")
    correlation_col = st.selectbox("Select Column for Correlation", options=["Volume", "Daily Returns"])
    correlation = data["Close"].corr(data[correlation_col])
    st.write(f"Correlation between Close Price and {correlation_col}: {correlation:.2f}")
    fig_correlation = px.scatter(data, x="Close", y=correlation_col, title=f"Price vs {correlation_col} Correlation")
    st.plotly_chart(fig_correlation)
