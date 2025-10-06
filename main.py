import streamlit as st
import yfinance as yf
import pandas as pd

def calculate_return(ticker, start_date, end_date, max_loss_ratio, target_win_ratio):
    # Ensure that the data is downloaded with 'auto_adjust' set to False for raw prices
    data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)

    # Initialize counts and cumulative ROI
    win, loss, both, draw = 0, 0, 0, 0
    win_cum_return, loss_cum_return, both_cum_return, draw_cum_return = 0.0, 0.0, 0.0, 0.0

    # Iterate over each row in the DataFrame
    for index, row in data.iterrows():
        if row.isnull().any():
            continue
        
        high_reached = (row['High'] - row['Open']) / row['Open']
        low_reached = (row['Open'] - row['Low']) / row['Open']
        high_reached = high_reached.item()
        low_reached =  low_reached.item()
        
        if (high_reached >= target_win_ratio) and (low_reached >= max_loss_ratio):
            both += 1
            both_cum_return += (row['Close'] - row['Open']) / row['Open']
        elif high_reached >= target_win_ratio:
            win += 1
            win_cum_return += (row['High'] - row['Open']) / row['Open']
        elif low_reached >= max_loss_ratio:
            loss += 1
            loss_cum_return += (row['Low'] - row['Open']) / row['Open']
        else:
            draw += 1
            draw_cum_return += (row['Close'] - row['Open']) / row['Open']

    win_roi = win_cum_return / win if win > 0 else 0
    loss_roi = loss_cum_return / loss if loss > 0 else 0
    both_roi = both_cum_return / both if both > 0 else 0
    draw_roi = draw_cum_return / draw if draw > 0 else 0

    return win, loss, both, draw, win_roi, loss_roi, both_roi, draw_roi, data

# Streamlit app
st.title("Trading Strategy Analysis")

# Sidebar inputs
st.sidebar.header("Input Parameters")
ticker = st.sidebar.text_input("Enter Ticker", 'AAPL')
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2021-12-31"))
max_loss_ratio = st.sidebar.slider("Max Loss Ratio (%)", min_value=0.0, max_value=1.0, value=0.05) / 100
target_win_ratio = st.sidebar.slider("Target Win Ratio (%)", min_value=0.0, max_value=5.0, value=1.0) / 100

if st.sidebar.button("Calculate"):
    win, loss, both, draw, win_roi, loss_roi, both_roi, draw_roi, data_m = calculate_return(
        ticker, start_date, end_date, max_loss_ratio, target_win_ratio
    )

    st.write("### Results")
    st.write(f"Total Trades: {len(data_m)}")
    st.write(f"Win count: {win}")
    st.write(f"Loss count: {loss}")
    st.write(f"Both Win & Loss count: {both}")
    st.write(f"Draw count: {draw}")
    st.write(f"Expected ROI for Win: {win_roi:.2%}")
    st.write(f"Expected ROI for Loss: {loss_roi:.2%}")
    st.write(f"Expected ROI for Both: {both_roi:.2%}")
    st.write(f"Expected ROI for Draw: {draw_roi:.2%}")

