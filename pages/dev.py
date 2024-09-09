import pandas as pd
import plotly.graph_objs as go
import streamlit as st

df = pd.DataFrame(
    dict(
        year=[2000, 2010, 2020],
        var1=[10, 20, 15],
        var2=[12, 8, 18],
        var3=[10, 17, 13],
        var4=[12, 11, 20],
    )
)

fig = go.Figure()

fig.update_layout(
    template="simple_white",
    xaxis=dict(title_text="Year"),
    yaxis=dict(title_text="Count"),
    barmode="stack",
)

groups = ['var1', 'var2', 'var3', 'var4']
colors = ["blue", "red", "green", "purple"]
names = ['spent on fruit', 'spent on toys', 'earned from stocks', 'earned from gambling']

i = 0
for r, n, c in zip(groups, names, colors):
    ## put var1 and var2 together on the first subgrouped bar
    if i <= 1:
        fig.add_trace(
            go.Bar(x=[df.year, ['subgroup1'] * len(df.year)], y=df[r], name=n, marker_color=c),
        )
    ## put var3 and var4 together on the first subgrouped bar
    else:
        fig.add_trace(
            go.Bar(x=[df.year, ['subgroup2'] * len(df.year)], y=df[r], name=n, marker_color=c),
        )
    i += 1

st.plotly_chart(fig, use_container_width=True)