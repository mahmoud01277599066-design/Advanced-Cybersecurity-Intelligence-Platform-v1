import streamlit as st
import pandas as pd
import os
import sys
import time

# Ensure project root is in path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.database import get_recent_incidents

# Configure Page
st.set_page_config(
    page_title="ACIP - Professional SOC Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep Dark Theme Styles
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #3e4149;
    }
</style>
""", unsafe_allow_html=True)

def run_dashboard():
    st.title("🛡️ ACIP Advanced SOC Visualization")
    st.subheader("Real-World Threat Intelligence & AI Analysis")
    
    # Refresh Logic
    refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 2, 20, 5)
    
    # Load Data
    data = get_recent_incidents(limit=100)
    df = pd.DataFrame(data)
    
    if df.empty:
        st.info("No incidents detected yet. Waiting for live events...")
        time.sleep(refresh_rate)
        st.rerun()
        return

    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Incidents", len(df))
    with col2:
        tp_count = len(df[df['classification'] == 'True Positive'])
        st.metric("True Positives", tp_count, delta=f"{tp_count/len(df)*100:.1f}%", delta_color="inverse")
    with col3:
        fp_count = len(df[df['classification'] == 'False Positive'])
        st.metric("False Positives", fp_count)
    with col4:
        high_severity = len(df[df['severity'].str.lower() == 'high'])
        st.metric("High Severity", high_severity)

    # Main Content Area
    st.divider()
    
    tab1, tab2 = st.tabs(["📊 Live Incident Stream", "🕵️ AI Deep Analysis"])
    
    with tab1:
        st.write("### Latest Security Events")
        # Color coding for severities
        def color_severity(val):
            color = "#ff4b4b" if val.lower() == 'high' else "#ffa500" if val.lower() == 'medium' else "#00ff00"
            return f'color: {color}'
        
        display_df = df[['timestamp', 'src_ip', 'severity', 'classification', 'description']]
        st.dataframe(display_df.style.applymap(color_severity, subset=['severity']), use_container_width=True)

    with tab2:
        st.write("### AI Reasoning & Decision Logs")
        for index, row in df.head(5).iterrows():
            with st.expander(f"Incident {row['id']} - From {row['src_ip']} ({row['timestamp']})"):
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.write("**Classification:**")
                    st.code(row['classification'])
                    st.write("**Confidence Score:**")
                    st.progress(row['confidence'])
                with c2:
                    st.write("**AI Reasoning:**")
                    st.info(row['reason'])
                    st.write("**Recommended Report:**")
                    if os.path.exists(row['report_path']):
                        st.markdown(f"[Download Full Report](file:///{row['report_path']})")

    # Auto-rerun
    time.sleep(refresh_rate)
    st.rerun()

if __name__ == "__main__":
    run_dashboard()
