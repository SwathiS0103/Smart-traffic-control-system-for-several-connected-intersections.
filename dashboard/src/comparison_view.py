import streamlit as st
import pandas as pd
import plotly.express as px

def render_comparison(data):
    perf = data.get("performance_comparison", {})
    if not perf:
        st.write("No comparison data available.")
        return
        
    df = pd.DataFrame.from_dict(perf, orient='index')
    
    st.markdown("### Classical vs Quantum (QAOA) Summary")
    st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(df.reset_index(), x='index', y='waiting', title="Average Waiting Time (sec)", color='index')
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        fig2 = px.bar(df.reset_index(), x='index', y='queue', title="Average Queue Length", color='index')
        st.plotly_chart(fig2, use_container_width=True)
