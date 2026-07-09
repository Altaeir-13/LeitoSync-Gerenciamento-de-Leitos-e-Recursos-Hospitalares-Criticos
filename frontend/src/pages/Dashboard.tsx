import { useEffect, useState } from 'react';
import api from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';

interface Summary {
  total_hospitals: number;
  total_resources: number;
  available: number;
  reserved: number;
  occupied: number;
  blocked: number;
  maintenance: number;
  occupancy_rate: number;
}

const Dashboard = () => {
  const [summary, setSummary] = useState<Summary | null>(null);
  
  // Connect to websocket to automatically trigger refetch on any updates
  const { messages } = useWebSocket(`${import.meta.env.VITE_API_URL?.replace('http', 'ws') || 'ws://localhost:8000'}/ws/resources`);

  const fetchSummary = async () => {
    try {
      const { data } = await api.get('/dashboard/summary');
      setSummary(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      fetchSummary();
    }
  }, [messages]);

  if (!summary) return <div className="p-4">Loading...</div>;

  const stats = [
    { label: 'Total Hospitals', value: summary.total_hospitals, color: 'bg-blue-100 text-blue-800' },
    { label: 'Total Resources', value: summary.total_resources, color: 'bg-indigo-100 text-indigo-800' },
    { label: 'Available', value: summary.available, color: 'bg-green-100 text-green-800' },
    { label: 'Reserved', value: summary.reserved, color: 'bg-yellow-100 text-yellow-800' },
    { label: 'Occupied', value: summary.occupied, color: 'bg-red-100 text-red-800' },
    { label: 'Blocked', value: summary.blocked, color: 'bg-gray-200 text-gray-800' },
    { label: 'Maintenance', value: summary.maintenance, color: 'bg-orange-100 text-orange-800' },
    { label: 'Occupancy Rate', value: `${summary.occupancy_rate.toFixed(1)}%`, color: 'bg-purple-100 text-purple-800' },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <h3 className="text-sm font-medium text-gray-500 mb-2">{stat.label}</h3>
            <p className={`text-3xl font-bold inline-block px-3 py-1 rounded-lg ${stat.color}`}>
              {stat.value}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
