
const EventPanel = ({ events }: { events: any[] }) => {
  return (
    <div className="bg-gray-800 p-4 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-4 text-blue-300">Active Events & Impact</h2>
      {!events || events.length === 0 ? (
        <p className="text-gray-400">No active events.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {events.map((e, i) => (
            <div key={i} className={`p-3 rounded border-l-4 ${e.type === 'ACCIDENT' ? 'border-red-500 bg-red-900/20' : e.type === 'ROAD_CLOSURE' ? 'border-purple-500 bg-purple-900/20' : 'border-orange-500 bg-orange-900/20'}`}>
              <div className="font-bold flex justify-between">
                <span>{e.type === 'ACCIDENT' ? '⚠ ACCIDENT' : e.type === 'ROAD_CLOSURE' ? '⛔ CLOSURE' : '🚗 CONGESTION'}</span>
                <span className="text-sm font-normal text-gray-400">{e.time}</span>
              </div>
              <p className="mt-1">{e.event}</p>
              <p className="text-sm text-gray-400">Status: {e.status}</p>
              {e.impact && (
                <div className="mt-2 text-sm bg-gray-900 p-2 rounded">
                  <p><strong>Direct Impact:</strong> {e.impact.direct?.join(', ')}</p>
                  <p><strong>Secondary:</strong> {e.impact.secondary?.join(', ')}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EventPanel;
