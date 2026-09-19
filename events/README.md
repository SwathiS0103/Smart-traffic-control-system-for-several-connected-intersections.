# Q-FLOW: Dynamic Event Management (Member 3)

The Dynamic Event Management module provides the intelligence layer for handling traffic anomalies in real-time. Sitting between the Traffic Digital Twin (Member 1) and the Quantum Optimization Engine (Member 2), this module evaluates raw traffic data to detect congestion, manage road closures, compute dynamic routing for emergency vehicles, and shift optimizer priorities instantly.

## 1. What Member 3 Does
- **Detects Anomalies:** Analyzes density and speed to trigger congestion events.
- **Analyzes Impact:** Calculates the blast-radius of accidents and closures across adjacent intersections.
- **Reroutes Traffic & Emergencies:** Utilizes NetworkX graph routing to circumvent road closures.
- **Generates Green Corridors:** Computes precise time windows for emergency vehicles to pass through intersections based on ETAs.
- **Adjusts Priorities Dynamically:** Modifies the weights (queue, waiting, emergency, throughput) for the Quantum Optimizer based on the highest priority active event.

## 2. Architecture & Event Lifecycle

```text
Traffic State
      ↓
Event Detection & Engine
      ↓
Event Classification (Congestion, Emergency, Closure)
      ↓
Impact Analysis
      ↓
Prediction & Rerouting
      ↓
 ┌───────────────┐
 │ Emergency?    │
 └───────┬───────┘
         │
      YES│
         ↓
 Emergency Route
         ↓
 ETA Calculation
         ↓
 Green Corridor
         ↓
 Safety Validation
         ↓
 Optimizer Request (Dynamic Weights)
```

**Lifecycle**: Events start as `PENDING`, are activated to `ACTIVE`, and ultimately marked `RESOLVED`. Once resolved, the `RecoveryManager` computes a necessary recovery period before releasing normal operations to smooth out residual queues.

## 3. Project Novelty

This module introduces several advanced features over basic signal controllers:
1. **Event impact / blast-radius analysis:** We compute both direct and secondary affected junctions.
2. **Predictive event response:** Short-term queue growth is predicted based on arrival and severity-adjusted departure rates.
3. **ETA-based emergency green-wave reservation:** We do not blindly turn lights green; we compute exact ETA time-windows.
4. **Emergency corridor safety validation:** We validate green windows against safety constraints (minimum green times, clearance times).
5. **Dynamic objective weighting:** Optimization priorities fluidly shift depending on the context (e.g., heavily weighting throughput during closures).
6. **Event-aware communication with quantum optimizer:** We translate the messy real-world anomalies into a clean mathematical request (`optimizer_request.json`) for Member 2.

## 4. Integration

- **Integration with Member 1 (SUMO Twin):** Exposes `IntegrationAdapter.parse_traffic_state()` to read incoming real-time schema from the simulation.
- **Integration with Member 2 (Quantum Optimizer):** Formats output into a cohesive payload containing traffic states, active closures, emergency routes, and dynamic weights.
- **Integration with Member 4 (Dashboard):** Provides a FastAPI service (`api.py`) where Member 4 can `GET /events/active` and visualize ETAs and blast radii.

## 5. How to Run & Test

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Run End-to-End Mock Scenarios:**
This script simulates Normal Traffic, Sudden Congestion, Road Closures, and Emergency Dispatch/Rerouting.
```bash
python run_event_demo.py
```

**Run API Server for Dashboard Integration:**
```bash
uvicorn src.api:app --reload
```

**Run Unit Tests:**
```bash
pytest tests/
```

## 6. Known Limitations & Future ML Enhancement
- **Limitation:** Arrival and departure rates are currently deterministic heuristics based on density and severity.
- **Future ML Enhancement:** `CongestionPredictor` is designed to be easily swapped with an LSTM or Graph Neural Network (GNN) model that ingests historical state data to predict exact queue lengths 30, 60, and 120 seconds into the future.
