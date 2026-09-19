import streamlit as st
import folium
from streamlit_folium import st_folium

def render_map(data):
    # Center map roughly on the junctions
    m = folium.Map(location=[13.085, 80.275], zoom_start=15)
    
    # Draw edges
    for edge in data.get("edges", []):
        coords = edge["coords"]
        status = edge["status"]
        density = edge["density"]
        
        color = "green"
        if density > 0.6: color = "orange"
        if density > 0.8: color = "red"
        
        if status == "CLOSED":
            color = "black"
            folium.PolyLine(coords, color=color, weight=5, dash_array="5, 5").add_to(m)
        elif status == "ACCIDENT":
            color = "purple"
            folium.PolyLine(coords, color=color, weight=6).add_to(m)
        else:
            folium.PolyLine(coords, color=color, weight=5, opacity=0.8).add_to(m)
            
    # Draw junctions
    for j_id, j_data in data.get("junctions", {}).items():
        lat = j_data["lat"]
        lon = j_data["lon"]
        density = j_data["density"]
        
        color = "green"
        if density > 0.6: color = "orange"
        if density > 0.8: color = "red"
        
        tooltip = f"{j_id} | Q: {j_data['queue']} | Sig: {j_data['signal']}"
        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            popup=tooltip,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.9
        ).add_to(m)
        
    st_folium(m, height=400, use_container_width=True)
