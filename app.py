import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import yaml
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ======================
# File to store locations
# ======================
DATA_FILE = "locations.yaml"

def load_locations():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

def save_locations(data):
    with open(DATA_FILE, "w") as f:
        yaml.dump(data, f)

# ======================
# Page setup
# ======================
st.set_page_config(page_title="📍 Multi-Phone Tracker", layout="wide")
st.title("📍 Real-Time Multi-Phone Tracker")

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="tracker_refresh")

# ======================
# User setup
# ======================
username = st.text_input("Enter your name/ID", key="user_input")

# JavaScript for GPS
get_location_js = """
<script>
function sendLocation() {
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const url = new URL(window.location.href);
            url.searchParams.set("lat", lat);
            url.searchParams.set("lon", lon);
            window.location.href = url;  // reload with coords
        },
        function(error) {
            alert("Error: " + error.message);
        }
    );
}
</script>
<button onclick="sendLocation()">Share My Location</button>
"""

# Inject JS
components.html(get_location_js, height=100)

# ======================
# Save location if provided
# ======================
params = st.query_params
lat = params.get("lat", [None])[0]
lon = params.get("lon", [None])[0]

if lat and lon and username:
    lat, lon = float(lat), float(lon)
    data = load_locations()
    data[username] = {
        "lat": lat,
        "lon": lon,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_locations(data)
    st.success(f"✅ Location updated for {username}")

# ======================
# Show all phones on map
# ======================
data = load_locations()
if data:
    st.subheader("🌍 Live Map of All Phones")
    df = pd.DataFrame(data).T.reset_index().rename(columns={"index": "user"})
    st.map(df[["lat", "lon"]])

    st.subheader("📋 User Details")
    st.dataframe(df)
else:
    st.info("No locations yet. Ask users to share their location.")
