import { MapContainer, TileLayer, Polyline, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';



const TrafficMap = ({ data }: { data: any }) => {
  if (!data || !data.edges) return <div className="h-96 bg-gray-700 rounded animate-pulse" />;

  const center: [number, number] = [13.085, 80.275];

  return (
    <div className="h-96 w-full rounded-lg overflow-hidden border border-gray-700 z-0">
      <MapContainer center={center} zoom={15} style={{ height: '100%', width: '100%', background: '#1a1a2e' }}>
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        
        {data.edges.map((edge: any, i: number) => {
          let color = '#22c55e'; // green
          if (edge.density > 0.6) color = '#f97316'; // orange
          if (edge.density > 0.8) color = '#ef4444'; // red
          let dashArray = '';
          
          if (edge.status === 'CLOSED') {
            color = '#000000';
            dashArray = '5, 10';
          } else if (edge.status === 'ACCIDENT') {
            color = '#a855f7'; // purple
          }

          return (
            <Polyline 
              key={`edge-${i}`} 
              positions={edge.coords} 
              color={color} 
              weight={edge.status === 'CLOSED' ? 4 : 6}
              dashArray={dashArray}
            >
                <Popup>
                    <div className="text-black">
                        <strong>Road ID:</strong> {edge.id}<br/>
                        <strong>Density:</strong> {edge.density}<br/>
                        <strong>Status:</strong> {edge.status}
                    </div>
                </Popup>
            </Polyline>
          );
        })}

        {Object.entries(data.junctions).map(([id, j]: [string, any]) => {
          let color = '#22c55e';
          if (j.density > 0.6) color = '#f97316';
          if (j.density > 0.8) color = '#ef4444';

          return (
            <CircleMarker 
              key={`j-${id}`}
              center={[j.lat, j.lon]}
              radius={8}
              pathOptions={{ fillColor: color, color: '#fff', weight: 1, fillOpacity: 0.9 }}
            >
              <Popup>
                <div className="text-black">
                    <strong>Junction {id}</strong><br/>
                    <strong>Queue:</strong> {j.queue}<br/>
                    <strong>Signal:</strong> {j.signal}
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default TrafficMap;
