# src/ui/dashboard.py
import streamlit as st
import requests
import pandas as pd

# Configure page
st.set_page_config(page_title="Passive Analyzer Dashboard", layout="wide")

st.title("🛡️ Passive Traffic Analyzer")
st.markdown("### Real-time Session Metadata & Triage")

# Fetch data from our local FastAPI backend
API_URL = "http://localhost:8000"

try:
    response = requests.get(f"{API_URL}/api/sessions/recent")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data["sessions"])
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Failed to fetch data from API")
except Exception as e:
    st.warning(f"API is currently unreachable: {e}")

st.markdown("---")
st.caption("P0 Status: Ingress Active | Session Correlator: Pending | AI Detection: Pending")