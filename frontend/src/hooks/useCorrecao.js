import { useMutation, useQuery } from '@tanstack/react-query';
import { corrigirRedacao, buscarCorrecao } from '../services/api';

/**
 * Hook para corrigir redação
 */
export function useCorrigirRedacao() {
  return useMutation({
    mutationFn: corrigirRedacao,
    onSuccess: (data) => {
      console.log('Redação corrigida com sucesso:', data);
    },
    onError: (error) => {
      console.error('Erro ao corrigir redação:', error);
    },
  });
}

/**
 * Hook para buscar correção
 */
export function useBuscarCorrecao(correcaoId) {
  return useQuery({
    queryKey: ['correcao', correcaoId],
    queryFn: () => buscarCorrecao(correcaoId),
    enabled: !!correcaoId,
  });
}
