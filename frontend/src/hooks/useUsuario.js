import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

/**
 * Lista correções do usuário
 */
export function useListarCorrecoes(usuarioId, limit = 100) {
  return useQuery({
    queryKey: ['correcoes-usuario', usuarioId, limit],
    queryFn: async () => {
      const response = await api.get('/usuario/correcoes', {
        params: { limit, ordem: 'desc' }
      });
      return response.data;
    },
    enabled: !!usuarioId,
  });
}

/**
 * Busca estatísticas do usuário
 */
export function useEstatisticasUsuario() {
  return useQuery({
    queryKey: ['estatisticas-usuario'],
    queryFn: async () => {
      const response = await api.get('/usuario/estatisticas');
      return response.data;
    },
  });
}

/**
 * Busca dados do dashboard
 */
export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await api.get('/usuario/dashboard');
      return response.data;
    },
  });
}
