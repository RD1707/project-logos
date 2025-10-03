import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { User, LogOut, Settings, FileText, ChevronDown, LayoutDashboard, ArrowLeftRight } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

export default function UserMenu() {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);

  // Fechar menu ao clicar fora
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    setIsOpen(false);
    await logout();
  };

  // Obter iniciais do nome para avatar
  const getInitials = (name) => {
    if (!name) return 'U';
    const parts = name.split(' ');
    if (parts.length === 1) return parts[0][0].toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  };

  return (
    <div className="relative" ref={menuRef}>
      {/* Botão do Menu */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
      >
        {/* Avatar */}
        {user?.avatar_url ? (
          <img
            src={user.avatar_url}
            alt={user.nome}
            className="w-8 h-8 rounded-full object-cover"
          />
        ) : (
          <div className="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-semibold">
            {getInitials(user?.nome)}
          </div>
        )}

        {/* Nome (esconder em mobile) */}
        <span className="hidden sm:block text-sm font-medium text-gray-700">
          {user?.nome?.split(' ')[0]}
        </span>

        {/* Ícone */}
        <ChevronDown
          className={`h-4 w-4 text-gray-500 transition-transform ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50"
          >
            {/* Info do Usuário */}
            <div className="px-4 py-3 border-b border-gray-100">
              <p className="text-sm font-semibold text-gray-900">{user?.nome}</p>
              <p className="text-xs text-gray-500 truncate">{user?.email}</p>
            </div>

            {/* Menu Items */}
            <div className="py-1">
              <Link
                to="/dashboard"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <LayoutDashboard className="h-4 w-4" />
                Dashboard
              </Link>

              <Link
                to="/perfil"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <User className="h-4 w-4" />
                Meu Perfil
              </Link>

              <Link
                to="/historico"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <FileText className="h-4 w-4" />
                Histórico
              </Link>

              <Link
                to="/comparar"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <ArrowLeftRight className="h-4 w-4" />
                Comparar
              </Link>
            </div>

            {/* Logout */}
            <div className="border-t border-gray-100 py-1">
              <button
                onClick={handleLogout}
                className="flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors w-full"
              >
                <LogOut className="h-4 w-4" />
                Sair
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
