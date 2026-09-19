import streamlit as st

def render_sidebar():
    st.sidebar.title("Controls")
    
    st.sidebar.subheader("Scenario")
    scenario = st.sidebar.selectbox(
        "Select Traffic Scenario",
        [
            "Normal Traffic", 
            "Heavy Traffic", 
            "Congestion", 
            "Accident", 
            "Road Closure", 
            "Emergency", 
            "Emergency + Congestion", 
            "Emergency + Road Closure", 
            "Multiple Events"
        ],
        index=0
    )
    
    st.sidebar.subheader("Simulation")
    col1, col2 = st.sidebar.columns(2)
    start_btn = col1.button("Start")
    pause_btn = col2.button("Pause")
    reset_btn = st.sidebar.button("Reset Simulation", use_container_width=True)
    
    st.sidebar.subheader("Optimization")
    optimization_mode = st.sidebar.radio(
        "Optimization Mode",
        ["Fixed", "Classical Adaptive", "QAOA"]
    )
    st.sidebar.button("Optimize Traffic", use_container_width=True, type="primary")
    
    st.sidebar.subheader("Inject Events")
    st.sidebar.button("🚑 Add Ambulance", use_container_width=True)
    st.sidebar.button("⚠ Trigger Accident", use_container_width=True)
    st.sidebar.button("⛔ Close Road", use_container_width=True)
    st.sidebar.button("🚗 Create Congestion", use_container_width=True)
    
    actions = {
        "start": start_btn,
        "pause": pause_btn,
        "reset": reset_btn
    }
    
    return scenario, optimization_mode, actions
