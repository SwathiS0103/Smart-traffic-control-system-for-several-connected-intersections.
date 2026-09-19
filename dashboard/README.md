# Q-FLOW: Dashboard & Integration (Member 4)

This module provides the central visualization and integration layer for the Quantum-Enhanced Adaptive Urban Traffic Optimization system. It connects the Traffic Digital Twin (Member 1), Quantum Optimizer (Member 2), and Event Intelligence Engine (Member 3) into a cohesive interactive dashboard.

## 1. What Member 4 Does
- **Live Traffic Map:** Uses Folium to visualize traffic density, queues, closures, and accidents on the road network.
- **Event & Emergency Visualization:** Visually highlights active emergency corridors (green-wave) and accident impact radii.
- **Quantum Optimization Panel:** Displays QUBO parameters and QAOA bitstring probabilities, verifying the quantum component's execution.
- **Performance Comparisons:** Compares waiting time, throughput, fuel consumption, and CO2 emissions between Fixed, Classical, and QAOA methodologies.
- **Interactive Scenarios:** Allows judges to select distinct scenarios (e.g. Normal, Congestion, Accident, Ambulance Dispatch) and see the system react in real-time.
- **Demo Mode:** Runs flawlessly even if the SUMO or Quantum backend services are disconnected, generating realistic simulation-like outputs from sample data.

## 2. Architecture

```text
       ┌───────────────┐
       │   DASHBOARD   │
       │ (Streamlit UI)│
       └───────┬───────┘
               │
      ┌────────┴────────┐
      │Integration Layer│
      └─┬──────┬──────┬─┘
        │      │      │
    SUMO│ QUBO │ EVENT│
   M1   │  M2  │   M3 │
```

## 3. How to Run

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Launch the Dashboard:**
```bash
streamlit run app.py
```

**Run Tests:**
```bash
pytest tests/
```

## 4. Integration Instructions

- **Member 1 (SUMO):** The dashboard expects traffic density and queue lengths provided in the mock schema (see `data/sample_traffic_state.json`). It will poll the `get_traffic_state()` method when live.
- **Member 2 (Quantum):** The dashboard visualizes `objective_value`, `best_bitstring`, and comparative metrics. Ensure the optimizer yields output conforming to the QAOA structure.
- **Member 3 (Events):** The dashboard reads from `get_active_events()` and visualizes exact locations. Ensure `impact` arrays exist to render the blast-radius overlays.

## 5. Known Limitations
- The current interactive timeline heavily relies on the DemoManager when backend services are disconnected. 
- Map interactions (like clicking an intersection to manually close a road) are conceptual and currently mapped to sidebar controls.
