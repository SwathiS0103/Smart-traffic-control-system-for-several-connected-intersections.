import { useTrafficWebSocket } from './hooks/useTrafficWebSocket';
import Dashboard from './components/Dashboard/Dashboard';

function App() {
  const { trafficState, isConnected } = useTrafficWebSocket('ws://localhost:8000/ws/traffic');

  return (
    <div className="min-h-screen bg-gray-900 text-white font-sans p-4">
      <header className="flex justify-between items-center mb-6 pb-4 border-b border-gray-700">
        <h1 className="text-2xl font-bold text-blue-400">Q-FLOW Dashboard (Live)</h1>
        <div className="flex gap-4">
          <span className={isConnected ? "text-green-400" : "text-red-400"}>
            {isConnected ? "● WS Connected" : "○ WS Disconnected"}
          </span>
          <span className={trafficState?.sumo_connected ? "text-green-400" : "text-yellow-400"}>
            {trafficState?.sumo_connected ? "● SUMO Connected" : "● Demo Mode"}
          </span>
        </div>
      </header>

      {trafficState ? (
        <Dashboard data={trafficState} />
      ) : (
        <div className="flex items-center justify-center h-64">
          <p className="text-xl text-gray-400">Waiting for data...</p>
        </div>
      )}
    </div>
  );
}

export default App;
