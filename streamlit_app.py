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

st.logo("images/logo.png")


years = st.sidebar.number_input("Years until my retirement", min_value=0, max_value=100, value=5, step=1)
current_job_salary = st.sidebar.number_input("Current Job Salary (k€/year)", min_value=0, value=100)
new_job_salary = st.sidebar.number_input("New job Salary (k€/year)", min_value=0, value=90)
salary_increase_input = st.sidebar.number_input("Expected yearly salary increase (%)", min_value=0.0, value=2.0, step=0.1)
salary_increase_rate = salary_increase_input / 100
#severance = st.sidebar.number_input("severance pay", min_value=0, value=200)
#yield_percent = st.sidebar.number_input("Yield (%)", min_value=0.0, value=5.0)

def calculate_final_salary(start_salary, increase, years):
    final_salary = start_salary * (1 + increase) ** years
    return final_salary


current_job_salary_final = calculate_final_salary(current_job_salary, salary_increase_rate, years)
new_job_salary_final = calculate_final_salary(new_job_salary, salary_increase_rate, years)

st.title("Do you want or need to change your current job?")

st.text("""
Have you ever wondered what that means for your salary? With this app, you can easily calculate the financial impact of a job change on your future salary and visualize the results.
""")
#st.text("") # vertical space


#info_text = f"""
#Do you want or need to change your current job? Have you ever wondered what that means for your salary?
#With this app, you can easily calculate the financial impact of a job change on your future salary and visualize the results.
#
#Note: I have deliberately not taken gross/net salary into account here, as this is highly individual. You may enter your
#gross or net salary, see online gross/net calculators to get your numbers.
#"""
#\tCompare your current salary with the new job’s salary:\n
#\t   # Current job: {current_job_salary:.02f} k€ will be {current_job_salary_final:.02f} k€ in {years} years with {salary_increase_input} % salary increase rate.\n
#\t   # New job: {new_job_salary:.02f} k€ will be {new_job_salary_final:.02f} k€ in {years} years with {salary_increase_input} % salary increase rate.\n
#\t   # Difference: First year: {new_job_salary - current_job_salary:.02f} k€ -> Last year: {new_job_salary_final - current_job_salary_final:.02f} k€


#st.info(info_text, icon="ℹ️")


def calculate_next_years_1(current_salary, salary_increase_rate, years):
    # init first cell with current salary
    data = {column_names[0]: [current_salary]}
    # calc the salary for the next years
    for i in range(1, years):
        previous_year_salary = data[column_names[i - 1]][0]
        new_salary = previous_year_salary * (1 + salary_increase_rate)
        data[column_names[i]] = [new_salary]

    return data

def add_calculations(df, name, initial_salary, salary_increase_rate) -> pd.DataFrame:
    data = {column_names[0]: [initial_salary]}

    # Berechne die Gehälter für die folgenden Jahre
    tmp_salary = initial_salary
    for i in range(1, df.shape[1]):
        previous_year_salary = data[column_names[i - 1]][0]
        tmp_salary = previous_year_salary * (1 + salary_increase_rate)
        data[column_names[i]] = [tmp_salary]

    salary_dict = [initial_salary * ((1 + salary_increase_rate) ** i) for i in range(len(column_names))]
    df.loc[name] = salary_dict

    return df

column_names = [float(i) for i in range(years+1)]
df = pd.DataFrame(columns=column_names)
df = add_calculations(df, "Current job", current_job_salary, salary_increase_rate)
df = add_calculations(df, "New job", new_job_salary, salary_increase_rate)

df.columns = df.columns.astype(float)
df = df.sort_index(axis=1)

# metrics
def overall_sum_4_job(df, job_name, column_names) -> float:
    sum = np.sum(df.loc[job_name, column_names].values)
    return sum

st.header("Key metrics")
col_1_1, col_1_2, col_1_3, col_1_4, col_1_5 = st.columns(5)
help_salary_new_job_initial = "Your start salary of the new job. With a comparision to your current's job salary."
col_1_1.metric(f"Salary new job inital",
               value=f"{new_job_salary} k€",
               delta=f"{new_job_salary-current_job_salary:.2f} k€",
               help=help_salary_new_job_initial)
