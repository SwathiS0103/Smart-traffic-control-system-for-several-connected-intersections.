import streamlit as st
import pandas as pd
import plotly.express as px

def render_environment(data):
    perf = data.get("performance_comparison", {})
    if not perf:
        return
        
    df = pd.DataFrame.from_dict(perf, orient='index').reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(df, values='fuel', names='index', title='Fuel Consumption Comparison (L/hr)')
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        fig = px.pie(df, values='co2', names='index', title='CO2 Emissions Comparison (kg/hr)')
        st.plotly_chart(fig, use_container_width=True)
