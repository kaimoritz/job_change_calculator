import streamlit as st
import pandas as pd
import altair as alt

# Beispiel-Daten
data = {
    'Wert': [10, 20, 30]
}

# DataFrame erstellen und benutzerdefinierten Index setzen
df = pd.DataFrame(data, index=['B', 'A', 'C'])

# Gewünschte Reihenfolge des Index festlegen
index_reihenfolge = ['C', 'B', 'A']
df = df.reindex(index_reihenfolge)

# DataFrame für Altair vorbereiten
df_reset = df.reset_index().rename(columns={'index': 'Kategorie'})

# Bar Chart mit Altair erstellen
chart = alt.Chart(df_reset).mark_bar().encode(
    x=alt.X('Kategorie', sort=index_reihenfolge),
    y='Wert'
)

# Chart in Streamlit anzeigen
st.altair_chart(chart, use_container_width=True)
