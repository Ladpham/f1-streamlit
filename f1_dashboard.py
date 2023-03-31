import requests
import streamlit as st
import pandas as pd
import plotly.express as px

def get_f1_data(season, round, endpoint):
    base_url = 'http://ergast.com/api/f1/'
    url = f'{base_url}{season}/{round}/{endpoint}.json'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def race_finishing_positions(data):
    results = data['MRData']['RaceTable']['Races'][0]['Results']
    df = pd.DataFrame(results)
    df['position'] = df['position'].astype(int)
    fig = px.bar(df, x='Driver', y='position', text='position', title='Race Finishing Positions')
    fig.update_traces(texttemplate='%{text}s', textposition='outside')
    return fig

def qualifying_performance(data):
    qualifying = data['MRData']['RaceTable']['Races'][0]['QualifyingResults']
    df = pd.DataFrame(qualifying)
    df['q1_time'] = pd.to_numeric(df['Q1'].str.extract(r'(\d+\.\d+)')[0])
    fig = px.line(df, x='Driver', y='q1_time', title='Qualifying Performance (Q1 times)')
    return fig

st.title("F1 Dashboard")

years = list(range(1950, 2023))
selected_year = st.sidebar.selectbox("Select Year", years, index=len(years) - 1)

rounds = list(range(1, 23))
selected_round = st.sidebar.selectbox("Select Round", rounds)

data = get_f1_data(selected_year, selected_round, "qualifying")
if data:
    st.plotly_chart(race_finishing_positions(data), use_container_width=True)
    st.plotly_chart(qualifying_performance(data), use_container_width=True)
else:
    st.error("Error fetching data")
