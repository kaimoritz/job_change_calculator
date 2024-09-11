import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Job Change Calculator",
    page_icon=":moneybag:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': "https://github.com/kaimoritz/job_change_calculator",
        'Report a bug': "https://github.com/kaimoritz/job_change_calculator",
        'About': "Version 1.0 | Created by Kai Moritz."
    }
)

TYPE_OF_INCOME = "Type of income"
NEW_JOB = "Salary new job"
CURRENT_JOB = "Salary current Job"
ANNUAL_COMPENSATIOIN = "Compensation payment (annual)"
TOTAL_NEW_JOB = f"Total: {NEW_JOB} + {ANNUAL_COMPENSATIOIN}"

st.logo("images/logo.png")
st.sidebar.text("")  # vertical space

# sidebar: parameter input
help_year = "Enter the number of years you want work until retirement."
years = st.sidebar.number_input("Years until my retirement", min_value=0, max_value=100, value=10, step=1,
                                help=help_year)

help_current_job_salary = "Enter the salary of your CURRENT job. You can enter your gross or net salary, but then enter gross or net everywhere."
current_job_salary = st.sidebar.number_input("Current Job Salary (k€/year)", min_value=0, value=100,
                                             help=help_current_job_salary)

help_new_job_salary = "Enter the salary of your NEW job. You can enter your gross or net salary, but then enter gross or net everywhere."
new_job_salary = st.sidebar.number_input("New job Salary (k€/year)", min_value=0, value=80, help=help_new_job_salary)

help_salary_increase_input = "Enter the expected annual salary increase in percent. E.g. '2.00'%."
salary_increase_input = st.sidebar.number_input("Expected annual salary increase rate (%)",
                                                min_value=0.0,
                                                value=0.0,
                                                step=0.1,
                                                help=help_salary_increase_input)
salary_increase_rate = salary_increase_input / 100

compensation_payment = 0
compensation_annual_rate = 0
help_compensation_paid = "If you will receive a compensation payment, activate the checkbox and enter your numbers."
compensation_paid = st.sidebar.checkbox("I will receive a compensation payment", help=help_compensation_paid)
if compensation_paid:
    help_compensation_payment = "Enter the amount of compensation payment you will receive. You can enter your gross or net salary, but then enter gross or net everywhere."
    compensation_payment = st.sidebar.number_input("Compensation payment (k€)", min_value=0, value=100, step=1,
                                                   help=help_compensation_payment)
    help_compensation_annual_payment = "You can use the compensation payment you receive to compensate for a lower salary in your new job. To do this, you pay yourself the desired amount of your compensation payment each year."
    compensation_annual_rate = st.sidebar.number_input("Annual payment from compensation payment (yearly/k€)",
                                                       min_value=0,
                                                       value=20,
                                                       help=help_compensation_annual_payment)

st.sidebar.text("")  # vertical space
st.sidebar.write("<sup>Reset: Press 'STRG'+'F5'</sup>", unsafe_allow_html=True)


def calculate_final_salary(start_salary, increase, years):
    final_salary = start_salary * (1 + increase) ** (
                years - 1)  # years-1 because the first increase is wfter the first year.
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
        previous_year_salary = data[column_names[i - 1]][0]
        tmp_salary = previous_year_salary * (1 + salary_increase_rate)
        data[column_names[i]] = [tmp_salary]

    salary_dict = [initial_salary * ((1 + salary_increase_rate) ** i) for i in range(len(column_names))]
    df.loc[name] = salary_dict

    return df


def add_compensation_payments(df, compensation_payment, annual_payment) -> pd.DataFrame:
    # Calculation of payments
    payments = []
    remaining_balance = compensation_payment

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
    df.loc[ANNUAL_COMPENSATIOIN] = payments

    # add new row for new job + compensation
    df.loc[TOTAL_NEW_JOB] = np.add(df.loc[NEW_JOB], df.loc[ANNUAL_COMPENSATIOIN])

    return df


column_names = [float(i) for i in range(1, years + 1)]
df = pd.DataFrame(columns=column_names)
df.index.name = TYPE_OF_INCOME
df = add_calculations_salary_in_the_next_years(df, CURRENT_JOB, current_job_salary, salary_increase_rate)
df = add_calculations_salary_in_the_next_years(df, NEW_JOB, new_job_salary, salary_increase_rate)
if compensation_paid:
    df = add_compensation_payments(df, compensation_payment, compensation_annual_rate)

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
    help_salary_new_job_final = (f"This is the salary of the new job when you retire ({new_job_salary_final:.2f} k€). "
                                 f"This takes into account the 'Expected annual salary increase rate (%)' of "
                                 f"{salary_increase_rate}%. Compared to the current job's salary "
                                 f"({(current_job_salary_final):.2f} k€) when you retire.")
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

help_overall_sum_new = "The sum of your new job's salary until your retirement. Does not include the compensation payment."
new_job_overall_salary = overall_sum_4_job(df, NEW_JOB, column_names)
col_1_4.metric("Overall sum new job",
               value=f"{new_job_overall_salary:.2f} k€",
               help=help_overall_sum_new
               )

help_compenstation = "Amount of your compensation payment, if received"
col_1_5.metric("Severance pay",
               value=f"{compensation_payment:.2f} k€",
               help=help_compenstation
               )

overall_delta = new_job_overall_salary + compensation_payment - current_job_overall_salary
help_overall_delta = (f"The is the cumulative income for the next {years} years, including the compensation payment of "
                      f"{compensation_payment} k€. New job+compensation payment vs. current job.")
col_1_6.metric("Overall delta",
               value=f"{overall_delta:.2f} k€",
               delta=f"{overall_delta:.2f} k€",
               help=help_overall_delta)

