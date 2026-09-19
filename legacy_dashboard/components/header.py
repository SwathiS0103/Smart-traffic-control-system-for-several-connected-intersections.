import streamlit as st

def render_header(data):
    st.title("Q-FLOW: Quantum-Enhanced Adaptive Urban Traffic Optimization")
    
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.info("● Simulation Connected" if data.get("sumo_connected", True) else "○ Simulation Offline (DEMO)")
    with status_col2:
        st.success("● Quantum Optimizer Ready" if data.get("quantum_ready", True) else "○ Quantum Optimizer Offline")
    with status_col3:
        st.success("● Event Engine Ready" if data.get("event_ready", True) else "○ Event Engine Offline")
        
    st.markdown(f"**Current Time:** `{data.get('time', '00:00')}` | **Scenario:** `{st.session_state.get('current_scenario', 'Unknown')}`")
