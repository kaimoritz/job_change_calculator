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
        'About': "Version 2.0 | Created by Kai Moritz."
    }
)

# income types (index values for dataframe) for "normal" yearly view:
TYPE_OF_INCOME = "Type of income"
CURRENT_JOB = "Salary current Job"
NEW_JOB = "Salary new job"
ANNUAL_COMPENSATION = "Compensation payment (annual)"
COMPENSATION_ACCOUNT_BALANCE = "Remaining compensation (incl. investment revenue)"  # the remaining heigt of the compensation over the years
TOTAL_NEW_JOB = f"Total: {NEW_JOB} + {ANNUAL_COMPENSATION}"
DIFFERENCE_NJ_CJ = f"Difference {NEW_JOB} vs. {CURRENT_JOB}"
DIFFERENCE_NJ_CJ_COMP = f"Difference {NEW_JOB} vs {CURRENT_JOB} + {ANNUAL_COMPENSATION}"

# income types (index values for dataframe) for cummulated "Overall sum":
CURRENT_JOB_CUM_SUM = f"Overall sum {CURRENT_JOB}"
NEW_JOB_CUM_SUM = f"Overall sum {NEW_JOB}"
ANNUAL_COMPENSATION_SUM = f"Overall sum {ANNUAL_COMPENSATION}"
TOTAL_NEW_JOB_SUM = f"Overall sum {TOTAL_NEW_JOB}"
DIFFERENCE_NJ_CJ_SUM = f"Overall sum {DIFFERENCE_NJ_CJ}"
DIFFERENCE_NJ_CJ_COMP_SUM = f"Overall sum {DIFFERENCE_NJ_CJ_COMP}"

# color scheme for the charts
COLOR_CURRENT_JOB = "#83C9FF"
COLOR_NEW_JOB = "#0068C9"
COLOR_ANNUAL_COMPENSATION = "#FFB74D"
COLOR_TOTAL_NEW_JOB = "#7F7F7F"
COLOR_POSITIVE = "#4CAF50"
COLOR_NEGATIVE = "#E57373"
COLOR_DIFFERENCE = "#9C27B0"

color_discrete_map = {CURRENT_JOB: COLOR_CURRENT_JOB,
                      CURRENT_JOB_CUM_SUM: COLOR_CURRENT_JOB,
                      NEW_JOB: COLOR_NEW_JOB,
                      NEW_JOB_CUM_SUM: COLOR_NEW_JOB,
                      ANNUAL_COMPENSATION: COLOR_ANNUAL_COMPENSATION,
                      ANNUAL_COMPENSATION_SUM: COLOR_ANNUAL_COMPENSATION,
                      TOTAL_NEW_JOB: COLOR_TOTAL_NEW_JOB,
                      TOTAL_NEW_JOB_SUM: COLOR_TOTAL_NEW_JOB
                      }

st.logo("images/logo.png")
st.sidebar.text("")  # vertical space

# sidebar: parameter input
help_year = "Enter the number of years you want work until retirement."
years = st.sidebar.number_input("Years until my retirement",
                                min_value=0,
                                max_value=100,
                                value=10,
                                step=1,
                                help=help_year)

help_current_job_salary = ("Enter the salary of your CURRENT job. You can enter your gross or net salary, but then "
                           "enter gross or net everywhere.")
current_job_salary = st.sidebar.number_input("Current Job Salary (k€/year)",
                                             min_value=0,
                                             max_value=1000,
                                             value=100,
                                             help=help_current_job_salary)

help_new_job_salary = ("Enter the salary of your NEW job. You can enter your gross or net salary, but then enter gross "
                       "or net everywhere.")
new_job_salary = st.sidebar.number_input("New job Salary (k€/year)",
                                         min_value=0,
                                         max_value=1000,
                                         value=80,
                                         help=help_new_job_salary)

help_salary_increase_input = "Enter the expected annual salary increase in percent. E.g. '2.00'%."
salary_increase_input = st.sidebar.number_input("Expected annual salary increase rate (%)",
                                                min_value=0.0,
                                                max_value=100.0,
                                                value=0.0,
                                                step=0.1,
                                                help=help_salary_increase_input)
salary_increase_percent = salary_increase_input / 100

compensation_payment = 0
compensation_annual_rate = 0
investment_revenue_input = 0
investment_revenue_percent = 0.0

