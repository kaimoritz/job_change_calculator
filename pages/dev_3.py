import pandas as pd
import plotly.graph_objs as go
import streamlit as st

df = pd.DataFrame(
    dict(
        year=[2000, 2010, 2020],
        var1=[10, 20, 5],
        var2=[10, 20, 5],
        var3=[10, 20, 5],
    )
)
print(df)

data = {
    'Year 1': [50000, 60000, 10000],
    'Year 2': [50000, 60000, 10000],
    'Year 3': [50000, 60000, 10000],
    'Year 4': [50000, 60000, 10000],
    'Year 5': [50000, 60000, 10000]
}
df_c = pd.DataFrame(data, index=['salary old job', 'salary new job', 'severance payment'])
print(df_c)
print("\n")
print(df_c.T)

df_c_t = df_c.T

fig = go.Figure()

fig.update_layout(
    template="simple_white",
    xaxis=dict(title_text="Year"),
    yaxis=dict(title_text="Count"),
    barmode="stack",
)

groups = ['var1', 'var2', 'var3', ]
colors = ["blue", "red", "green", ]
names = ['Current job salary', 'Annual severance payment', 'New job']

i = 0
for r, n, c in zip(groups, names, colors):
    ## put var1 and var2 together on the first subgrouped bar
    if i <= 1:
        fig.add_trace(
            go.Bar(x=[df.year, ['New job'] * len(df.year)], y=df[r], name=n, marker_color=c),
        )
    ## put var3 and var4 together on the first subgrouped bar
    else:
        fig.add_trace(
            go.Bar(x=[df.year, ['Current job'] * len(df.year)], y=df[r], name=n, marker_color=c),
        )
    i += 1

st.plotly_chart(fig, use_container_width=True)