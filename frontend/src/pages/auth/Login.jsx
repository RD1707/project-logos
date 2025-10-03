import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, Lock, LogIn, AlertCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import Container from '../../components/layout/Container';
import Card, { CardBody, CardHeader } from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import ErrorMessage from '../../components/ui/ErrorMessage';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, loading } = useAuth();

  const [formData, setFormData] = useState({
    email: '',
    senha: ''
  });
  const [error, setError] = useState('');

  // Redirecionar para onde o usuário estava tentando acessar
  const from = location.state?.from?.pathname || '/';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validação básica
    if (!formData.email || !formData.senha) {
      setError('Preencha todos os campos');
      return;
    }

    // Fazer login
    const result = await login(formData.email, formData.senha);

    if (result.success) {
      navigate(from, { replace: true });
    } else {
      setError(result.error || 'Erro ao fazer login');
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-blue-50 py-12 px-4">
      <Container size="xs">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {/* Logo/Title */}
          <div className="text-center mb-8">
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
              Bem-vindo de volta!
            </h1>
            <p className="text-gray-600">
              Faça login para continuar corrigindo suas redações
            </p>
          </div>

          {/* Card de Login */}
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold text-gray-900">
                Entrar na sua conta
              </h2>
            </CardHeader>

            <CardBody>
              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Email */}
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Mail className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="seu@email.com"
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                      required
                      autoComplete="email"
                    />
                  </div>
                </div>

                {/* Senha */}
                <div>
                  <label htmlFor="senha" className="block text-sm font-medium text-gray-700 mb-2">
                    Senha
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Lock className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      type="password"
                      id="senha"
                      name="senha"
                      value={formData.senha}
                      onChange={handleChange}
                      placeholder="••••••••"
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                      required
                      autoComplete="current-password"
                    />
                  </div>
                </div>

                {/* Esqueceu a senha - TODO */}
                <div className="flex items-center justify-end">
                  <button
                    type="button"
                    className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                    disabled
                  >
                    Esqueceu a senha?
                  </button>
                </div>

                {/* Erro */}
                {error && (
                  <ErrorMessage
                    title="Erro ao fazer login"
                    message={error}
                  />
                )}

                {/* Botão de Submit */}
                <Button
                  type="submit"
                  size="lg"
                  className="w-full"
                  loading={loading}
                  disabled={loading}
                >
                  {loading ? (
                    'Entrando...'
                  ) : (
                    <>
                      Entrar
                      <LogIn className="ml-2 h-5 w-5" />
                    </>
                  )}
                </Button>
              </form>

              {/* Link para Registro */}
              <div className="mt-6 text-center">
                <p className="text-sm text-gray-600">
                  Não tem uma conta?{' '}
                  <Link
                    to="/registro"
                    className="text-primary-600 hover:text-primary-700 font-semibold"
                  >
                    Criar conta grátis
                  </Link>
                </p>
              </div>
            </CardBody>
          </Card>

          {/* Info */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="mt-6 text-center"
          >
            <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
              <AlertCircle className="h-4 w-4" />
              <span>Seus dados estão seguros e protegidos</span>
            </div>
          </motion.div>
        </motion.div>
      </Container>
    </div>
  );
}