help_compensation_paid = "If you will receive a compensation payment, activate the checkbox and enter your numbers."
compensation_paid = st.sidebar.checkbox("I will receive a compensation payment", help=help_compensation_paid)

if compensation_paid:
    help_compensation_payment = ("Enter the amount of compensation payment you will receive. You can enter your gross "
                                 "or net salary, but then enter gross or net everywhere.")
    compensation_payment = st.sidebar.number_input("Compensation payment (k€)",
                                                   min_value=0,
                                                   max_value=1000,
                                                   value=90,
                                                   step=1,
                                                   help=help_compensation_payment)

    help_compensation_annual_payment = ("You can use the compensation payment you receive to compensate for a lower "
                                        "salary in your new job. To do this, you pay yourself the desired amount of "
                                        "your compensation payment each year.")
    compensation_annual_rate = st.sidebar.number_input("Annual payout from compensation payment (yearly/k€)",
                                                       min_value=0,
                                                       max_value=1000,
                                                       value=25,
                                                       help=help_compensation_annual_payment)

    help_investment_revenue_input = ("If you plan to invest your compensation payment (e.g. ETF, stocks, gold, ...), "
                                     "enter the expected annual increase in value including dividend (e.g. 5%).")
    investment_revenue_input = st.sidebar.number_input("Expected annual revenue from investment (%)",
                                                       min_value=0.0,
                                                       max_value=500.0,
                                                       value=0.0,
                                                       step=0.1,
                                                       help=help_investment_revenue_input)
    investment_revenue_percent = investment_revenue_input / 100  # 2% -> 0.02

st.sidebar.text("")  # vertical space
st.sidebar.write("<sup>Reset: Press 'STRG'+'F5'</sup>", unsafe_allow_html=True)

st.title("Do you want or need to change your current job?")
st.text("""
Have you ever wondered what that means for your salary? With this app, you can easily calculate the financial 
impact of a job change on your future salary and visualize the results.
""")


def add_calculations_salary_in_the_next_years(_df, _name, _initial_salary, _salary_increase_rate) -> pd.DataFrame:
    data = {column_names[0]: [_initial_salary]}
    # calculate the salaries for the next years
    tmp_salary = _initial_salary
    for i in range(1, _df.shape[1]):
        previous_year_salary = data[column_names[i - 1]][0]
        tmp_salary = previous_year_salary * (1 + _salary_increase_rate)
        data[column_names[i]] = [tmp_salary]

    salary_dict = [_initial_salary * ((1 + _salary_increase_rate) ** i) for i in range(len(column_names))]
    _df.loc[_name] = salary_dict

    return _df


def add_compensation_payments(_df, _compensation_payment, _annual_payment, _investment_revenue_percent) -> pd.DataFrame:
    # calculation of payments
    payments = []
    compensation_account_balance = []
    remaining_balance = _compensation_payment
    for year in column_names:
        if year == column_names[-1]:
            payments.append(remaining_balance)
            remaining_balance = 0
        else:
            if remaining_balance >= _annual_payment:
                payments.append(_annual_payment)
                remaining_balance -= _annual_payment
            else:
                payments.append(remaining_balance)
                remaining_balance = 0
        # add the investment revenue after each year.
        remaining_balance = remaining_balance * (1 + _investment_revenue_percent)
        compensation_account_balance.append(remaining_balance)

    # Add new row to DataFrame
    _df.loc[ANNUAL_COMPENSATION] = payments

    # add new row for new job + compensation
    _df.loc[TOTAL_NEW_JOB] = np.add(_df.loc[NEW_JOB], _df.loc[ANNUAL_COMPENSATION])

    # add new row for the remaining height of your compensation balance
    _df.loc[COMPENSATION_ACCOUNT_BALANCE] = compensation_account_balance

    return _df


def add_calculations_differences_in_the_next_years(_df):
    if compensation_paid == 0:
        _df.loc[DIFFERENCE_NJ_CJ] = _df.loc[NEW_JOB] - _df.loc[CURRENT_JOB]
    else:
        _df.loc[DIFFERENCE_NJ_CJ_COMP] = _df.loc[NEW_JOB] + _df.loc[ANNUAL_COMPENSATION] - _df.loc[CURRENT_JOB]
    return _df


