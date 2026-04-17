import os
from datetime import UTC, datetime, timedelta

import httpx
import plotly.graph_objects as go  # type: ignore[import-untyped]
import streamlit as st
from wordcloud import WordCloud  # type: ignore[import-untyped]

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

tab_weather, tab_hits = st.tabs(["Weather Query", "Weather Hits"])

with tab_weather:
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
                    source = data["source"]
                    source_label = "Data retrieved from cache." if source == "cache" else "Data retrieved from API."
                    st.info(source_label)
                elif response.status_code == 404:
                    st.error(response.json().get("detail", "City not found."))
                else:
                    st.error(f"Upstream error ({response.status_code}). Try again later.")
            except httpx.TimeoutException:
                st.error("Request timed out. Try again.")
            except httpx.RequestError:
                st.error("Could not reach the API. Is it running?")

with tab_hits:
    st.title("Weather Hits")

    now = datetime.now(UTC)
    payload = {
        "from": (now - timedelta(hours=24)).isoformat(),
        "to": now.isoformat(),
    }

    with st.spinner("Loading analytics..."):
        try:
            cloud_resp = httpx.post(f"{API_BASE_URL}/cities-cloud", json=payload, timeout=10)
            dots_resp = httpx.post(f"{API_BASE_URL}/cities-dots", json=payload, timeout=10)

            if cloud_resp.status_code == 200:
                cloud_data = cloud_resp.json()
                city_hits = {entry["city"]: entry["hits"] for entry in cloud_data["cities"]}

                if city_hits:
                    st.subheader("Cities cloud")
                    wc = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(city_hits)  # type: ignore[reportUnknownMemberType]
                    st.image(wc.to_array())  # type: ignore[reportUnknownMemberType]
                else:
                    st.info("No weather queries in the last 24h.")

            if dots_resp.status_code == 200:
                dots_data = dots_resp.json()["dots"]

                if dots_data:
                    st.subheader("Queries — last 24h")
                    cities_seen = sorted({d["city"] for d in dots_data})
                    color_map = {c: f"hsl({i * 360 // len(cities_seen)}, 70%, 50%)" for i, c in enumerate(cities_seen)}

                    fig = go.Figure()  # type: ignore[reportUnknownMemberType]
                    for city_name in cities_seen:
                        city_dots = [d for d in dots_data if d["city"] == city_name]
                        fig.add_trace(go.Scatter(  # type: ignore[reportUnknownMemberType]
                            x=[d["datetime"] for d in city_dots],
                            y=[city_name] * len(city_dots),
                            mode="markers",
                            marker={"size": 12, "color": color_map[city_name]},
                            name=city_name,
                            hovertemplate="%{x}<br>%{y}<extra></extra>",
                        ))

                    fig.update_layout(  # type: ignore[reportUnknownMemberType]
                        xaxis_title="Time",
                        yaxis_title="City",
                        showlegend=True,
                        height=400,
                    )
                    st.plotly_chart(fig, use_container_width=True)  # type: ignore[reportUnknownMemberType]

        except httpx.RequestError:
            st.error("Could not reach the API. Is it running?")
