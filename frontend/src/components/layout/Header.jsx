import { Link, useLocation } from 'react-router-dom';
import { PenTool, Home, FileText } from 'lucide-react';
import clsx from 'clsx';

export default function Header() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-40 backdrop-blur-sm bg-white/95">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="bg-primary-600 p-2 rounded-lg group-hover:bg-primary-700 transition-colors">
              <PenTool className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">
              Redator <span className="text-primary-600">ENEM</span>
            </span>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center gap-6">
            <Link
              to="/"
              className={clsx(
                'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive('/')
                  ? 'bg-primary-50 text-primary-600'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              )}
            >
              <Home className="h-4 w-4" />
              Início
            </Link>

            <Link
              to="/corrigir"
              className={clsx(
                'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive('/corrigir')
                  ? 'bg-primary-50 text-primary-600'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              )}
            >
              <FileText className="h-4 w-4" />
              Corrigir
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
