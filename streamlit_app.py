import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Job Change Calculator",
    page_icon=":moneybag:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/kaimoritz/job_change_calculator',
        'Report a bug': "https://github.com/kaimoritz/job_change_calculator",
        'About': "Version 1.0 | Created by Kai Moritz."
    }
)

TYPE_OF_INCOME = "Type of income"
NEW_JOB = "Salary new job"
CURRENT_JOB = "Salary current Job"
ANNUAL_SEVERANCE_PAY = "Severance pay (annual)"
TOTAL_NEW_JOB = f"Total: {NEW_JOB} + {ANNUAL_SEVERANCE_PAY}"

st.logo("images/logo.png")
st.sidebar.text("")  # vertical space

# sidebar: parameter input
help_year="Enter the number of years you want work until retirement."
years = st.sidebar.number_input("Years until my retirement", min_value=0, max_value=100, value=5, step=1, help=help_year)

help_current_job_salary = "Enter the salary of your CURRENT job. You can enter your gross or net salary, but then enter gross or net everywhere."
current_job_salary = st.sidebar.number_input("Current Job Salary (k€/year)", min_value=0, value=100, help=help_current_job_salary)

help_new_job_salary = "Enter the salary of your NEW job. You can enter your gross or net salary, but then enter gross or net everywhere."
new_job_salary = st.sidebar.number_input("New job Salary (k€/year)", min_value=0, value=90, help=help_new_job_salary)

help_salary_increase_input="Enter the expected annual salary increase in percent. E.g. '2.00'%."
salary_increase_input = st.sidebar.number_input("Expected annual salary increase rate (%)",
                                                min_value=0.0,
                                                value=0.0,
                                                step=0.1,
                                                help=help_salary_increase_input)
salary_increase_rate = salary_increase_input / 100

severance_pay = 0
severance_annual_rate = 0
help_severance_paid= "If you will receive a severance pay, activate the checkbox and enter your numbers."
severance_paid = st.sidebar.checkbox("I will receive a severance pay", help=help_severance_paid)
if severance_paid:
    help_severance_pay="Enter the amount of severance pay you will receive. You can enter your gross or net salary, but then enter gross or net everywhere."
    severance_pay = st.sidebar.number_input("Severance pay (k€)", min_value=0, value=50, step=1, help=help_severance_pay)
    help_severance_annual_pay="You can use the severance pay you receive to compensate for a lower salary in your new job. To do this, you pay yourself the desired amount of your severance pay each year."
    severance_annual_rate = st.sidebar.number_input("Annual payment from severance pay (yearly/k€)",
                                                    min_value=0,
                                                    value=10,
                                                    help=help_severance_annual_pay)

st.sidebar.text("") # vertical space
st.sidebar.write("<sup>Reset: Press 'STRG'+'F5'</sup>", unsafe_allow_html=True)

def calculate_final_salary(start_salary, increase, years):
    final_salary = start_salary * (1 + increase) ** years
    return final_salary


current_job_salary_final = calculate_final_salary(current_job_salary, salary_increase_rate, years)
new_job_salary_final = calculate_final_salary(new_job_salary, salary_increase_rate, years)

st.title("Do you want or need to change your current job?")

st.text("""
Have you ever wondered what that means for your salary? With this app, you can easily calculate the financial 
impact of a job change on your future salary and visualize the results.
""")


def add_calculations_salary_in_the_next_years(df, name, initial_salary, salary_increase_rate) -> pd.DataFrame:
    data = {column_names[0]: [initial_salary]}
    # calculate the salaries for the next years
    tmp_salary = initial_salary
    for i in range(1, df.shape[1]):
        previous_year_salary = data[column_names[i-1]][0]
        tmp_salary = previous_year_salary * (1 + salary_increase_rate)
        data[column_names[i]] = [tmp_salary]

    salary_dict = [initial_salary * ((1 + salary_increase_rate) ** i) for i in range(len(column_names))]
    df.loc[name] = salary_dict

    return df


def add_severance_payments(df, severance_pay, annual_payment) -> pd.DataFrame:
    # Calculation of payments
    payments = []
    remaining_balance = severance_pay

    for year in column_names:
        if year == column_names[-1]:
            payments.append(remaining_balance)
        else:
            if remaining_balance >= annual_payment:
                payments.append(annual_payment)
                remaining_balance -= annual_payment
            else:
                payments.append(remaining_balance)
                remaining_balance = 0

    # Add new row to DataFrame
    df.loc[ANNUAL_SEVERANCE_PAY] = payments

    # add new row for new job + severance
    df.loc[TOTAL_NEW_JOB] = np.add(df.loc[NEW_JOB], df.loc[ANNUAL_SEVERANCE_PAY])

    return df


