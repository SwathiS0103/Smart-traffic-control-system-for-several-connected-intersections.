import streamlit as st
import pandas as pd

def render_signals(data):
    st.markdown("Compare current signal state against QAOA and Classical plans.")
    
    comparisons = data.get("signal_comparison", {})
    if not comparisons:
        st.write("No signal data available.")
        return
        
    df = pd.DataFrame.from_dict(comparisons, orient='index')
    st.dataframe(df, use_container_width=True)
