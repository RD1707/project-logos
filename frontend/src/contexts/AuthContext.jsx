import { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';
import { useLocalStorage } from '../hooks/useLocalStorage';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const navigate = useNavigate();

  // Estados
  const [user, setUser] = useState(null);
  const [tokens, setTokens] = useLocalStorage('auth_tokens', null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Configurar axios para incluir token em todas as requisições
  useEffect(() => {
    if (tokens?.access_token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access_token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [tokens]);

  // Carregar usuário ao iniciar (se tiver token)
  useEffect(() => {
    if (tokens?.access_token) {
      carregarUsuario();
    } else {
      setLoading(false);
    }
  }, []);

  // Carregar dados do usuário
  const carregarUsuario = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/auth/me`);

      if (response.data.success) {
        setUser(response.data.usuario);
        setError(null);
      }
    } catch (err) {
      console.error('Erro ao carregar usuário:', err);

      // Se token expirou, tentar renovar
      if (err.response?.status === 401 && tokens?.refresh_token) {
        const renovado = await tentarRenovarToken();
        if (!renovado) {
          // Se não conseguiu renovar, fazer logout
          await logout();
        }
      } else {
        setError('Erro ao carregar usuário');
        setTokens(null);
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  };

  // Registrar novo usuário
  const register = async (dados) => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.post(`${API_BASE_URL}/auth/register`, dados);

      if (response.data.success) {
        setUser(response.data.usuario);
        setTokens(response.data.tokens);
        return { success: true };
      }
    } catch (err) {
      console.error('Erro no registro:', err);
      const errorMessage = err.response?.data?.detail || 'Erro ao criar conta';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Login
  const login = async (email, senha) => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email,
        senha
      });

      if (response.data.success) {
        setUser(response.data.usuario);
        setTokens(response.data.tokens);
        return { success: true };
      }
    } catch (err) {
      console.error('Erro no login:', err);
      const errorMessage = err.response?.data?.detail || 'Erro ao fazer login';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Logout
  const logout = async () => {
    try {
      if (tokens?.refresh_token) {
        await axios.post(`${API_BASE_URL}/auth/logout`, {
          refresh_token: tokens.refresh_token
        });
      }
    } catch (err) {
      console.error('Erro no logout:', err);
    } finally {
      setUser(null);
      setTokens(null);
      setError(null);
      navigate('/');
    }
  };

  // Renovar token
  const tentarRenovarToken = async () => {
    try {
      if (!tokens?.refresh_token) {
        return false;
      }

      const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
        refresh_token: tokens.refresh_token
      });

      if (response.data) {
        setTokens(response.data);
        // Recarregar usuário com novo token
        await carregarUsuario();
        return true;
      }

      return false;
    } catch (err) {
      console.error('Erro ao renovar token:', err);
      return false;
    }
  };

  // Atualizar perfil
  const updateProfile = async (dados) => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.put(`${API_BASE_URL}/auth/me`, dados);

      if (response.data.success) {
        setUser(response.data.usuario);
        return { success: true };
      }
    } catch (err) {
      console.error('Erro ao atualizar perfil:', err);
      const errorMessage = err.response?.data?.detail || 'Erro ao atualizar perfil';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Alterar senha
  const changePassword = async (senhaAtual, senhaNova) => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.put(`${API_BASE_URL}/auth/me/senha`, {
        senha_atual: senhaAtual,
        senha_nova: senhaNova
      });

      if (response.data.success) {
        // Logout após trocar senha
        await logout();
        return { success: true };
      }
    } catch (err) {
      console.error('Erro ao alterar senha:', err);
      const errorMessage = err.response?.data?.detail || 'Erro ao alterar senha';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    tokens,
    loading,
    error,
    isAuthenticated: !!user,
    register,
    login,
    logout,
    updateProfile,
    changePassword,
    carregarUsuario
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Hook para usar o contexto
export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }

  return context;
}
