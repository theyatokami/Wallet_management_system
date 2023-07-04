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
expenses = []
incomes = []
if os.path.exists(user_inputs_file):
    user_inputs_df = pd.read_csv(user_inputs_file)
    if not user_inputs_df.empty:
        user_inputs = user_inputs_df.iloc[0].to_dict()
        for i in range(int(user_inputs.get("num_expenses", 0))):
            expenses.append({
                "name": user_inputs.get(f"expense_name_{i}", ""),
                "frequency": user_inputs.get(f"expense_frequency_{i}", ""),
                "amount": user_inputs.get(f"expense_amount_{i}", 0),
                "day": user_inputs.get(f"expense_day_{i}", 0),
            })
        for i in range(int(user_inputs.get("num_incomes", 0))):
            incomes.append({
                "name": user_inputs.get(f"income_name_{i}", ""),
                "frequency": user_inputs.get(f"income_frequency_{i}", ""),
                "amount": user_inputs.get(f"income_amount_{i}", 0),
                "day": user_inputs.get(f"income_day_{i}", 0),
            })


def calculate_money_evolution(current_money, expenses, incomes, current_day, total_days):
    remaining_balances = []
    for day in range(current_day, total_days + 1):
        daily_expense = 0
        daily_income = 0
        for expense in expenses:
            if expense['frequency'] == 'daily':
                daily_expense += expense['amount']
            elif expense['frequency'] == 'weekly':
                if (day - current_day) % 7 == 0:
                    daily_expense += expense['amount']
            elif expense['frequency'] == 'monthly':
                if day == int(expense['day']):
                    daily_expense += expense['amount']
        for income in incomes:
            if income['frequency'] == 'daily':
                daily_income += income['amount']
            elif income['frequency'] == 'weekly':
                if (day - current_day) % 7 == 0:
                    daily_income += income['amount']
            elif income['frequency'] == 'monthly':
                if day == int(income['day']):
                    daily_income += income['amount']
        remaining_balance = current_money - daily_expense + daily_income
        remaining_balances.append(remaining_balance)
        current_money = remaining_balance
    return pd.DataFrame({"Day": np.arange(current_day, total_days + 1), "Remaining Balance": remaining_balances})


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

# Set layout for 16:9 ratio screen
col1, col2 = st.columns(2)

# Incomes inputs
with col1:
    st.markdown("---")
    st.header("Incomes")
    st.markdown("<style>h2 {color: green;}</style>", unsafe_allow_html=True)  # Change header color to green
    num_incomes = st.number_input("Number of Incomes", min_value=0, max_value=None, value=int(user_inputs.get("num_incomes", 0)))

    incomes = []
    for i in range(num_incomes):
        st.subheader(f"Income #{i+1}")
        name = st.text_input("Name", value=user_inputs.get(f"income_name_{i}", ""), key=f"income_name_{i}")
        frequency = st.selectbox("Frequency", options=["daily", "weekly", "monthly"], index=["daily", "weekly", "monthly"].index(user_inputs.get(f"income_frequency_{i}", "monthly")), key=f"income_frequency_{i}")
        amount = st.number_input("Amount", value=user_inputs.get(f"income_amount_{i}", 0.0), step=1.0, format="%.2f", key=f"income_amount_{i}")
        if frequency == "monthly":
            day_value = user_inputs.get(f"income_day_{i}", 1)
            day = st.number_input("Day of the month", min_value=1, max_value=31, value=int(day_value) if pd.notna(day_value) else 1, key=f"income_day_{i}")
        else:
            day = None
        incomes.append({"name": name, "frequency": frequency, "amount": amount, "day": day})

