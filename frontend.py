import yfinance as yf
import datetime
import streamlit as st

start_date = datetime.date(2022,1,1)
end_date = datetime.date.today()
ticker = 'AAPL'

st.markdown("<h1 style='text-align: center; color: orange;'> Stock Prices</h1>", unsafe_allow_html=True,)

