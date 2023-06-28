import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# Default values
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
    user_inputs_df = pd.read_csv(user_inputs_file)
    if not user_inputs_df.empty:
        user_inputs = user_inputs_df.iloc[0].to_dict()

def calculate_remaining_balance(current_money, expenses, current_day, total_days):
    remaining_balances = []
    for day in range(current_day, total_days+1):
        remaining_balance = current_money
        for expense in expenses:
            if expense['frequency'] == 'daily':
                remaining_balance -= expense['amount']
            elif expense['frequency'] == 'weekly':
                if (day - current_day) % 7 == 0:
                    remaining_balance -= expense['amount']
            elif expense['frequency'] == 'monthly':
                if day == int(expense['day']):
                    remaining_balance -= expense['amount']
        remaining_balances.append(remaining_balance)
        current_money -= sum(expense['amount'] for expense in expenses if expense['frequency'] == 'daily')
    return pd.DataFrame({"Day": np.arange(current_day, total_days+1), "Remaining Balance": remaining_balances})

def calculate_money_evolution(current_money, expenses, current_day, total_days):
    remaining_balances = []
    for day in range(current_day, total_days+1):
        remaining_balance = current_money
        for expense in expenses:
            if expense['frequency'] == 'daily':
                remaining_balance -= expense['amount']
            elif expense['frequency'] == 'weekly':
                if (day - current_day) % 7 == 0:
                    remaining_balance -= expense['amount']
            elif expense['frequency'] == 'monthly':
                if day == int(expense['day']):
                    remaining_balance -= expense['amount']
        remaining_balances.append(remaining_balance)
        current_money -= sum(expense['amount'] for expense in expenses if expense['frequency'] == 'daily')
    return pd.DataFrame({"Day": np.arange(current_day, total_days+1), "Remaining Balance": remaining_balances})

st.title('Money Management System')

# User inputs
current_money = st.number_input("Enter your current total money:", value=user_inputs.get("current_money", 0))
saving_goal = st.number_input("Enter your saving goal:", value=user_inputs.get("saving_goal", default_saving_goal))

# Get today's date
now = datetime.now()
current_day = now.day

# For simplicity, we assume every month has 30 days
total_days = 30

remaining_balance = None  # Default value for remaining_balance

# Expenses inputs
st.header("Expenses")
num_expenses = st.number_input("Number of Expenses", min_value=0.0, value=user_inputs.get("num_expenses", 0))


expenses = []
for i in range(int(num_expenses)):

    st.subheader(f"Expense #{i+1}")
    name = st.text_input("Name", key=f"name_{i}")
    frequency = st.selectbox("Frequency", options=["daily", "weekly", "monthly"], key=f"frequency_{i}")
    amount = st.number_input("Amount", value=user_inputs.get(f"expense_amount_{i}", 0), key=f"amount_{i}")
    if frequency == "monthly":
        day = st.number_input("Day of the month", min_value=1, max_value=31, value=int(user_inputs.get(f"expense_day_{i}", 1)), key=f"day_{i}")
    else:
        day = None
    expenses.append({"name": name, "frequency": frequency, "amount": amount, "day": day})

# If the user has clicked the "Submit" button
if st.button('Submit'):
    remaining_balance = calculate_remaining_balance(current_money, expenses, current_day, total_days)
    new_row = pd.DataFrame({"Date": [now.strftime("%Y-%m-%d")], "Remaining Balance": [remaining_balance["Remaining Balance"].values[0]]})


    balance_history = pd.concat([balance_history, new_row], ignore_index=True)

    balance_history.to_csv(balance_history_file, index=False)

    # Save user inputs
    user_inputs_df = pd.DataFrame({
        "current_money": [current_money],
        "saving_goal": [saving_goal],
        "num_expenses": [num_expenses]
    })
    for i, expense in enumerate(expenses):
        user_inputs_df[f"expense_name_{i}"] = expense['name']
        user_inputs_df[f"expense_amount_{i}"] = expense['amount']
        user_inputs_df[f"expense_day_{i}"] = expense['day']
    user_inputs_df.to_csv(user_inputs_file, index=False)


    # Display money evolution chart
    money_evolution_df = calculate_money_evolution(current_money, expenses, current_day, total_days)
    st.line_chart(money_evolution_df.set_index("Day"))

    # Display balance history chart
    st.line_chart(balance_history.set_index('Date'))
    balance_history['Date'] = pd.to_datetime(balance_history['Date'])






# If the user has clicked the "Reset" button
if st.button('Reset'):
    current_money = 0
    saving_goal = default_saving_goal
    balance_history = pd.DataFrame(columns=["Date", "Remaining Balance"])
    balance_history.to_csv(balance_history_file, index=False)

    # Reset user inputs
    user_inputs = {}
    user_inputs_df = pd.DataFrame(columns=["current_money", "saving_goal", "num_expenses"])
    user_inputs_df.to_csv(user_inputs_file, index=False)

if remaining_balance is not None:
    st.write(f"Your predicted remaining balance at the end of the month is: €{remaining_balance['Remaining Balance'].iloc[0]:.2f}")


    st.write(f"Your predicted disposable income at the end of the month is: €{(remaining_balance['Remaining Balance'].iloc[0] - saving_goal):.2f}")


# Pie chart for expenses breakdown
if expenses:
    expenses_df = pd.DataFrame(expenses)
    expenses_total = expenses_df['amount'].sum()
    expenses_df['Percentage'] = (expenses_df['amount'] / expenses_total) * 100
    st.header("Expenses Breakdown")
    st.dataframe(expenses_df)

    labels = expenses_df['name']
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(expenses_df['amount'].tolist(), labels=labels.tolist(), autopct='%1.1f%%')
    ax.set_aspect('equal')
    st.pyplot(fig)
