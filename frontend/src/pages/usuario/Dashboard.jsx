import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FileText, TrendingUp, Award, BarChart3, Plus, AlertCircle } from 'lucide-react';
import axios from 'axios';

import { useAuth } from '../../contexts/AuthContext';
import Container from '../../components/layout/Container';
import StatCard from '../../components/dashboard/StatCard';
import SimpleLineChart from '../../components/dashboard/SimpleLineChart';
import CorrecaoCard from '../../components/dashboard/CorrecaoCard';
import Button from '../../components/ui/Button';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import ErrorMessage from '../../components/ui/ErrorMessage';
import { API_BASE_URL } from '../../utils/constants';

export default function Dashboard() {
  const { user } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    carregarDashboard();
  }, []);

  const carregarDashboard = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.get(`${API_BASE_URL}/usuario/dashboard`);

      if (response.data.success) {
        setDashboard(response.data.dashboard);
      }
    } catch (err) {
      console.error('Erro ao carregar dashboard:', err);
      setError('Erro ao carregar dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner fullScreen size="xl" text="Carregando dashboard..." />;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <Container>
          <ErrorMessage title="Erro" message={error} />
        </Container>
      </div>
    );
  }

  const stats = dashboard?.estatisticas || {};
  const ultimas = dashboard?.ultimas_correcoes || [];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <Container>
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Olá, {user?.nome?.split(' ')[0]}! 👋
          </h1>
          <p className="mt-2 text-gray-600">
            Aqui está um resumo do seu progresso
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total de Redações"
            value={stats.total_redacoes || 0}
            icon={FileText}
            color="primary"
            index={0}
          />

          <StatCard
            title="Média Geral"
            value={stats.media_geral || 0}
            subtitle="de 1000 pontos"
            icon={BarChart3}
            color="blue"
            index={1}
          />

          <StatCard
            title="Melhor Nota"
            value={stats.melhor_nota || 0}
            icon={Award}
            color="green"
            index={2}
          />

          <StatCard
            title="Progresso"
            value={stats.total_redacoes > 0 ? 'Ativo' : 'Inativo'}
            subtitle={stats.total_redacoes > 0 ? 'Continue assim!' : 'Comece agora'}
            icon={TrendingUp}
            color="purple"
            index={3}
          />
        </div>

        {/* Sem redações ainda */}
        {stats.total_redacoes === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg p-12 text-center shadow-sm border border-gray-200 mb-8"
          >
            <div className="max-w-md mx-auto">
              <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <FileText className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Comece sua jornada
              </h3>
              <p className="text-gray-600 mb-6">
                Você ainda não corrigiu nenhuma redação. Que tal começar agora?
              </p>
              <Link to="/corrigir">
                <Button size="lg">
                  <Plus className="mr-2 h-5 w-5" />
                  Corrigir minha primeira redação
                </Button>
              </Link>
            </div>
          </motion.div>
        )}

        {/* Gráfico de Evolução */}
        {stats.evolucao && stats.evolucao.length > 1 && (
          <div className="mb-8">
            <SimpleLineChart
              data={stats.evolucao}
              title="Evolução das Notas"
            />
          </div>
        )}

        {/* Médias por Competência */}
        {stats.medias_competencias && stats.total_redacoes > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 mb-8"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-6">
              Médias por Competência
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {Object.entries(stats.medias_competencias).map(([key, value], index) => (
                <div key={key} className="text-center">
                  <div className="text-sm text-gray-600 mb-2">
                    Competência {index + 1}
                  </div>
                  <div className="text-3xl font-bold text-primary-600 mb-1">
                    {Math.round(value)}
                  </div>
                  <div className="text-xs text-gray-500">de 200</div>

                  {/* Barra de progresso */}
                  <div className="mt-3 bg-gray-200 rounded-full h-2 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(value / 200) * 100}%` }}
                      transition={{ delay: 0.5 + index * 0.1, duration: 0.8 }}
                      className="h-full bg-primary-600 rounded-full"
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Últimas Correções */}
        {ultimas.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                Últimas Correções
              </h2>
              <Link to="/historico">
                <Button variant="ghost">
                  Ver todas →
                </Button>
              </Link>
            </div>

            <div className="grid grid-cols-1 gap-6">
              {ultimas.map((correcao, index) => (
                <CorrecaoCard
                  key={correcao.id}
                  correcao={correcao}
                  index={index}
                />
              ))}
            </div>
          </div>
        )}

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-8 text-center"
        >
          <Link to="/corrigir">
            <Button size="lg">
              <Plus className="mr-2 h-5 w-5" />
              Corrigir Nova Redação
            </Button>
          </Link>
        </motion.div>
      </Container>
    </div>
  );
}