help_salary_new_job_final = "Your salary of the new job when you retire. Compared to the current job's salary when you retire."
col_1_2.metric(f"Salary new job in {years} years",
               value=f"{new_job_salary_final:.2f} k€",
               delta=f"{(new_job_salary_final-current_job_salary_final):.2f} k€",
               help=help_salary_new_job_final
               )
#current_job_final_salary = calculate_final_salary(current_job_salary, salary_increase_rate, years)

current_job_overall_salary = overall_sum_4_job(df, "Current job", column_names)
help_overall_sum_current = "The sum of your current job's salary until your retirement."
col_1_3.metric("Overall sum current job",
               value=f"{current_job_overall_salary:.2f} k€",
               help=help_overall_sum_current)
help_overall_sum_new = "The sum of your new job's salary until your retirement."
new_job_overall_salary = overall_sum_4_job(df, "New job", column_names)
col_1_4.metric("Overall sum new job",
               value=f"{new_job_overall_salary:.2f} k€",
               help=help_overall_sum_new
               )
overall_difference = new_job_overall_salary - current_job_overall_salary
help_overall_delta = f"The is the cumulative salary for the next {years} years. New job vs. current job."
col_1_5.metric("Overall delta",
               value=f"{overall_difference:.2f} k€",
               help=help_overall_delta)

col_3_1, col_3_2, col_3_3, col_3_4 = st.columns([2,1,1,1])
col_3_1.header("Future development")

with col_3_2:
    data_type = st.radio(
        "View",
        ["Yearly", "Overall sum"],
        label_visibility="collapsed"
    )

#with col_3_3:
#    value_type = st.radio(
#        "Value",
#        ["Absolute", "Difference"]
#    )
value_type = "Absolute"

with col_3_3:
    chart_type = st.radio(
        "Chart type",
        ["Bar", "Line"],
        label_visibility="collapsed",
    )

if data_type == "Yearly":
    if chart_type == "Line":    # yearly + line
        df_t = df.T
        st.line_chart(df_t)
    else:                       # yearly + bar
        df_t = df.T
        st.bar_chart(df_t, stack=False)

elif data_type == "Overall sum":
    # Berechne die kumulative Summe für jedes Jahr
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
column_config_float = {}
for col in column_names:
    column_config_float[col] = st.column_config.NumberColumn(
        f"+ {int(col)} years",
        help=f"Your future income in {int(col)} years.",
        min_value=0,
        #step=1,
        format="%.2f k€",
        )

st.dataframe(df,  column_config=column_config_float
)


#        cumsum_diff = df_cumsum.loc["New job"] - df_cumsum.loc['Current job']
#        df_cumsum_diff  = pd.DataFrame(cumsum_diff)
#        if value_type == "Absolute":
#            if chart_type == "Line":
#                df_cumsum_t = df_cumsum_diff.T
#                st.line_chart(df_cumsum_t)
#            else:
#                df_cumsum_diff_t = df_cumsum_diff.T
#                st.bar_chart(df_cumsum_diff_t, stack=False)
#        else:
#                if chart_type == "Line":
#                    df_cumsum_diff_t = df_cumsum_diff.T
#                    st.line_chart(df_cumsum_diff_t)
#                else:
#                    df_cumsum_diff_t = df_cumsum_diff.T
#                    st.bar_chart(df_cumsum_diff_t, stack=False)
#

#  cumsum_diff = df_cumsum.loc["New job"] - df_cumsum.loc['Current job']
#        df_cumsum_diff  = pd.DataFrame(cumsum_diff)
#        if value_type == "Absolute":
#            if chart_type == "Line":
#                df_cumsum_t = df_cumsum_diff.T
#                st.line_chart(df_cumsum_t)
#            else:
#                df_cumsum_diff_t = df_cumsum_diff.T
#                st.bar_chart(df_cumsum_diff_t, stack=False)
#        else:
#                if chart_type == "Line":
#                    df_cumsum_diff_t = df_cumsum_diff.T
#                    st.line_chart(df_cumsum_diff_t)
#                else:
#                    df_cumsum_diff_t = df_cumsum_diff.T
#                    st.bar_chart(df_cumsum_diff_t, stack=False)
#



st.text("""
Note: I have deliberately not taken gross/net salary into account here, as this is highly individual. You may enter your 
gross or net salary, see online gross/net calculators to get your numbers.
"""
)