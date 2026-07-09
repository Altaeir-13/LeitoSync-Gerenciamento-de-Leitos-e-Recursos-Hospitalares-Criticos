import { useEffect, useState } from 'react';
import api from '../services/api';

const AuditLogs = () => {
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const { data } = await api.get('/audit-logs');
        setLogs(data);
      } catch (e) {
        console.error(e);
      }
    };
    fetchLogs();
  }, []);

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date/Time</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resource ID</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Old Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">New Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actor</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {logs.map((log) => (
            <tr key={log.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(log.created_at).toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{log.resource_id}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">{log.action}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{log.old_status || '-'}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{log.new_status}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{log.actor_name}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {logs.length === 0 && (
        <div className="p-8 text-center text-gray-500">No audit logs found.</div>
      )}
    </div>
  );
};

export default AuditLogs;
