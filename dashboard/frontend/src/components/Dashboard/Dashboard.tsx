import TrafficMetrics from '../TrafficMetrics/TrafficMetrics';
import TrafficMap from '../TrafficMap/TrafficMap';
import EventPanel from '../EventPanel/EventPanel';
import EmergencyPanel from '../EmergencyPanel/EmergencyPanel';
import QuantumPanel from '../QuantumPanel/QuantumPanel';
import ComparisonPanel from '../ComparisonPanel/ComparisonPanel';
import axios from 'axios';

const Dashboard = ({ data }: { data: any }) => {
  const handleScenarioChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    try {
      await axios.post('http://localhost:8000/api/simulation/scenario', { name: e.target.value });
    } catch (err) {
      console.error(err);
    }
  };

  const startSim = async () => axios.post('http://localhost:8000/api/simulation/start');
  const pauseSim = async () => axios.post('http://localhost:8000/api/simulation/pause');
  const resetSim = async () => axios.post('http://localhost:8000/api/simulation/reset');

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-center bg-gray-800 p-4 rounded-lg">
        <div className="flex gap-4 items-center">
            <span className="font-bold">Scenario:</span>
            <select onChange={handleScenarioChange} className="bg-gray-700 p-2 rounded">
                <option value="Normal Traffic">Normal Traffic</option>
                <option value="Congestion">Congestion</option>
                <option value="Accident">Accident</option>
                <option value="Closure">Closure</option>
                <option value="Emergency">Emergency</option>
                <option value="Emergency + Closure">Emergency + Closure</option>
            </select>
        </div>
        <div className="flex gap-2">
            <button onClick={startSim} className="bg-green-600 px-4 py-2 rounded hover:bg-green-500">Play</button>
            <button onClick={pauseSim} className="bg-yellow-600 px-4 py-2 rounded hover:bg-yellow-500">Pause</button>
            <button onClick={resetSim} className="bg-red-600 px-4 py-2 rounded hover:bg-red-500">Reset</button>
        </div>
      </div>

      <TrafficMetrics data={data.metrics} events={data.events} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 flex flex-col gap-6">
          <div className="bg-gray-800 p-4 rounded-lg shadow-lg">
            <h2 className="text-xl font-bold mb-4 text-blue-300">Live Traffic Map</h2>
            <TrafficMap data={data} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <EventPanel events={data.events} />
            <EmergencyPanel emergencies={data.emergencies} />
          </div>
        </div>
        
        <div className="flex flex-col gap-6">
          <QuantumPanel quantum={data.quantum} signals={data.signal_comparison} />
        </div>
      </div>

      <ComparisonPanel data={data.performance_comparison} />
    </div>
  );
};

export default Dashboard;
