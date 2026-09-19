
const MetricCard = ({ title, value, unit }: { title: string, value: string | number, unit?: string }) => (
  <div className="bg-gray-800 p-4 rounded-lg shadow border border-gray-700">
    <h3 className="text-sm text-gray-400 mb-1">{title}</h3>
    <div className="text-2xl font-bold text-blue-100">
      {value} <span className="text-sm font-normal text-gray-500">{unit}</span>
    </div>
  </div>
);

const TrafficMetrics = ({ data, events }: { data: any, events: any[] }) => {
  if (!data) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <MetricCard title="Avg Wait Time" value={data.waiting_time} unit="sec" />
      <MetricCard title="Queue Length" value={data.queue_length} unit="veh" />
      <MetricCard title="Throughput" value={data.throughput} unit="veh/hr" />
      <MetricCard title="Avg Speed" value={data.speed} unit="km/h" />
      <MetricCard title="Fuel Consumed" value={data.fuel} unit="L/hr" />
      <MetricCard title="CO2 Emission" value={data.co2} unit="kg/hr" />
      <MetricCard title="Emergency Travel" value={data.emergency_time} unit="sec" />
      <MetricCard title="Active Events" value={events?.length || 0} />
    </div>
  );
};

export default TrafficMetrics;
