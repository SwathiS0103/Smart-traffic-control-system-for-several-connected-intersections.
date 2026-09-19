import streamlit as st

def render_emergency_panel(data):
    emergencies = data.get("emergencies", [])
    if not emergencies:
        st.info("No active emergency vehicles.")
        return
        
    for e in emergencies:
        st.error(f"🚑 **EMERGENCY ACTIVE**: {e['vehicle_id']}")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Origin:** {e['origin']}")
            st.write(f"**Destination:** {e['destination']}")
        with col2:
            st.write(f"**Status:** {e['status']}")
            st.write(f"**ETA:** {e['eta']} sec")
            
        st.write(f"**Route:** {' → '.join(e['route'])}")

def render_green_corridor(data):
    emergencies = data.get("emergencies", [])
    for e in emergencies:
        if "corridor" in e:
            st.markdown("##### 🟢 Green Corridor Schedule")
            for stop in e["corridor"]:
                st.write(f"**{stop['junction']}** | ETA: {stop['eta']}s | Green: {stop['green_start']}s to {stop['green_end']}s")
