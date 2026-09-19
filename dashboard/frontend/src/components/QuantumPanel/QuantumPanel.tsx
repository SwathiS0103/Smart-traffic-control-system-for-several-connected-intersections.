import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const QuantumPanel = ({ quantum, signals }: { quantum: any, signals: any }) => {
  if (!quantum) return null;

  const chartData = quantum.top_strings ? Object.entries(quantum.top_strings).map(([bitstring, prob]) => ({
    bitstring,
    Probability: prob
  })) : [];

  return (
    <div className="bg-gray-800 p-4 rounded-lg shadow-lg flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-bold mb-4 text-blue-300">Quantum Optimization (QAOA)</h2>
        <div className="grid grid-cols-2 gap-4 text-sm bg-gray-900 p-4 rounded">
            <div>
                <p><strong>Method:</strong> {quantum.method}</p>
                <p><strong>Backend:</strong> {quantum.backend}</p>
                <p><strong>QAOA Depth (p):</strong> {quantum.depth}</p>
                <p><strong>Shots:</strong> {quantum.shots}</p>
            </div>
            <div>
                <p><strong>Variables:</strong> {quantum.variables}</p>
                <p><strong>Obj Value:</strong> {quantum.objective_value}</p>
                <p><strong>Exec Time:</strong> {quantum.execution_time}</p>
                <p><strong>Best State:</strong> <code className="bg-gray-800 px-1 rounded text-green-400">{quantum.best_bitstring}</code></p>
            </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-bold mb-2 text-gray-300">Top Measured States</h3>
        <div className="h-48 w-full bg-gray-900 rounded p-2">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                    <XAxis type="number" hide />
                    <YAxis dataKey="bitstring" type="category" stroke="#9ca3af" fontSize={12} width={100} />
                    <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', color: '#fff' }} />
                    <Bar dataKey="Probability" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
      </div>

      {signals && (
        <div>
            <h3 className="text-lg font-bold mb-2 text-gray-300">Signal Optimization Comparison</h3>
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="bg-gray-700 text-gray-300">
                        <tr>
                            <th className="px-4 py-2 rounded-tl">Junction</th>
                            <th className="px-4 py-2">Current</th>
                            <th className="px-4 py-2">Classical</th>
                            <th className="px-4 py-2 rounded-tr text-blue-400">QAOA</th>
                        </tr>
                    </thead>
                    <tbody>
                        {Object.entries(signals).map(([j, s]: [string, any], i) => (
                            <tr key={i} className="border-b border-gray-700 hover:bg-gray-750">
                                <td className="px-4 py-2 font-bold">{j}</td>
                                <td className="px-4 py-2 text-gray-400">{s.current}</td>
                                <td className="px-4 py-2">{s.classical}</td>
                                <td className="px-4 py-2 font-bold text-blue-400">{s.qaoa}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
      )}
    </div>
  );
};

export default QuantumPanel;
