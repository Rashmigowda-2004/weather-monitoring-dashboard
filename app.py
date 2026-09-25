import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Weather Dashboard", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0e1117; color: white; }
div[data-testid="metric"] { background-color: #1e2130; padding: 15px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🌦️ Pro Weather Monitoring Dashboard")

city = st.text_input("Enter city name", "Bangalore")

if st.button("Get Weather"):
    try:
        # Geocoding with headers
        headers = {"User-Agent": "Mozilla/5.0"}
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=5&language=en&format=json"
        geo = requests.get(geo_url, headers=headers, timeout=10).json()

        if "results" not in geo or len(geo["results"])==0:
            st.error(f"City '{city}' not found. Try 'Delhi', 'London'")
            st.write(geo) # debug
        else:
            results = geo["results"]
            best = next((r for r in results if r.get('country') == 'India'), results[0])
            lat = best["latitude"]
            lon = best["longitude"]
            st.success(f"Found: {best['name']}, {best.get('country','')}")

            w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m&hourly=temperature_2m&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
            w = requests.get(w_url, headers=headers, timeout=10).json()

            curr = w["current"]
            col1, col2, col3 = st.columns(3)
            col1.metric("🌡️ Temperature", f"{curr['temperature_2m']}°C")
            col2.metric("💧 Humidity", f"{curr['relative_humidity_2m']}%")
            col3.metric("💨 Wind", f"{curr['wind_speed_10m']} km/h")

            st.subheader("24-Hour Temperature Trend")
            df_h = pd.DataFrame({"Temp": w["hourly"]["temperature_2m"][:24]})
            st.line_chart(df_h)

            st.subheader("7-Day Forecast")
            df_d = pd.DataFrame({
                "Max": w["daily"]["temperature_2m_max"],
                "Min": w["daily"]["temperature_2m_min"]
            })
            st.bar_chart(df_d)

            st.subheader("📍 Location Map")
            st.map(pd.DataFrame({"lat":[lat], "lon":[lon]}))
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Check your internet connection")