import streamlit as st
import pandas as pd
import plotly.express as px

# Beispiel-Daten erstellen
data = {
    'type of income': ['Salary', 'Bonus', 'Investment', 'Other'],
    '2024': [50000, 10000, 15000, 5000],
    '2025': [52000, 11000, 16000, 6000],
    '2026': [54000, 12000, 57000, 7000],
    '2027': [56000, 13000, 68000, 8000],
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
    # Radiobutton für Diagrammtyp im Differenzmodus
    diff_chart_type = st.radio("Wähle den Diagrammtyp:", ('Bar Chart', 'Line Chart'))

    # Differenz zwischen Salary und Investment berechnen
    df_diff = df.loc[['Salary', 'Investment']].diff().iloc[1].reset_index()
    df_diff.columns = ['Year', 'Difference']
    #df_diff['Difference'] = df.loc['Salary'] - df.loc['Investment']

    if diff_chart_type == 'Bar Chart':
        # Differenz-Balkendiagramm mit Farbänderung für negative Werte
        df_diff['Color'] = df_diff['Difference'].apply(lambda x: 'red' if x < 0 else 'blue')
        fig = px.bar(df_diff, x='Year', y='Difference', title='Difference between Salary and Investment', color='Color', color_discrete_map={'red': 'red', 'blue': 'blue'})
    else:
        # Differenz-Liniendiagramm
        fig = px.line(df_diff, x='Year', y='Difference', title='Difference between Salary and Investment', markers=True)

    # Y-Achse anpassen, um negative Werte anzuzeigen
    y_min = df_diff['Difference'].min()
    y_max = df_diff['Difference'].max()
    fig.update_layout(yaxis=dict(range=[y_min, y_max * 1.1]))

# Layout anpassen, um die Legende unter das Diagramm zu setzen und den Titel zu entfernen
fig.update_layout(
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,
        xanchor="center",
        x=0.5
    ),
    legend_title=None
)

# Diagramm in Streamlit anzeigen
st.plotly_chart(fig, use_container_width=True)
