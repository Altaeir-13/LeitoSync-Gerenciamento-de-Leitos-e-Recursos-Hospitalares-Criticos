import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Building2, BedDouble, Activity, ShieldAlert } from 'lucide-react';
import clsx from 'clsx';

const Layout = () => {
  const location = useLocation();

  const navItems = [
    { name: 'Painel', path: '/', icon: LayoutDashboard },
    { name: 'Hospitais', path: '/hospitals', icon: Building2 },
    { name: 'Recursos', path: '/resources', icon: BedDouble },
    { name: 'Simulador', path: '/simulator', icon: Activity },
    { name: 'Auditoria', path: '/audit-logs', icon: ShieldAlert },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex-shrink-0">
        <div className="h-16 flex items-center px-6 border-b border-gray-200">
          <BedDouble className="w-8 h-8 text-blue-600 mr-2" />
          <span className="text-xl font-bold text-gray-900">LeitoSync</span>
        </div>
        <nav className="p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || 
              (item.path !== '/' && location.pathname.startsWith(item.path));
            
            return (
              <Link
                key={item.name}
                to={item.path}
                className={clsx(
                  'flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                )}
              >
                <Icon className={clsx('w-5 h-5 mr-3', isActive ? 'text-blue-700' : 'text-gray-400')} />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-8 flex-shrink-0">
          <h1 className="text-xl font-semibold text-gray-800">
            {navItems.find(i => location.pathname === i.path || (i.path !== '/' && location.pathname.startsWith(i.path)))?.name || 'Dashboard'}
          </h1>
        </header>
        <div className="flex-1 overflow-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
