import streamlit as st
import pandas as pd
import plotly.express as px

# Beispiel-Daten erstellen
data = {
    'type of income': ['Salary', 'Bonus', 'Investment', 'Other'],
    '2024': [50000, 10000, 15000, 5000],
    '2025': [52000, 11000, 16000, 6000],
    '2026': [54000, 12000, 60000, 7000],
    '2027': [56000, 13000, 70000, 8000],
    '2028': [58000, 14000, 19000, 9000]
}

df = pd.DataFrame(data)
df = df.set_index('type of income')

# DataFrame in ein langes Format umwandeln
df_long = df.reset_index().melt(id_vars='type of income', var_name='Year', value_name='Income')

# Radioboxen hinzufügen
view_type = st.radio("Wähle die Ansicht:", ('Yearly', 'Difference'))

if view_type == 'Yearly':
    # Yearly Balkendiagramm
    fig = px.bar(df_long, x='Year', y='Income', color='type of income', barmode='group')
else:
    # Differenz zwischen Salary und Investment berechnen
    df_diff = df.loc[['Investment', 'Salary']].diff().iloc[1].reset_index()
    df_diff.columns = ['Year', 'Difference']
    #df_diff['Difference'] = df.loc['Salary'] - df.loc['Investment']

    # Differenz-Balkendiagramm
    fig = px.bar(df_diff, x='Year', y='Difference', title='Difference between Salary and Investment')

    # Y-Achse anpassen, um negative Werte anzuzeigen
    y_min = df_diff['Difference'].min()
    y_max = df_diff['Difference'].max()
    fig.update_layout(yaxis=dict(range=[y_min, y_max * 1.1]))

# Layout anpassen, um die Legende unter das Diagramm zu setzen und den Titel zu entfernen
#fig.update_layout(
#    legend=dict(
#        orientation="h",
#        yanchor="bottom",
#        y=-0.3,
#        xanchor="center",
#        x=0.5
#    ),
#    legend_title=None,
#    # yaxis=dict(range=[0, df_long['Income'].max() * 1.1])  # Y-Achse bei 0 beginnen lassen
#)

# Diagramm in Streamlit anzeigen
st.plotly_chart(fig, use_container_width=True)
