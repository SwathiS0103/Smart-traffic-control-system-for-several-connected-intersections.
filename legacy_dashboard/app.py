import streamlit as st
import sys
import os

# Set up paths so we can import src modules
sys.path.insert(0, os.path.dirname(__file__))

from components.header import render_header
from components.sidebar import render_sidebar
from components.metric_cards import render_metrics
from src.map_view import render_map
from src.event_view import render_event_panel, render_impact_analysis
from src.emergency_view import render_emergency_panel, render_green_corridor
from src.signal_view import render_signals
from src.quantum_view import render_quantum_panel
from src.comparison_view import render_comparison
from src.environmental_view import render_environment
from src.scenario_view import render_scenario_controls
from src.integration_manager import IntegrationManager
from src.demo_mode import DemoManager

# Page config must be first
st.set_page_config(
    page_title="Q-FLOW Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session():
    if "integration_manager" not in st.session_state:
        st.session_state.integration_manager = IntegrationManager()
    if "demo_manager" not in st.session_state:
        st.session_state.demo_manager = DemoManager()
    if "current_scenario" not in st.session_state:
        st.session_state.current_scenario = "Normal Traffic"
    if "running" not in st.session_state:
        st.session_state.running = False
    if "current_step" not in st.session_state:
        st.session_state.current_step = 0
    if "traffic_state" not in st.session_state:
        st.session_state.traffic_state = None

def main():
    init_session()
    
    # Render Sidebar and Header
    scenario, optimization_mode, actions = render_sidebar()
    st.session_state.current_scenario = scenario
    
    # Process actions (like "Start Simulation" etc.)
    if actions.get("reset"):
        st.session_state.current_step = 0
        st.session_state.running = False
    if actions.get("start"):
        st.session_state.running = True
    if actions.get("pause"):
        st.session_state.running = False
        
    # Fetch Data (Demo or Live)
    im = st.session_state.integration_manager
    dm = st.session_state.demo_manager
    
    # If integration is purely demo for now
    data = dm.get_state_for_scenario(st.session_state.current_scenario, st.session_state.current_step)
    
    render_header(data)
    
    if data:
        st.divider()
        render_metrics(data)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Live Traffic Map")
            render_map(data)
            
            st.subheader("Event Timeline & Impact")
            render_event_panel(data)
            render_impact_analysis(data)
            
            st.subheader("Emergency Operations")
            render_emergency_panel(data)
            render_green_corridor(data)
            
        with col2:
            st.subheader("Quantum Optimization")
            render_quantum_panel(data)
            
            st.subheader("Signal Status")
            render_signals(data)
            
        st.divider()
        st.subheader("Performance Comparison (Classical vs QAOA)")
        render_comparison(data)
        
        st.divider()
        st.subheader("Environmental Impact")
        render_environment(data)
        
        # Advance simulation step if running
        if st.session_state.running:
            st.session_state.current_step += 1

if __name__ == "__main__":
    main()
