import requests
import pandas as pd
import streamlit as st
import altair as alt

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
        df["full_name"] = df["Driver"].apply(lambda d: d["givenName"] + " " + d["familyName"])
        return df
    else:
        return None

st.title("F1 Race Analysis")

year = st.sidebar.selectbox("Select Year", range(2015, 2024))
round = st.sidebar.selectbox("Select Round", range(1, 22))

df = get_race_data(year, round)

if df is not None:
    st.header(f"{df['circuit_name'][0]} - {year}")

    final_positions_chart = alt.Chart(df).mark_circle(size=60).encode(
        x="position",
        #y="full_name",
        y=alt.Y("position", sort='x'),  # Updated line
        
        tooltip=["laps", "Time"],
        color=alt.Color("points", scale=alt.Scale(scheme="viridis"))
    ).properties(title="Final Positions")
    st.altair_chart(final_positions_chart, use_container_width=True)

    driver_rankings_chart = alt.Chart(df).mark_bar().encode(
        x="full_name",
        #y="points",
        y=alt.Y("points", sort='x'),  # Updated line
        
        tooltip=["laps", "Time"],
        color=alt.Color("points", scale=alt.Scale(scheme="viridis"))
    ).properties(title="Driver Rankings")
    st.altair_chart(driver_rankings_chart, use_container_width=True)

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
        df_qual["full_name"] = df_qual["Driver"].apply(lambda d: d["givenName"] + " " + d["familyName"])

        fastest_lap_chart = alt.Chart(df_qual).mark_bar().encode(
            x="full_name",
            #y="fastest_lap_rank",
            y=alt.Y("fastest_lap_rank", sort='x'),  # Updated line
            tooltip=["Q1"],
            color=alt.Color("fastest_lap_rank", scale=alt.Scale(scheme="viridis"))
        ).properties(title="Fastest Lap Analysis")
        st.altair_chart(fastest_lap_chart, use_container_width=True)
    else:
        st.write("No qualifying data available")

else:
    st.write("No data available for the selected year and round.")
