# Q-FLOW Simulation Module: Traffic Digital Twin

This module implements the **Traffic Digital Twin** for Q-FLOW using Eclipse SUMO and TraCI. It models a controlled 4-intersection arterial grid (J1, J2, J3, J4) with dual lanes, pedestrian crossings, dynamic signal timing, road incident handling, emergency priority vehicles, and real-time state extraction.

---

## 1. Prerequisites & Installation

### Option A: Running with SUMO (Live Digital Twin)
1. **Install SUMO**:
   - Download SUMO (>= 1.20.0) from [Eclipse SUMO Official Releases](https://eclipse.dev/sumo/).
   - Ensure `SUMO_HOME` is set in your environment variables (e.g. `C:\Program Files (x86)\Eclipse\Sumo\`).
   - Add `%SUMO_HOME%\bin` to your system `PATH`.
2. **Install Python Packages**:
   ```bash
   pip install -r requirements.txt
   ```

### Option B: Running in MOCK Mode (No SUMO Required)
Members 2 (Quantum Optimizer) and Member 4 (Dashboard) can run the module completely offline without installing SUMO:
```python
from simulation import TrafficSimulation

# Initialize in mock mode
sim = TrafficSimulation(mock=True)
sim.start()
state = sim.get_traffic_state()  # Returns 100% schema-compliant JSON
```

---

## 2. Network Structure

The simulation network is a deterministic 2x2 grid representing 4 interconnected signalized intersections:

```text
       N1           N2
        |            |
  W1 -- J1 -------- J2 -- E1
        |            |
        |            |
  W2 -- J3 -------- J4 -- E2
        |            |
       S1           S2
```

- **Junctions**: `J1`, `J2`, `J3`, `J4` (Signalized 4-phase traffic lights).
- **Perimeter Inflow/Outflow Edges**: `N1_J1`, `J1_N1`, `N2_J2`, `J2_N2`, `S1_J3`, `J3_S1`, `S2_J4`, `J4_S2`, `W1_J1`, `J1_W1`, `W2_J3`, `J3_W2`, `E1_J2`, `J2_E1`, `E2_J4`, `J4_E2`.
- **Internal Arterials**: `J1_J2`, `J2_J1`, `J3_J4`, `J4_J3`, `J1_J3`, `J3_J1`, `J2_J4`, `J4_J2`.
- **Road Specs**: Length = 150m, 2 lanes per edge + dedicated sidewalk (2.0m), speed limit = 50 km/h (13.89 m/s).
- **Capacity**: ~40 vehicles per edge.

---

## 3. Available Scenarios

Scenarios are located in `simulation/scenarios/` and can be selected via `scenario="<name>"`:

| Scenario | Description | Insertion Rate | Key Dynamics |
|---|---|---|---|
| `normal` | Balanced urban baseline traffic | Flow period: 10s | Mixed passenger flows & pedestrian crossings |
| `heavy_traffic` | Congestion & high demand | Flow period: 3-4s | Generates queues, high density, and delays |
| `emergency` | Scheduled priority ambulance | Flow period: 8-10s | Ambulance entering `W1` corridor destined for `E1` |
| `road_closure` | Corridor disruption | Flow period: 5s | Evaluates rerouting when `J1_J2` is closed |

---

## 4. Python API Reference

```python
from simulation import TrafficSimulation

# Initialize (mock=True or False)
sim = TrafficSimulation(mock=False, scenario="normal")

# Lifecycle
sim.start(gui=False)        # Start SUMO/TraCI session (set gui=True for visual viewer)
sim.step(steps=1)           # Advance simulation by N seconds
sim.stop()                  # Safely close TraCI session

# Telemetry
state = sim.get_traffic_state()          # Full TrafficState dictionary
j_state = sim.get_junction_state("J1")   # Junction-specific telemetry
e_state = sim.get_edge_state("J1_J2")    # Edge-specific telemetry
metrics = sim.get_metrics()              # Cumulative run performance metrics

# Control & Actions
sim.apply_signal_plan(signal_plan)       # Dynamic signal update from Member 2
sim.close_edge("J1_J2")                  # Road incident closure
sim.open_edge("J1_J2")                   # Reopen road
sim.add_emergency_vehicle(["W1_J1", "J1_J2", "J2_E1"])  # Dispatch priority ambulance
```

---

## 5. JSON Data Contracts

### A. Traffic State Contract (`get_traffic_state()`)

```json
{
  "timestamp": 1726749980.25,
  "simulation_time": 25.0,
  "junctions": {
    "J1": {
      "queue_ns": 4,
      "queue_ew": 2,
      "density": 0.225,
      "avg_speed": 42.5,
      "waiting_time": 6.8,
      "throughput": 12,
      "signal": "NS_GREEN",
      "pedestrian_waiting": 1
    }
  },
  "edges": {
    "J1_J2": {
      "vehicle_count": 8,
      "queue_length": 2,
      "density": 0.2,
      "average_speed": 44.1,
      "capacity": 40,
      "status": "OPEN"
    }
  },
  "global": {
    "vehicle_count": 35,
    "average_speed": 38.6,
    "average_waiting_time": 5.2,
    "total_queue": 6,
    "throughput": 15,
    "total_travel_time": 240.0,
    "fuel_consumption_ml": 84.2,
    "co2_emissions_g": 192.4
  }
}
```

### B. Signal Plan Contract (`apply_signal_plan()`)

Output format from **Member 2 (QUBO/QAOA Optimizer)** fed into SUMO:

```json
{
  "signal_plan": {
    "J1": {
      "NS_green": 45.0,
      "EW_green": 15.0
    },
    "J2": {
      "NS_green": 20.0,
      "EW_green": 40.0
    },
    "J3": {
      "NS_green": 35.0,
      "EW_green": 25.0
    },
    "J4": {
      "NS_green": 30.0,
      "EW_green": 30.0
    }
  }
}
```

---

## 6. Team Integration Guide

### For Member 2: Quantum Optimizer (QUBO / QAOA)
1. Query traffic state:
   ```python
   from simulation import TrafficSimulation
   sim = TrafficSimulation()
   sim.start()
   state = sim.get_traffic_state()
   # Read queue_ns, queue_ew, and density for each junction J1..J4
   ```
2. Formulate QUBO Hamiltonian using `queue_ns`, `queue_ew`, `density`, and `pedestrian_waiting`.
3. Compute optimal green times.
4. Apply the optimized timing back into SUMO:
   ```python
   sim.apply_signal_plan({
       "signal_plan": {
           "J1": {"NS_green": opt_ns, "EW_green": opt_ew},
           "J2": {"NS_green": opt_ns2, "EW_green": opt_ew2}
       }
   })
   sim.step(10) # Advance simulation with new timings active
   ```

### For Member 3: Event & Emergency Intelligence
1. **Road Incidents / Accidents**:
   ```python
   sim.close_edge("J1_J2")   # Closes corridor; SUMO auto-reroutes traffic
   # Inspect edge status
   assert sim.get_edge_state("J1_J2")["status"] == "CLOSED"
   # Once cleared:
   sim.open_edge("J1_J2")
   ```
2. **Emergency Green Corridor**:
   ```python
   route = ["W1_J1", "J1_J2", "J2_E1"]
   amb_id = sim.add_emergency_vehicle(route=route, vehicle_id="ambulance_01")
   ```

### For Member 4: Dashboard & Telemetry
1. In your polling or WebSocket loop:
   ```python
   state = sim.get_traffic_state()
   metrics = sim.get_metrics()
   ```
2. Stream `state["junctions"]`, `state["edges"]`, and `state["global"]` directly to your dashboard charts.
3. If running tests without SUMO installed on your local machine, use `TrafficSimulation(mock=True)`.

---

## 7. Running the Demonstration & Tests

### Run End-to-End Simulation Demo:
```bash
python simulation/run_simulation.py --steps 40 --scenario normal
```

### Run with SUMO GUI:
```bash
python simulation/run_simulation.py --steps 60 --gui
```

### Run in Offline Mock Mode:
```bash
python simulation/run_simulation.py --steps 30 --mock
```

### Run Unit and Integration Tests:
```bash
python -m pytest tests/ -v
```
