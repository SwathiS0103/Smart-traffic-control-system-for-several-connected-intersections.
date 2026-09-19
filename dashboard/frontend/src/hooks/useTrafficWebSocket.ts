import { useState, useEffect } from 'react';

type WebSocketMessage = {
  type: string;
  state: any;
};

export const useTrafficWebSocket = (url: string) => {
  const [trafficState, setTrafficState] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);

    ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        if (data.type === 'TRAFFIC_UPDATE') {
          setTrafficState(data.state);
        }
      } catch (err) {
        console.error("Error parsing WS message:", err);
      }
    };

    return () => {
      ws.close();
    };
  }, [url]);

  return { trafficState, isConnected };
};
