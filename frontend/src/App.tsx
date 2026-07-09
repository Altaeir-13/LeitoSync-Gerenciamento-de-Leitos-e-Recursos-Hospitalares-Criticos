import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Hospitals from './pages/Hospitals';
import Resources from './pages/Resources';
import ResourceDetail from './pages/ResourceDetail';
import Simulator from './pages/Simulator';
import AuditLogs from './pages/AuditLogs';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="hospitals" element={<Hospitals />} />
          <Route path="resources" element={<Resources />} />
          <Route path="resources/:id" element={<ResourceDetail />} />
          <Route path="simulator" element={<Simulator />} />
          <Route path="audit-logs" element={<AuditLogs />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
