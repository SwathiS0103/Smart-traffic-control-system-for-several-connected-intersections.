import streamlit as st
import pandas as pd
import plotly.express as px

def render_quantum_panel(data):
    quantum = data.get("quantum", {})
    if not quantum:
        st.info("Quantum optimization data not available.")
        return
        
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Method:** {quantum.get('method')}")
        st.write(f"**Backend:** {quantum.get('backend')}")
        st.write(f"**QAOA Depth (p):** {quantum.get('depth')}")
        st.write(f"**Shots:** {quantum.get('shots')}")
    with col2:
        st.write(f"**Variables:** {quantum.get('variables')}")
        st.write(f"**Objective Value:** {quantum.get('objective_value')}")
        st.write(f"**Execution Time:** {quantum.get('execution_time')}")
        st.write(f"**Best Bitstring:** `{quantum.get('best_bitstring')}`")
        
    top_strings = quantum.get("top_strings", {})
    if top_strings:
        df = pd.DataFrame({
            "Bitstring": list(top_strings.keys()),
            "Probability": list(top_strings.values())
        })
        fig = px.bar(df, x="Probability", y="Bitstring", orientation='h', title="Top Measured States")
        st.plotly_chart(fig, use_container_width=True)
