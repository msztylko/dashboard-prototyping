import yfinance as yf
import datetime
import streamlit as st
import plotly.graph_objects as go

start_date = datetime.date(2022,1,1)
end_date = datetime.date.today()
ticker = 'AAPL'

st.markdown("<h1 style='text-align: center; color: orange;'> Stock Prices</h1>", unsafe_allow_html=True,)

data = yf.download(ticker, start_date, end_date)
value = 'Close'

fig = go.Figure()
fig.add_scatter(x=data.index, y=data[value], name=value)
fig.update_layout(
    title_text=f"{ticker} {value}",
    title_x=0.5,
    xaxis_title='Date',
    yaxis_title=value,
    legend_title=ticker,
)

st.plotly_chart(fig)
