import requests
import pandas as pd
import streamlit as st
import plotly.express as px

ERGAST_API = "https://ergast.com/api/f1"

def get_race_data(year, round):
    response = requests.get(f"{ERGAST_API}/{year}/{round}/results.json")
    data = response.json()["MRData"]["RaceTable"]["Races"]
    if data:
        race = data[0]
        results = race["Results"]
        df = pd.DataFrame(results)
        df["year"] = year
        df["round"] = round
        df["circuit_name"] = race["Circuit"]["circuitName"]
        df["position"] = df["position"].astype(int)
        df["points"] = df["points"].astype(float)
        df["laps"] = df["laps"].astype(int)
        df["grid"] = df["grid"].astype(int)
        return df
    else:
        return None

st.title("F1 Race Analysis")

year = st.sidebar.selectbox("Select Year", range(2000, 2022))
round = st.sidebar.selectbox("Select Round", range(1, 22))

df = get_race_data(year, round)

if df is not None:
    st.header(f"{df['circuit_name'][0]} - {year}")

    fig = px.scatter(df, x="position", y="Driver", hover_data=["laps", "Time"], title="Final Positions")
    st.plotly_chart(fig)

    fig = px.bar(df, x="Driver", y="points", hover_data=["laps", "Time"], title="Driver Rankings")
    st.plotly_chart(fig)

    # Technical analysis of the fastest lap during the qualifying
    response = requests.get(f"{ERGAST_API}/{year}/{round}/qualifying.json")
    data = response.json()["MRData"]["RaceTable"]["Races"]
    if data:
        qualifying = data[0]["QualifyingResults"]
        df_qual = pd.DataFrame(qualifying)
        df_qual["fastest_lap_rank"] = df_qual["Q1"].rank(method="min").astype(int)
        df_qual["year"] = year
        df_qual["round"] = round
        df_qual["circuit_name"] = data[0]["Circuit"]["circuitName"]

        fig = px.histogram(df_qual, x="Driver", y="fastest_lap_rank", hover_data=["Q1"], title="Fastest Lap Analysis")
        st.plotly_chart(fig)
    else:
        st.write("No qualifying data available")

else:
    st.write("No data available for the selected year and round.")