col_3_1, col_3_2, col_3_3, col_3_4 = st.columns([3, 1, 1, 1])
col_3_1.header("Future development of your income")

with col_3_3:
    data_type = st.radio(
        "View",
        ["Yearly", "Difference", "Overall sum"],
        label_visibility="collapsed"
    )

with col_3_4:
    chart_type = st.radio(
        "Chart type",
        ["Bar", "Line"],
        label_visibility="collapsed",
    )


def plot_bar_chart(_df):
    # convert df into "longer" format, because it is easier for plotly
    df_long = _df.reset_index().melt(id_vars=TYPE_OF_INCOME, var_name='Year', value_name='Income')
    fig = px.bar(df_long, x='Year', y='Income', color=TYPE_OF_INCOME, barmode='group')
    # set legend
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        legend_title=None,
        yaxis_title="Income (k€)"
    )
    st.plotly_chart(fig, use_container_width=True)



def plot_line_chart(_df_cumsum):
    # convert df into "longer" format, because it is easier for plotly
    df_long = _df_cumsum.reset_index().melt(id_vars=TYPE_OF_INCOME, var_name='Year', value_name='Income')
    fig = px.line(df_long, x='Year', y='Income', color=TYPE_OF_INCOME, markers=True)
    fig.update_xaxes(tickmode='linear', dtick=1)  # only full years
    # set legend
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        legend_title=None,
        yaxis=dict(range=[0, df_long['Income'].max() * 1.1]),  # Y-axis start with '0'
        yaxis_title="Income (k€)"
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_difference_bar_chart(_df):
    if compensation_paid == 0:
        # -> difference between CURRENT_JOB, NEW_JOB
        df_diff = _df.loc[[CURRENT_JOB, NEW_JOB]].diff().iloc[1].reset_index()
        title = f"Difference between {CURRENT_JOB} and {NEW_JOB}"
    else:
        # -> difference between CURRENT_JOB, TOTAL_NEW_JOB
        df_diff = _df.loc[[CURRENT_JOB, TOTAL_NEW_JOB]].diff().iloc[1].reset_index()
        title = f"Difference between '{CURRENT_JOB}' and '{TOTAL_NEW_JOB}'"
    df_diff.columns = ['Year', 'Difference']
    # add colors: negative is red, positive is green
    df_diff['Color'] = df_diff['Difference'].apply(lambda x: 'red' if x < 0 else 'green')
    fig = px.bar(df_diff,
                 x='Year',
                 y='Difference',
                 title=title,
                 color='Color',
                 color_discrete_map={'red': '#D62728', 'green': '#2CA02C'})

    # set y axis to always display the "0"-line
    y_min = min(df_diff['Difference'].min(), -5.0)
    y_max = max(df_diff['Difference'].max(), 5.0)
    fig.update_layout(yaxis=dict(range=[y_min, y_max * 1.1]),
                      yaxis_title="Difference (k€)",
                      showlegend=False,
                      title_font=dict(size=14, family="Arial", weight="normal"),
                      title_x=0.25,  # centered title
                      title_y=0.0  # title below the chart
                      )

    st.plotly_chart(fig, use_container_width=True)


def plot_difference_line_char(_df):
    if compensation_paid == 0:
        # -> difference between CURRENT_JOB, NEW_JOB
        df_diff = _df.loc[[CURRENT_JOB, NEW_JOB]].diff().iloc[1].reset_index()
        title = f"Difference between '{CURRENT_JOB}' and '{NEW_JOB}'"
    else:
        # -> difference between CURRENT_JOB, TOTAL_NEW_JOB
        df_diff = _df.loc[[CURRENT_JOB, TOTAL_NEW_JOB]].diff().iloc[1].reset_index()
        title = f"Difference between '{CURRENT_JOB}' and '{TOTAL_NEW_JOB}'"
    df_diff.columns = ['Year', 'Difference']
    fig = px.line(df_diff, x='Year', y='Difference', title=title, markers=True)
    # set y axis to always display the "0"-line
    y_min = min(df_diff['Difference'].min(), -5.0)
    y_max = max(df_diff['Difference'].max(), 5.0)
    fig.update_layout(yaxis=dict(range=[y_min, y_max * 1.1]),
                      yaxis_title="Income (k€)",
                      showlegend=False,
                      title_font=dict(size=14, family="Arial", weight="normal"),
                      title_x=0.25, # centered title
                      title_y=0.0 # title below the chart
                      )

    st.plotly_chart(fig, use_container_width=True)


if data_type == "Yearly":
    if chart_type == "Line":  # yearly + line
        plot_line_chart(df)
    else:  # yearly + bar
        plot_bar_chart(df)

elif data_type == "Overall sum":
    # calculate the cumulative sum for each year
    df_cumsum = df.cumsum(axis=1)
    if chart_type == "Line":
        plot_line_chart(df_cumsum)
    else:
        plot_bar_chart(df_cumsum)

elif data_type == "Difference":
    if chart_type == "Line":  # yearly + line
        plot_difference_line_char(df)
    else:  # yearly + bar
        df_t = df.T
        plot_difference_bar_chart(df)

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

st.write("""Note: I have deliberately not taken gross/net salary into account here, as this is highly individual. You 
may enter your your gross or net salary, but you should than stick to one type - don't  mix it up. Check out a <a 
href='https://www.lexware.de/werkzeuge-ebooks/brutto-netto-rechner/' id='gross-net-link'>online gross/net 
calculators</a> to get your numbers. In particular, the calculation of the net amount of the compensation payment 
must be considered separately. Compensation payments may have a higher taxation than your salary. For more details see 
<a href='https://www.lexware.de/werkzeuge-ebooks/abfindungsrechner/' id='gross-net-link'> online compensation payment 
calculators</a> """, unsafe_allow_html=True)