# Expenses inputs
with col2:
    st.markdown("---")
    st.header("Expenses")
    st.markdown("<style>h2 {color: red;}</style>", unsafe_allow_html=True)  # Change header color to red
    num_expenses = st.number_input("Number of Expenses", min_value=0, max_value=None, value=int(user_inputs.get("num_expenses", 0)))

    expenses = []
    for i in range(num_expenses):
        st.subheader(f"Expense #{i+1}")
        name = st.text_input("Name", value=user_inputs.get(f"expense_name_{i}", ""), key=f"expense_name_{i}")
        frequency = st.selectbox("Frequency", options=["daily", "weekly", "monthly"], index=["daily", "weekly", "monthly"].index(user_inputs.get(f"expense_frequency_{i}", "daily")), key=f"expense_frequency_{i}")

        amount = st.number_input("Amount", value=user_inputs.get(f"expense_amount_{i}", 0.0), step=1.0, format="%.2f", key=f"expense_amount_{i}")
        if frequency == "monthly":
            day_value = user_inputs.get(f"expense_day_{i}", 1)
            day = st.number_input("Day of the month", min_value=1, max_value=31, value=int(day_value) if pd.notna(day_value) else 1, key=f"expense_day_{i}")
        else:
            day = None
        expenses.append({"name": name, "frequency": frequency, "amount": amount, "day": day})

# If the user has clicked the "Submit" button
if st.button('Submit'):
    remaining_balance = calculate_money_evolution(current_money, expenses, incomes, current_day, total_days)
    new_row = pd.DataFrame({"Date": [now.strftime("%Y-%m-%d")], "Remaining Balance": [remaining_balance["Remaining Balance"].values[0]]})

    balance_history = pd.concat([balance_history, new_row], ignore_index=True)
    balance_history.to_csv(balance_history_file, index=False)

    # Save user inputs
    user_inputs_df = pd.DataFrame({
        "current_money": [current_money],
        "saving_goal": [saving_goal],
        "num_expenses": [num_expenses],
        "num_incomes": [num_incomes]
    })
    for i, expense in enumerate(expenses):
        user_inputs_df[f"expense_name_{i}"] = expense['name']
        user_inputs_df[f"expense_frequency_{i}"] = expense['frequency']
        user_inputs_df[f"expense_amount_{i}"] = expense['amount']
        user_inputs_df[f"expense_day_{i}"] = expense['day']
    for i, income in enumerate(incomes):
        user_inputs_df[f"income_name_{i}"] = income['name']
        user_inputs_df[f"income_frequency_{i}"] = income['frequency']
        user_inputs_df[f"income_amount_{i}"] = income['amount']
        user_inputs_df[f"income_day_{i}"] = income['day']
    user_inputs_df.to_csv(user_inputs_file, index=False)

    # Display money evolution chart
    money_evolution_df = calculate_money_evolution(current_money, expenses, incomes, current_day, total_days)
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
    st.write(f"Your remaining balance at the end of the month will be: €{remaining_balance['Remaining Balance'].iloc[-1]:.2f}")
    st.write(f"Your disposable income at the end of the month will be: €{(remaining_balance['Remaining Balance'].iloc[-1] - saving_goal):.2f}")



# Pie chart for expenses breakdown
if expenses:
    # Existing code
    expenses_df = pd.DataFrame(expenses)
    expenses_total = expenses_df['amount'].sum()

    # New code to calculate total amount for each expense
    expenses_df['total_amount'] = np.where(expenses_df['frequency'] == 'daily', expenses_df['amount'] * 30,
                                            np.where(expenses_df['frequency'] == 'weekly', expenses_df['amount'] * 4,
                                                    expenses_df['amount']))

    # Calculate new total for all expenses
    expenses_total = expenses_df['total_amount'].sum()

    # New code to calculate percentage based on total_amount
    expenses_df['Percentage'] = (expenses_df['total_amount'] / expenses_total) * 100

    st.header("Expenses Breakdown")
    st.dataframe(expenses_df)

    labels = expenses_df['name']
    fig, ax = plt.subplots(figsize=(6, 6))
    # Use total_amount for the pie chart
    ax.pie(expenses_df['total_amount'].tolist(), labels=labels.tolist(), autopct='%1.1f%%')
    ax.set_aspect('equal')
    st.pyplot(fig)