column_names = [float(i) for i in range(1, years+1)]
df = pd.DataFrame(columns=column_names)
df.index.name = TYPE_OF_INCOME
df = add_calculations_salary_in_the_next_years(df, CURRENT_JOB, current_job_salary, salary_increase_rate)
df = add_calculations_salary_in_the_next_years(df, NEW_JOB, new_job_salary, salary_increase_rate)
if severance_paid:
    df = add_severance_payments(df, severance_pay, severance_annual_rate)

df.columns = df.columns.astype(float)
df = df.sort_index(axis=1)


# metrics
def overall_sum_4_job(df, job_name, column_names) -> float:
    sum = np.sum(df.loc[job_name, column_names].values)
    return sum


st.header("Key metrics")
col_1_1, col_1_2, col_1_3, col_1_4, col_1_5, col_1_6 = st.columns(6)
help_salary_new_job_initial = "Enter your starting salary of the new job. With a comparision to your current's job salary."
col_1_1.metric(f"Starting salary new job",
               value=f"{new_job_salary} k€",
               delta=f"{new_job_salary - current_job_salary:.2f} k€",
               help=help_salary_new_job_initial)
if salary_increase_rate > 0.0:
    help_salary_new_job_final = f"This is the salary of the new job when you retire. This takes into account the 'Expected annual salary increase rate (%)' of {salary_increase_rate}%. Compared to the current job's salary when you retire."
    col_1_2.metric(f"Salary new job in {years} years",
                   value=f"{new_job_salary_final:.2f} k€",
                   delta=f"{(new_job_salary_final - current_job_salary_final):.2f} k€",
                   help=help_salary_new_job_final
                   )

current_job_overall_salary = overall_sum_4_job(df, CURRENT_JOB, column_names)
help_overall_sum_current = "The sum of your current job's salary until your retirement."
col_1_3.metric("Overall sum current job",
               value=f"{current_job_overall_salary:.2f} k€",
               help=help_overall_sum_current)

help_overall_sum_new = "The sum of your new job's salary until your retirement. Does not include the severance pay."
new_job_overall_salary = overall_sum_4_job(df, NEW_JOB, column_names)
col_1_4.metric("Overall sum new job",
               value=f"{new_job_overall_salary:.2f} k€",
               help=help_overall_sum_new
               )

help_severance = "Amount of your severance pay, if received"
col_1_5.metric("Severance pay",
               value=f"{severance_pay:.2f} k€",
               help=help_severance
               )

overall_delta = new_job_overall_salary + severance_pay - current_job_overall_salary
help_overall_delta = f"The is the cumulative income for the next {years} years, including the severance pay of {severance_pay} k€. New job+severance pay vs. current job."
col_1_6.metric("Overall delta",
               value=f"{overall_delta:.2f} k€",
               delta=f"{overall_delta:.2f} k€",
               help=help_overall_delta)



col_3_1, col_3_2, col_3_3, col_3_4 = st.columns([3, 1, 1, 1])
col_3_1.header("Future development of your income")

with col_3_3:
    data_type = st.radio(
        "View",
        ["Yearly", "Overall sum"],
        label_visibility="collapsed"
    )

with col_3_4:
    chart_type = st.radio(
        "Chart type",
        ["Bar", "Line"],
        label_visibility="collapsed",
    )

if data_type == "Yearly":
    if chart_type == "Line":  # yearly + line
        df_t = df.T
        st.line_chart(df_t)
    else:  # yearly + bar
        df_t = df.T
        st.bar_chart(df_t, stack=False)

elif data_type == "Overall sum":
    # calculate the cumulative sum for each year
    df_cumsum = df.cumsum(axis=1)
    if chart_type == "Line":
        df_cumsum_t = df_cumsum.T
        st.line_chart(df_cumsum_t)
    else:
        df_cumsum_t = df_cumsum.T
        st.bar_chart(df_cumsum_t, stack=False)

st.header("Detailed calculation")

# column configs:
# create a number float %.1f only for dtype float (-> dynamic names "relevant month)
column_config = {}
for col in column_names:
    column_config[col] = st.column_config.NumberColumn(
        f"{int(col)}. year",
        help=f"Your future income in the {int(col)}. year.",
        min_value=0,
        # step=1,
        format="%.2f k€",
    )
# add column config for index / "type"
column_config[df.index.name] = st.column_config.TextColumn(width=220)

st.dataframe(df, column_config=column_config)

st.text("""
Note: I have deliberately not taken gross/net salary into account here, as this is highly individual. You may enter your 
gross or net salary, see online gross/net calculators to get your numbers.
"""
        )
