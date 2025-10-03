import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../ui/LoadingSpinner';

/**
 * Componente para proteger rotas que requerem autenticação
 * Redireciona para login se não estiver autenticado
 */
export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  // Mostrar loading enquanto verifica autenticação
  if (loading) {
    return <LoadingSpinner fullScreen size="xl" text="Verificando autenticação..." />;
  }

  // Se não estiver autenticado, redirecionar para login
  if (!isAuthenticated) {
    // Salvar a localização que o usuário estava tentando acessar
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Se autenticado, mostrar o conteúdo
  return children;
}
