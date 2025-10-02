import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';

// Criar instância do axios
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 segundos (correção pode demorar)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para requisições
api.interceptors.request.use(
  (config) => {
    // Adicionar token se existir (futuro)
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para respostas
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Tratamento de erros global
    if (error.response) {
      // Erro com resposta do servidor
      console.error('Erro na resposta:', error.response.data);
    } else if (error.request) {
      // Erro sem resposta
      console.error('Erro na requisição:', error.request);
    } else {
      // Outro erro
      console.error('Erro:', error.message);
    }
    return Promise.reject(error);
  }
);

// ============= ENDPOINTS =============

/**
 * Corrige uma redação
 */
export const corrigirRedacao = async (data) => {
  try {
    const response = await api.post('/correcao/corrigir', {
      texto: data.texto,
      titulo: data.titulo || null,
      prompt_id: data.promptId || null,
      usuario_id: data.usuarioId || null,
    });

    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Busca uma correção por ID
 */
export const buscarCorrecao = async (correcaoId) => {
  try {
    const response = await api.get(`/correcao/correcao/${correcaoId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Envia feedback humano sobre uma correção
 */
export const enviarFeedback = async (correcaoId, feedbackData) => {
  try {
    const response = await api.post(`/correcao/feedback/${correcaoId}`, feedbackData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Busca informações do modelo
 */
export const buscarInfoModelo = async () => {
  try {
    const response = await api.get('/modelo/version');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Busca métricas do modelo
 */
export const buscarMetricas = async () => {
  try {
    const response = await api.get('/modelo/metrics');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Health check da API
 */
export const healthCheck = async () => {
  try {
    const response = await api.get('/modelo/health');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default api;
