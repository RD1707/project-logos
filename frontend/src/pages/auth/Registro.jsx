import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, Lock, User, UserPlus, AlertCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import Container from '../../components/layout/Container';
import Card, { CardBody, CardHeader } from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import ErrorMessage from '../../components/ui/ErrorMessage';

export default function Registro() {
  const navigate = useNavigate();
  const { register, loading } = useAuth();

  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    senha: '',
    senhaConfirmacao: '',
    tipo: 'estudante'
  });
  const [errors, setErrors] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors([]);

    // Validações
    const newErrors = [];

    if (!formData.nome.trim()) {
      newErrors.push('Nome é obrigatório');
    }

    if (!formData.email.trim()) {
      newErrors.push('Email é obrigatório');
    }

    if (formData.senha.length < 6) {
      newErrors.push('Senha deve ter no mínimo 6 caracteres');
    }

    if (formData.senha !== formData.senhaConfirmacao) {
      newErrors.push('As senhas não coincidem');
    }

    if (newErrors.length > 0) {
      setErrors(newErrors);
      return;
    }

    // Registrar
    const result = await register({
      nome: formData.nome,
      email: formData.email,
      senha: formData.senha,
      tipo: formData.tipo
    });

    if (result.success) {
      navigate('/');
    } else {
      setErrors([result.error || 'Erro ao criar conta']);
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
              Crie sua conta
            </h1>
            <p className="text-gray-600">
              Comece a corrigir suas redações gratuitamente
            </p>
          </div>

          {/* Card de Registro */}
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold text-gray-900">
                Criar nova conta
              </h2>
            </CardHeader>

            <CardBody>
              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Nome */}
                <div>
                  <label htmlFor="nome" className="block text-sm font-medium text-gray-700 mb-2">
                    Nome completo
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <User className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      type="text"
                      id="nome"
                      name="nome"
                      value={formData.nome}
                      onChange={handleChange}
                      placeholder="João Silva"
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                      required
                      autoComplete="name"
                    />
                  </div>
                </div>

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

                {/* Tipo de Usuário */}
                <div>
                  <label htmlFor="tipo" className="block text-sm font-medium text-gray-700 mb-2">
                    Você é:
                  </label>
                  <select
                    id="tipo"
                    name="tipo"
                    value={formData.tipo}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                  >
                    <option value="estudante">Estudante</option>
                    <option value="professor">Professor</option>
                  </select>
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
                      autoComplete="new-password"
                      minLength={6}
                    />
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    Mínimo de 6 caracteres
                  </p>
                </div>

                {/* Confirmar Senha */}
                <div>
                  <label htmlFor="senhaConfirmacao" className="block text-sm font-medium text-gray-700 mb-2">
                    Confirmar senha
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Lock className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      type="password"
                      id="senhaConfirmacao"
                      name="senhaConfirmacao"
                      value={formData.senhaConfirmacao}
                      onChange={handleChange}
                      placeholder="••••••••"
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                      required
                      autoComplete="new-password"
                    />
                  </div>
                </div>

                {/* Erros */}
                {errors.length > 0 && (
                  <ErrorMessage
                    title="Erro ao criar conta"
                    message={
                      <ul className="list-disc list-inside space-y-1">
                        {errors.map((err, i) => (
                          <li key={i}>{err}</li>
                        ))}
                      </ul>
                    }
                  />
                )}

                {/* Termos */}
                <div className="text-xs text-gray-500">
                  Ao criar uma conta, você concorda com nossos{' '}
                  <Link to="/termos" className="text-primary-600 hover:text-primary-700">
                    Termos de Uso
                  </Link>{' '}
                  e{' '}
                  <Link to="/privacidade" className="text-primary-600 hover:text-primary-700">
                    Política de Privacidade
                  </Link>
                  .
                </div>

                {/* Botão de Submit */}
                <Button
                  type="submit"
                  size="lg"
                  className="w-full"
                  loading={loading}
                  disabled={loading}
                >
                  {loading ? (
                    'Criando conta...'
                  ) : (
                    <>
                      Criar conta
                      <UserPlus className="ml-2 h-5 w-5" />
                    </>
                  )}
                </Button>
              </form>

              {/* Link para Login */}
              <div className="mt-6 text-center">
                <p className="text-sm text-gray-600">
                  Já tem uma conta?{' '}
                  <Link
                    to="/login"
                    className="text-primary-600 hover:text-primary-700 font-semibold"
                  >
                    Fazer login
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
              <span>100% gratuito • Sem cartão de crédito</span>
            </div>
          </motion.div>
        </motion.div>
      </Container>
    </div>
  );
}