column_names = [float(i) for i in range(1, years + 1)]
df = pd.DataFrame(columns=column_names)
df.index.name = TYPE_OF_INCOME
df = add_calculations_salary_in_the_next_years(df, CURRENT_JOB, current_job_salary, salary_increase_percent)
df = add_calculations_salary_in_the_next_years(df, NEW_JOB, new_job_salary, salary_increase_percent)
if compensation_paid:
    df = add_compensation_payments(df, compensation_payment, compensation_annual_rate, investment_revenue_percent)
df = add_calculations_differences_in_the_next_years(df)

df.columns = df.columns.astype(float)
df = df.sort_index(axis=1)

# metrics
# def calculate_final_salary(start_salary, increase, years):
#    final_salary = start_salary * (1 + increase) ** (
#            years - 1)  # years-1 because the first increase is after the first year.
#    return final_salary
current_job_salary_final = df.loc[CURRENT_JOB].iloc[-1]
new_job_salary_final = df.loc[NEW_JOB].iloc[-1]
if compensation_paid:
    compensation_payment_incl_revenue = df.loc[ANNUAL_COMPENSATION].sum()
else:
    compensation_payment_incl_revenue = 0.0

def overall_sum_4_job(df, job_name, column_names) -> float:
    sum = np.sum(df.loc[job_name, column_names].values)
    return sum


st.header("Key metrics")
col_1_1, col_1_2, col_1_3, col_1_4, col_1_5, col_1_6 = st.columns(6)
help_salary_new_job_initial = ("Your starting salary of the new job. The plus/minus trend is the comparison to "
                               "your current's job salary per year (per month).")
col_1_1.metric(f"Starting salary new job",
               value=f"{new_job_salary} k€",
               delta=f"{new_job_salary - current_job_salary:.2f} k€ ({(new_job_salary - current_job_salary)/12:.2f} k€)",
               help=help_salary_new_job_initial)

if salary_increase_percent > 0.0:
    salary_difference_year = new_job_salary_final - current_job_salary_final
    salary_difference_month = salary_difference_year / 12
    help_salary_new_job_final = (f"This is the salary of the new job when you retire in {years} years: ({new_job_salary_final:.2f} k€). "
                                 f"This takes into account your 'Expected annual salary increase rate (%)' of "
                                 f"{salary_increase_input}%. The plus/minus trend compares this to the current salary"
                                 f" in {years} years: {(current_job_salary_final):.2f} k€), shown as difference "
                                 f"k€/year (k€/month).")
    col_1_2.metric(f"Salary new job in {years} years",
                   value=f"{new_job_salary_final:.2f} k€",
                   delta=f"{(salary_difference_year):.2f} k€ ({salary_difference_month:.2f} k€)",
                   help=help_salary_new_job_final
                   )

current_job_overall_salary = overall_sum_4_job(df, CURRENT_JOB, column_names)
help_overall_sum_current = "The cumulative sum of your current job's salary until your retirement."
col_1_3.metric("Overall sum current job",
               value=f"{current_job_overall_salary:.2f} k€",
               help=help_overall_sum_current)

help_overall_sum_new = ("The cumulative sum of your new job's salary until your retirement. Does not include the "
                        "compensation payment.")
new_job_overall_salary = overall_sum_4_job(df, NEW_JOB, column_names)
col_1_4.metric("Overall sum new job",
               value=f"{new_job_overall_salary:.2f} k€",
               help=help_overall_sum_new
               )

help_compenstation = ("Amount of your compensation payment, if received. This includes your expected annual revenue "
                      "when investing the compensation payment e.g in stocks. The trend value is the amount of "
                      "revenue from the investment.")
col_1_5.metric("Compensation incl. revenue",
               value=f"{compensation_payment_incl_revenue:.2f} k€",
               delta=f"{compensation_payment_incl_revenue - compensation_payment:.2f} k€",
               help=help_compenstation
               )

overall_delta = new_job_overall_salary + compensation_payment_incl_revenue - current_job_overall_salary
help_overall_delta = (f"The is the cumulative income for the next {years} years, including the compensation payment of "
                      f"{compensation_payment_incl_revenue} k€ including investment revenues. New job+compensation "
                      f"payment+investment revenues vs. current job.")
col_1_6.metric("Overall delta",
               value=f"{overall_delta:.2f} k€",
               delta=f"{overall_delta:.2f} k€",
               help=help_overall_delta)

col_3_1, col_3_2, col_3_3, col_3_4 = st.columns([3, 1, 1, 1])
col_3_1.header("Future development of your income")

