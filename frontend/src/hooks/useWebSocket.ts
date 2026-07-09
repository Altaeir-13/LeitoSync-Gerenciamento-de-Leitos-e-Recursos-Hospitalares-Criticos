import { useEffect, useState } from 'react';

type WebSocketMessage = {
  type: string;
  resource_id: number;
  new_status: string;
  timestamp: string;
};

export const useWebSocket = (url: string) => {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        if (data.type === 'RESOURCE_UPDATED') {
          setMessages((prev) => [...prev, data]);
        }
      } catch (e) {
        console.error('Failed to parse WS message', e);
      }
    };

    return () => {
      ws.close();
    };
  }, [url]);

  return { messages };
};
