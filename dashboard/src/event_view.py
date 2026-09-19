import streamlit as st

def render_event_panel(data):
    events = data.get("events", [])
    if not events:
        st.info("No active events.")
        return
        
    for e in events:
        if e.get("type") == "ACCIDENT":
            st.error(f"⚠ **ACCIDENT** | {e.get('event')} | Status: {e.get('status')}")
        elif e.get("type") == "ROAD_CLOSURE":
            st.error(f"⛔ **ROAD CLOSURE** | {e.get('event')} | Status: {e.get('status')}")
        else:
            st.warning(f"🚗 **CONGESTION** | {e.get('event')} | Status: {e.get('status')}")

def render_impact_analysis(data):
    events = data.get("events", [])
    for e in events:
        if "impact" in e:
            st.markdown("##### 💥 Impact Radius Analysis")
            st.write(f"**Direct Impact:** {', '.join(e['impact']['direct'])}")
            st.write(f"**Secondary Impact:** {', '.join(e['impact']['secondary'])}")
