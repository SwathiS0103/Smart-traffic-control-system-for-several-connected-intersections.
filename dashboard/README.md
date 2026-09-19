# Q-FLOW: Full-Stack Dashboard (Member 4)

This module provides the central visualization and integration layer for the Quantum-Enhanced Adaptive Urban Traffic Optimization system, rewritten in React, TypeScript, and FastAPI.

## 1. Architecture

```text
       ┌─────────────────────┐
       │   REACT FRONTEND    │
       │ (Vite, TypeScript,  │
       │  Leaflet, Recharts) │
       └──────────┬──────────┘
                  │
            WebSocket / REST
                  │
       ┌──────────┴──────────┐
       │   FASTAPI BACKEND   │
       │ (Uvicorn, Pydantic, │
       │  Adapters, Mocks)   │
       └─┬─────────┬────────┬┘
         │         │        │
       SUMO      QUBO     EVENT
        M1        M2       M3 
```

## 2. Project Structure
- `frontend/`: The React + TypeScript + Vite dashboard application.
- `backend/`: The FastAPI python server handling integration and WebSockets.
- `legacy_dashboard/`: The original Streamlit implementation (preserved as a prototype).

## 3. How to Run

### Backend
1. Open a terminal and navigate to `backend/`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Start the Uvicorn server: `uvicorn app.main:app --port 8000`
4. The API and WebSocket will be available at `localhost:8000`.

### Frontend
1. Open a new terminal and navigate to `frontend/`.
2. Install dependencies: `npm install`.
3. Start the Vite dev server: `npm run dev`.
4. The dashboard will be available at `http://localhost:5173`.

## 4. Features
- **Real-Time WebSocket Updates:** Data flows instantly from backend to frontend without polling.
- **Folium to Leaflet Migration:** The live topological map is now natively rendered in React.
- **Robust Mock Mode:** If Member 1, 2, or 3 are offline, the `DemoManager` adapter seamlessly takes over to ensure the dashboard still displays complex event simulations to the judges.