with col_3_2:
    data_type = st.radio(
        "View",
        ["Yearly", "Overall sum"],
        label_visibility="collapsed"
    )

with col_3_3:
    chart_type = st.radio(
        "Chart type",
        ["Bar charts", "Line charts"],
        label_visibility="collapsed",
    )


def plot_bar_chart(_df):
    if compensation_paid == 0:
        title = "Comparison of current salary and new salary"
    else:
        title = "Comparison of current salary and new salary with compensation payment"
    if data_type == "Overall sum":
        title = title + " (cumulative overall sum)"

    # convert df into "longer" format, because it is easier for plotly
    df_long = _df.reset_index().melt(id_vars=TYPE_OF_INCOME, var_name='Year', value_name='Income')
    fig = px.bar(df_long,
                 x='Year',
                 y='Income',
                 barmode='group',
                 hover_data={TYPE_OF_INCOME: True, 'Income': True, 'Year': True},
                 title=title,
                 color=TYPE_OF_INCOME,
                 color_discrete_map=color_discrete_map
                 )

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
        yaxis_title="Income (k€)",
        title_font=dict(size=14, family="Arial", weight="normal"),
        title_x=0.0,
        title_y=0.85
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_line_chart(_df_cumsum):
    if compensation_paid == 0:
        title = "Comparison of current salary and new salary"
    else:
        title = "Comparison of current salary and new salary with compensation payment"
    if data_type == "Overall sum":
        title = title + " (cumulative overall sum)"

    # convert df into "longer" format, because it is easier for plotly
    df_long = _df_cumsum.reset_index().melt(id_vars=TYPE_OF_INCOME, var_name='Year', value_name='Income')
    fig = px.line(df_long,
                  x='Year',
                  y='Income',
                  hover_data={TYPE_OF_INCOME: True, 'Income': True, 'Year': False},
                  color=TYPE_OF_INCOME,
                  title=title,
                  color_discrete_map=color_discrete_map,
                  markers=True)

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
        title_font=dict(size=14, family="Arial", weight="normal"),
        title_x=0.0,
        title_y=0.85,
        yaxis=dict(range=[0, df_long['Income'].max() * 1.1]),  # Y-axis start with '0'
        yaxis_title="Income (k€)"
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_difference_bar_chart(_df_diff):
    if compensation_paid == 0:
        # -> difference between CURRENT_JOB, NEW_JOB
        title = f"Difference between {CURRENT_JOB} and {NEW_JOB}"
    else:
        # -> difference between CURRENT_JOB, TOTAL_NEW_JOB
        title = f"Difference between '{CURRENT_JOB}' and '{TOTAL_NEW_JOB}'"
    if data_type == "Overall sum":
        title = title + " (cumulative overall sum)"

    df_diff_t = _df_diff.T
    df_diff_t = df_diff_t.reset_index()
    df_diff_t.columns = ['Year', 'Difference']
    # add colors: negative is red, positive is green
    df_diff_t['Color'] = df_diff_t['Difference'].apply(lambda x: 'red' if x < 0 else 'green')
    fig = px.bar(df_diff_t,
                 x='Year',
                 y='Difference',
                 hover_data={'Difference': True, 'Year': True, "Color": False},
                 title=title,
                 color='Color',
                 color_discrete_map={'red': COLOR_NEGATIVE, 'green': COLOR_POSITIVE})

    # set y axis to always display the "0"-line
    y_min = min(df_diff_t['Difference'].min(), -5.0)
    y_max = max(df_diff_t['Difference'].max(), 5.0)
    fig.update_layout(yaxis=dict(range=[y_min, y_max * 1.1]),
                      yaxis_title="Difference (k€)",
                      showlegend=False,
                      height=350,
                      title_font=dict(size=14, family="Arial", weight="normal"),
                      title_x=0.0,
                      title_y=0.85
                      )

    st.plotly_chart(fig, use_container_width=True)


