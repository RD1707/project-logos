import { NIVEIS_NOTA } from './constants';

/**
 * Retorna informações sobre o nível da nota
 */
export function getNivelNota(score) {
  for (const [key, nivel] of Object.entries(NIVEIS_NOTA)) {
    if (score >= nivel.min && score <= nivel.max) {
      return nivel;
    }
  }
  return NIVEIS_NOTA.PRECISA_MELHORAR;
}

/**
 * Formata nota para exibição
 */
export function formatarNota(nota) {
  return Math.round(nota);
}

/**
 * Retorna cor baseada na nota (0-200 ou 0-1000)
 */
export function getCorPorNota(nota, max = 200) {
  const percentual = (nota / max) * 100;

  if (percentual >= 90) return 'text-green-600';
  if (percentual >= 80) return 'text-blue-600';
  if (percentual >= 70) return 'text-cyan-600';
  if (percentual >= 60) return 'text-yellow-600';
  return 'text-red-600';
}

/**
 * Retorna cor de fundo baseada na nota
 */
export function getBgCorPorNota(nota, max = 200) {
  const percentual = (nota / max) * 100;

  if (percentual >= 90) return 'bg-green-100';
  if (percentual >= 80) return 'bg-blue-100';
  if (percentual >= 70) return 'bg-cyan-100';
  if (percentual >= 60) return 'bg-yellow-100';
  return 'bg-red-100';
}

/**
 * Formata data para exibição
 */
export function formatarData(dateString) {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
}

/**
 * Conta palavras em um texto
 */
export function contarPalavras(texto) {
  if (!texto) return 0;
  return texto.trim().split(/\s+/).filter(word => word.length > 0).length;
}

/**
 * Conta caracteres em um texto
 */
export function contarCaracteres(texto) {
  if (!texto) return 0;
  return texto.length;
}

/**
 * Trunca texto
 */
export function truncarTexto(texto, maxLength = 100) {
  if (!texto || texto.length <= maxLength) return texto;
  return texto.substring(0, maxLength) + '...';
}

/**
 * Retorna emoji baseado na nota
 */
export function getEmojiPorNota(score) {
  if (score >= 900) return '🏆';
  if (score >= 800) return '🌟';
  if (score >= 700) return '😊';
  if (score >= 600) return '😐';
  return '😟';
}

/**
 * Calcula porcentagem
 */
export function calcularPorcentagem(valor, total) {
  if (total === 0) return 0;
  return Math.round((valor / total) * 100);
}

/**
 * Retorna mensagem de boas-vindas baseada na hora
 */
export function getMensagemBoasVindas() {
  const hora = new Date().getHours();

  if (hora < 12) return 'Bom dia';
  if (hora < 18) return 'Boa tarde';
  return 'Boa noite';
}

/**
 * Valida texto da redação
 */
export function validarTextoRedacao(texto) {
  const errors = [];

  if (!texto || texto.trim().length === 0) {
    errors.push('O texto da redação é obrigatório');
  } else {
    const length = texto.trim().length;

    if (length < 100) {
      errors.push('O texto deve ter no mínimo 100 caracteres');
    }

    if (length > 5000) {
      errors.push('O texto deve ter no máximo 5000 caracteres');
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Debounce function
 */
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
