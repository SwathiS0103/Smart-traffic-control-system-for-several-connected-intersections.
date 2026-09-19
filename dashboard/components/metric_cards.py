import streamlit as st

def render_metrics(data):
    metrics = data.get("metrics", {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Average Waiting Time", value=f"{metrics.get('waiting_time', 0.0)} sec")
        st.metric(label="Fuel Consumption", value=f"{metrics.get('fuel', 0.0)} L/hr")
        
    with col2:
        st.metric(label="Average Queue Length", value=f"{metrics.get('queue_length', 0)} veh")
        st.metric(label="CO2 Emissions", value=f"{metrics.get('co2', 0.0)} kg/hr")
        
    with col3:
        st.metric(label="Traffic Throughput", value=f"{metrics.get('throughput', 0)} veh/hr")
        st.metric(label="Emergency Travel Time", value=f"{metrics.get('emergency_time', 0)} sec")
        
    with col4:
        st.metric(label="Average Speed", value=f"{metrics.get('speed', 0.0)} km/h")
        active_events = len(data.get("events", []))
        st.metric(label="Active Events", value=f"{active_events}")
