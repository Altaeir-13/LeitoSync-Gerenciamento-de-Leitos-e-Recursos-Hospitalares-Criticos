import { useState, useEffect } from 'react';
import api from '../services/api';
import { Activity, BookOpen, PenTool, AlertCircle, CheckCircle2 } from 'lucide-react';
import { STATUS_MAP } from '../utils/translations';

const Simulator = () => {
  const [resources, setResources] = useState<any[]>([]);
  const [selectedResource, setSelectedResource] = useState('');
  const [readersCount, setReadersCount] = useState(10);
  const [writersCount, setWritersCount] = useState(5);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchResources = async () => {
      const { data } = await api.get('/resources');
      setResources(data);
      if (data.length > 0) setSelectedResource(data[0].id.toString());
    };
    fetchResources();
  }, []);

  const runSimulation = async () => {
    if (!selectedResource) return;
    setLoading(true);
    setResults(null);
    try {
      const { data } = await api.post(`/simulation/readers-writers`, null, {
        params: {
          resource_id: selectedResource,
          readers_count: readersCount,
          writers_count: writersCount,
        }
      });
      setResults(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <div className="flex items-center mb-4">
          <Activity className="w-8 h-8 text-blue-600 mr-3" />
          <h2 className="text-2xl font-bold text-gray-900">Simulador de Leitores e Escritores</h2>
        </div>
        <p className="text-gray-600 mb-6">
          Este simulador demonstra de forma didática como o sistema lida com o acesso concorrente a um recurso compartilhado (problema clássico de sistemas distribuídos).
          <br/>
          <strong>Leitores</strong> (Operações de Consulta): Múltiplos leitores podem consultar o status de um recurso ao mesmo tempo, sem bloqueios (concorrência permitida). <br/>
          <strong>Escritores</strong> (Operações de Reserva/Modificação): Escritores precisam de acesso exclusivo sobre o recurso. Quando vários escritores tentam modificar o mesmo recurso simultaneamente, o banco de dados impõe bloqueio de linha (Row-Level Lock) via transações. Apenas uma operação é confirmada, enquanto os demais escritores recebem erro de conflito (HTTP 409).
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Recurso Alvo</label>
            <select
              value={selectedResource}
              onChange={(e) => setSelectedResource(e.target.value)}
              className="w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
            >
              {resources.map((r) => (
                <option key={r.id} value={r.id}>{r.code} ({STATUS_MAP[r.status] || r.status})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Leitores Simultâneos</label>
            <input
              type="number"
              value={readersCount}
              onChange={(e) => setReadersCount(Number(e.target.value))}
              min="1"
              max="50"
              className="w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Escritores Simultâneos</label>
            <input
              type="number"
              value={writersCount}
              onChange={(e) => setWritersCount(Number(e.target.value))}
              min="1"
              max="50"
              className="w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
            />
          </div>
        </div>

        <button
          onClick={runSimulation}
          disabled={loading || !selectedResource}
          className="w-full bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Rodando Simulação...' : 'Executar Operações Concorrentes'}
        </button>
      </div>

      {results && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col items-center justify-center text-center">
            <Activity className="w-10 h-10 text-gray-400 mb-2" />
            <span className="text-sm text-gray-500">Total de Op. Executadas</span>
            <span className="text-3xl font-bold text-gray-900">{results.total_operations}</span>
          </div>
          <div className="bg-white p-6 rounded-xl border border-blue-200 shadow-sm flex flex-col items-center justify-center text-center">
            <BookOpen className="w-10 h-10 text-blue-500 mb-2" />
            <span className="text-sm text-blue-600">Leituras com Sucesso</span>
            <span className="text-3xl font-bold text-blue-900">{results.read_success}</span>
          </div>
          <div className="bg-white p-6 rounded-xl border border-green-200 shadow-sm flex flex-col items-center justify-center text-center">
            <CheckCircle2 className="w-10 h-10 text-green-500 mb-2" />
            <span className="text-sm text-green-600">Escritas Confirmadas (Lock Adquirido)</span>
            <span className="text-3xl font-bold text-green-900">{results.write_success}</span>
          </div>
          <div className="bg-white p-6 rounded-xl border border-red-200 shadow-sm flex flex-col items-center justify-center text-center">
            <AlertCircle className="w-10 h-10 text-red-500 mb-2" />
            <span className="text-sm text-red-600">Escritas Rejeitadas (Conflito HTTP 409)</span>
            <span className="text-3xl font-bold text-red-900">{results.write_rejected}</span>
          </div>
        </div>
      )}

      {results && (
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
          <h3 className="text-lg font-medium text-blue-800 mb-2">Conclusão</h3>
          <p className="text-blue-700">
            De um total de {writersCount} escritores tentando reservar o recurso simultaneamente, apenas {results.write_success} obteve sucesso, pois o banco de dados garantiu o bloqueio da linha (SELECT FOR UPDATE). Os outros {results.write_rejected} escritores foram rejeitados para evitar reserva duplicada (conflito). Enquanto isso, todos os {results.read_success} leitores puderam consultar o estado sem serem bloqueados!
          </p>
        </div>
      )}
    </div>
  );
};

export default Simulator;
