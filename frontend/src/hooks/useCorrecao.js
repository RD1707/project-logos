import { useMutation, useQuery } from '@tanstack/react-query';
import {
  corrigirRedacao,
  buscarCorrecao,
  compararCorrecoes,
  exportarPDF,
  criarCompartilhamento,
  acessarCompartilhado
} from '../services/api';

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

/**
 * Hook para comparar múltiplas correções
 */
export function useCompararCorrecoes() {
  return useMutation({
    mutationFn: compararCorrecoes,
  });
}

/**
 * Hook para exportar PDF
 */
export function useExportarPDF() {
  return useMutation({
    mutationFn: exportarPDF,
  });
}

/**
 * Hook para criar compartilhamento
 */
export function useCriarCompartilhamento() {
  return useMutation({
    mutationFn: ({ correcaoId, options }) => criarCompartilhamento(correcaoId, options),
  });
}

/**
 * Hook para acessar compartilhado
 */
export function useAcessarCompartilhado(token) {
  return useQuery({
    queryKey: ['compartilhado', token],
    queryFn: () => acessarCompartilhado(token),
    enabled: !!token,
  });
}
