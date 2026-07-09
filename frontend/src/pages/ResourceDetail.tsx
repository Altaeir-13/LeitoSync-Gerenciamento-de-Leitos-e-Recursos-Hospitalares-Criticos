import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { rpcCall } from '../services/rpcClient';
import { useWebSocket } from '../hooks/useWebSocket';
import { STATUS_MAP, ACTION_MAP } from '../utils/translations';

const statusColors: Record<string, string> = {
  available: 'bg-green-100 text-green-800',
  reserved: 'bg-yellow-100 text-yellow-800',
  occupied: 'bg-red-100 text-red-800',
  blocked: 'bg-gray-200 text-gray-800',
  maintenance: 'bg-orange-100 text-orange-800',
};

const ResourceDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [resource, setResource] = useState<any>(null);
  const [error, setError] = useState('');
  const [actionSuccess, setActionSuccess] = useState('');

  const { messages } = useWebSocket(`${import.meta.env.VITE_API_URL?.replace('http', 'ws') || 'ws://localhost:8000'}/ws/resources`);

  const fetchResource = async () => {
    try {
      const data = await rpcCall<any>('recursos.obter', { resource_id: Number(id) });
      setResource(data);
    } catch (e) {
      console.error(e);
      setError('Falha ao carregar recurso.');
    }
  };

  useEffect(() => {
    fetchResource();
  }, [id]);

  useEffect(() => {
    if (messages.length > 0) {
      const latestMsg = messages[messages.length - 1];
      if (latestMsg.resource_id === Number(id)) {
        fetchResource();
      }
    }
  }, [messages, id]);

  const handleAction = async (action: string) => {
    setError('');
    setActionSuccess('');
    try {
      if (action === 'reserve') {
        await rpcCall('recursos.reservar', {
          resource_id: Number(id),
          requester_name: 'Operador',
          priority: 'medium',
          reason: 'Reserva manual'
        });
      } else {
        await rpcCall(`recursos.${action}`, {
          resource_id: Number(id),
          actor_name: 'Operador',
          reason: `Ação manual: ${action}`
        });
      }
      setActionSuccess(`${ACTION_MAP[action] || action} realizado com sucesso`);
      fetchResource();
    } catch (e: any) {
      setError(e.response?.data?.detail || `Falha ao executar ${action}`);
    }
  };

  if (!resource) return <div className="p-4">Carregando...</div>;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <button onClick={() => navigate(-1)} className="text-blue-600 hover:underline mb-4 inline-block">
        &larr; Voltar para Recursos
      </button>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">{error}</div>}
      {actionSuccess && <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">{actionSuccess}</div>}

      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{resource.code}</h2>
            <p className="text-sm text-gray-500 mt-1">
              Hospital: {resource.hospital?.name} | Tipo: {resource.resource_type?.name}
            </p>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${statusColors[resource.status] || 'bg-gray-100'}`}>
            {STATUS_MAP[resource.status] || resource.status.toUpperCase()}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="bg-gray-50 p-4 rounded-lg">
            <span className="text-sm text-gray-500">Versão Atual</span>
            <p className="text-lg font-semibold text-gray-900">v{resource.version}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <span className="text-sm text-gray-500">Última Atualização</span>
            <p className="text-lg font-semibold text-gray-900">{new Date(resource.updated_at).toLocaleString('pt-BR')}</p>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Ações</h3>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => handleAction('reserve')}
              disabled={resource.status !== 'available'}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Reservar
            </button>
            <button
              onClick={() => handleAction('occupy')}
              disabled={!['available', 'reserved'].includes(resource.status)}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Ocupar
            </button>
            <button
              onClick={() => handleAction('release')}
              disabled={resource.status === 'available'}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Liberar
            </button>
            <button
              onClick={() => handleAction('block')}
              disabled={['blocked', 'maintenance', 'occupied'].includes(resource.status)}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Bloquear
            </button>
            <button
              onClick={() => handleAction('maintenance')}
              disabled={['maintenance', 'occupied'].includes(resource.status)}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Manutenção
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResourceDetail;
