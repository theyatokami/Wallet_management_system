import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import os

# Default values
default_daily_spending = 7
default_saving_goal = 700
balance_history_file = "balance_history.csv"
user_inputs_file = "user_inputs.csv"

# Initialize balance history
if os.path.exists(balance_history_file):
    balance_history = pd.read_csv(balance_history_file)
else:
    balance_history = pd.DataFrame(columns=["Date", "Remaining Balance"])

# Load user inputs
user_inputs = {}
if os.path.exists(user_inputs_file):
    user_inputs_df = pd.read_csv(user_inputs_file, index_col=0)
    user_inputs = user_inputs_df.iloc[0].to_dict()

def calculate_remaining_balance(current_money, daily_spending, current_day, total_days):
    # Calculate the remaining money after subtracting the daily spending for the rest of the month
    remaining_money = current_money - daily_spending * (total_days - current_day + 1)
    return remaining_money

def calculate_money_evolution(current_money, daily_spending, current_day, total_days):
    remaining_balances = []
    for day in range(current_day, total_days+1):
        remaining_balance = current_money
        remaining_balances.append(remaining_balance)
        current_money -= daily_spending
    return pd.DataFrame({"Day": np.arange(current_day, total_days+1), "Remaining Balance": remaining_balances})

st.title('Money Management System')

# User inputs
current_money = st.number_input("Enter your current total money:", value=user_inputs.get("current_money", 0))
daily_spending = st.number_input("Enter your daily spending:", value=user_inputs.get("daily_spending", default_daily_spending))
saving_goal = st.number_input("Enter your saving goal:", value=user_inputs.get("saving_goal", default_saving_goal))

# Get today's date
now = datetime.now()
current_day = now.day

# For simplicity, we assume every month has 30 days
total_days = 30

remaining_balance = None  # Default value for remaining_balance

# If the user has clicked the "Submit" button
if st.button('Submit'):
    remaining_balance = calculate_remaining_balance(current_money, daily_spending, current_day, total_days)
    new_row = pd.DataFrame({"Date": [now.strftime("%Y-%m-%d")], "Remaining Balance": [remaining_balance]})
    balance_history = pd.concat([balance_history, new_row], ignore_index=True)
    balance_history.to_csv(balance_history_file, index=False)

    # Save user inputs
    user_inputs_df = pd.DataFrame({
        "current_money": [current_money],
        "daily_spending": [daily_spending],
        "saving_goal": [saving_goal]
    })
    user_inputs_df.to_csv(user_inputs_file)

    # Display pile of money
    money_bags = "💰" * int(remaining_balance / 100)  # One money bag emoji for each 100 euros
    st.write(money_bags)

    # Display money evolution chart
    money_evolution_df = calculate_money_evolution(current_money, daily_spending, current_day, total_days)
    st.line_chart(money_evolution_df.set_index("Day"))

    # Display balance history chart
    st.line_chart(balance_history.set_index("Date"))

# If the user has clicked the "Reset" button
if st.button('Reset'):
    current_money = 0
    daily_spending = default_daily_spending
    saving_goal = default_saving_goal
    balance_history = pd.DataFrame(columns=["Date", "Remaining Balance"])
    balance_history.to_csv(balance_history_file, index=False)

    # Reset user inputs
    user_inputs = {}
    user_inputs_df = pd.DataFrame(columns=["current_money", "daily_spending", "saving_goal"])
    user_inputs_df.to_csv(user_inputs_file)

if remaining_balance is not None:
    st.write(f"Your predicted remaining balance at the end of the month is: €{remaining_balance:.2f}")
    st.write(f"Your predicted disposable income at the end of the month is: €{(remaining_balance-saving_goal):.2f}")
