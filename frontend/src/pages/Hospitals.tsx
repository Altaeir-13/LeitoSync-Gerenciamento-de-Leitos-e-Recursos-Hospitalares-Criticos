import { useEffect, useState } from 'react';
import api from '../services/api';

interface Hospital {
  id: number;
  name: string;
  city: string;
  state: string;
  active: boolean;
}

const Hospitals = () => {
  const [hospitals, setHospitals] = useState<Hospital[]>([]);

  useEffect(() => {
    const fetchHospitals = async () => {
      try {
        const { data } = await api.get('/hospitals');
        setHospitals(data);
      } catch (e) {
        console.error(e);
      }
    };
    fetchHospitals();
  }, []);

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cidade</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {hospitals.map((hospital) => (
            <tr key={hospital.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{hospital.id}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{hospital.name}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{hospital.city}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{hospital.state}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${hospital.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {hospital.active ? 'Ativo' : 'Inativo'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Hospitals;