def plot_difference_line_char(_df_diff):
    if compensation_paid == 0:
        # -> difference between CURRENT_JOB, NEW_JOB
        title = f"Difference between '{CURRENT_JOB}' and '{NEW_JOB}'"
    else:
        # -> difference between CURRENT_JOB, TOTAL_NEW_JOB
        title = f"Difference between '{CURRENT_JOB}' and '{TOTAL_NEW_JOB}'"

    if data_type == "Overall sum":
        title = title + " (cumulative overall sum)"

    df_diff_t = _df_diff.T
    df_diff_t = df_diff_t.reset_index()
    df_diff_t.columns = ['Year', 'Difference']
    fig = px.line(df_diff_t, x='Year', y='Difference', title=title, markers=True, )

    fig.update_traces(line=dict(color=COLOR_DIFFERENCE))

    # set y axis to always display the "0"-line
    y_min = min(df_diff_t['Difference'].min(), -5.0)
    y_max = max(df_diff_t['Difference'].max(), 5.0)
    fig.update_layout(yaxis=dict(range=[y_min, y_max * 1.1]),
                      yaxis_title="Income (k€)",
                      showlegend=False,
                      height=350,
                      title_font=dict(size=14, family="Arial", weight="normal"),
                      title_x=0.0,
                      title_y=0.85
                      )

    st.plotly_chart(fig, use_container_width=True)


# generate the dataframes for the different chart types (comparison/difference) and view modes (Yearly/Overall sum)
if compensation_paid == 0:
    df_4_comparison = df.loc[[CURRENT_JOB, NEW_JOB]]
    df_4_difference = df.loc[[DIFFERENCE_NJ_CJ]]
else:
    df_4_comparison = df.loc[[CURRENT_JOB, NEW_JOB, ANNUAL_COMPENSATION, TOTAL_NEW_JOB]]
    df_4_difference = df.loc[[DIFFERENCE_NJ_CJ_COMP]]

# plot comparison chart:
if data_type == "Yearly":
    if chart_type == "Line charts":  # yearly + line
        plot_line_chart(df_4_comparison)
    else:  # yearly + bar
        plot_bar_chart(df_4_comparison)

elif data_type == "Overall sum":
    # calculate the cumulative/overall sum for each year
    df_4_comparison_cumsum = df_4_comparison.cumsum(axis=1)
    df_4_comparison_cumsum = df_4_comparison_cumsum.rename(index={CURRENT_JOB: CURRENT_JOB_CUM_SUM,
                                                                  NEW_JOB: NEW_JOB_CUM_SUM,
                                                                  ANNUAL_COMPENSATION: ANNUAL_COMPENSATION_SUM,
                                                                  TOTAL_NEW_JOB: TOTAL_NEW_JOB_SUM
                                                                  })
    # append cumsum data to "main" df, because we want to print the df later
    df = pd.concat([df, df_4_comparison_cumsum])
    if chart_type == "Line charts":
        plot_line_chart(df_4_comparison_cumsum)
    else:
        plot_bar_chart(df_4_comparison_cumsum)

# plot difference chart:
if data_type == "Yearly":
    if chart_type == "Line charts":  # yearly + line
        plot_difference_line_char(df_4_difference)
    else:  # yearly + bar
        plot_difference_bar_chart(df_4_difference)

elif data_type == "Overall sum":
    df_4_difference_cumsum = df_4_difference.cumsum(axis=1)
    df_4_difference_cumsum = df_4_difference_cumsum.rename(index={DIFFERENCE_NJ_CJ: DIFFERENCE_NJ_CJ_SUM,
                                                                  DIFFERENCE_NJ_CJ_COMP: DIFFERENCE_NJ_CJ_COMP_SUM,
                                                                  })
    # append cumsum data to "main" df, because we want to print the df later
    df = pd.concat([df, df_4_difference_cumsum])

    if chart_type == "Line charts":
        plot_difference_line_char(df_4_difference_cumsum)
    else:
        plot_difference_bar_chart(df_4_difference_cumsum)

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
# column_config[df.index.name] = st.column_config.TextColumn(width=500)

st.dataframe(df, column_config=column_config, use_container_width=True)

st.text(" ")
st.text(" ")
st.text(" ")

st.write("""Note: I have deliberately not taken gross-net salary into account here, as this is highly individual. You 
may enter your your gross or net salary, but you should than stick to one type - don't  mix it up. The inflation rate 
is also not taken into account.""")

st.write("💡", """Start with your gross salary to get a quick overview. If you want a better result, go to an <a 
href='https://www.lexware.de/werkzeuge-ebooks/brutto-netto-rechner/' id='gross-net-link'>online gross-net 
calculator</a> to calculate your real net salary and your <a 
href='https://www.lexware.de/werkzeuge-ebooks/abfindungsrechner/' id='gross-net-link'> net compensation payment</a>.""",
         unsafe_allow_html=True)
