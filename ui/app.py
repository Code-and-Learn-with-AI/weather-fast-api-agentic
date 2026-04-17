import os

import httpx
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.title("Weather Query")

city = st.text_input("Enter a city name")

if st.button("Get Weather") and city.strip():
    with st.spinner("Fetching..."):
        try:
            response = httpx.get(f"{API_BASE_URL}/weather", params={"city": city}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                st.success(f"**{data['city']}, {data['country']}**")
                col1, col2, col3 = st.columns(3)
                col1.metric("Temperature", f"{data['temperature']}°C")
                col2.metric("Feels like", f"{data['feels_like']}°C")
                col3.metric("Humidity", f"{data['humidity']}%")
                st.caption(data["description"].capitalize())
                source_label = "Data retrieved from cache." if data["source"] == "cache" else "Data retrieved from API."
                st.info(source_label)
            elif response.status_code == 404:
                st.error(response.json().get("detail", "City not found."))
            else:
                st.error(f"Upstream error ({response.status_code}). Try again later.")
        except httpx.TimeoutException:
            st.error("Request timed out. Try again.")
        except httpx.RequestError:
            st.error("Could not reach the API. Is it running?")
