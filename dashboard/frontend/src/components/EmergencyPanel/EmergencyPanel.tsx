
const EmergencyPanel = ({ emergencies }: { emergencies: any[] }) => {
  return (
    <div className="bg-gray-800 p-4 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-4 text-blue-300">Emergency Operations</h2>
      {!emergencies || emergencies.length === 0 ? (
        <p className="text-gray-400">No active emergency vehicles.</p>
      ) : (
        <div className="flex flex-col gap-4">
          {emergencies.map((e, i) => (
            <div key={i} className="p-3 rounded border border-green-500 bg-green-900/10">
              <h3 className="font-bold text-green-400 mb-2 flex items-center gap-2">
                🚑 {e.vehicle_id} - {e.status}
              </h3>
              <div className="grid grid-cols-2 gap-2 text-sm mb-2">
                <div><strong>Origin:</strong> {e.origin}</div>
                <div><strong>Destination:</strong> {e.destination}</div>
                <div><strong>ETA:</strong> {e.eta} sec</div>
              </div>
              <div className="text-sm text-gray-300 mb-2">
                <strong>Route:</strong> {e.route?.join(' → ')}
              </div>
              
              {e.corridor && (
                <div className="mt-3">
                  <h4 className="text-xs font-bold text-gray-400 uppercase mb-1">🟢 Green Corridor Schedule</h4>
                  <div className="bg-gray-900 rounded p-2 text-sm flex flex-col gap-1">
                    {e.corridor.map((c: any, j: number) => (
                      <div key={j} className="flex justify-between border-b border-gray-800 last:border-0 pb-1 last:pb-0">
                        <span><strong>{c.junction}</strong> (ETA: {c.eta}s)</span>
                        <span className="text-green-400">Green: {c.green_start}s - {c.green_end}s</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EmergencyPanel;
