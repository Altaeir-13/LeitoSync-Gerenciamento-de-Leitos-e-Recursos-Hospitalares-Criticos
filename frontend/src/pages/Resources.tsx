import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';

interface Resource {
  id: number;
  code: string;
  hospital_id: number;
  resource_type_id: number;
  status: string;
  version: number;
}

const statusColors: Record<string, string> = {
  available: 'bg-green-100 text-green-800',
  reserved: 'bg-yellow-100 text-yellow-800',
  occupied: 'bg-red-100 text-red-800',
  blocked: 'bg-gray-200 text-gray-800',
  maintenance: 'bg-orange-100 text-orange-800',
};

const Resources = () => {
  const [resources, setResources] = useState<Resource[]>([]);
  const { messages } = useWebSocket(`${import.meta.env.VITE_API_URL?.replace('http', 'ws') || 'ws://localhost:8000'}/ws/resources`);

  const fetchResources = async () => {
    try {
      const { data } = await api.get('/resources');
      setResources(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchResources();
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      const latestMsg = messages[messages.length - 1];
      setResources(prev => prev.map(r => 
        r.id === latestMsg.resource_id ? { ...r, status: latestMsg.new_status, version: r.version + 1 } : r
      ));
    }
  }, [messages]);

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Code</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hospital ID</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type ID</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Version</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {resources.map((resource) => (
            <tr key={resource.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{resource.code}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{resource.hospital_id}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{resource.resource_type_id}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusColors[resource.status] || 'bg-gray-100 text-gray-800'}`}>
                  {resource.status.toUpperCase()}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">v{resource.version}</td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <Link to={`/resources/${resource.id}`} className="text-blue-600 hover:text-blue-900">
                  View Details
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Resources;
