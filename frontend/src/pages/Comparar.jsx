import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeftRight, AlertCircle, TrendingUp, Award } from 'lucide-react';
import Container from '../components/layout/Container';
import Card, { CardBody, CardHeader } from '../components/ui/Card';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ErrorMessage from '../components/ui/ErrorMessage';
import { useCompararCorrecoes } from '../hooks/useCorrecao';
import { useListarCorrecoes } from '../hooks/useUsuario';
import { useAuth } from '../contexts/AuthContext';

export default function Comparar() {
  const { user } = useAuth();
  const [correcoesSelecionadas, setCorrecoesSelecionadas] = useState([]);
  const { data: correcoesData, isLoading: loadingCorrecoes } = useListarCorrecoes(user?.id);
  const { mutate: comparar, isPending, data: comparacao, error } = useCompararCorrecoes();

  const correcoes = correcoesData?.correcoes || [];

  const toggleSelecao = (correcaoId) => {
    if (correcoesSelecionadas.includes(correcaoId)) {
      setCorrecoesSelecionadas(correcoesSelecionadas.filter(id => id !== correcaoId));
    } else {
      if (correcoesSelecionadas.length < 5) {
        setCorrecoesSelecionadas([...correcoesSelecionadas, correcaoId]);
      }
    }
  };

  const handleComparar = () => {
    if (correcoesSelecionadas.length >= 2) {
      comparar(correcoesSelecionadas);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 800) return 'text-green-600';
    if (score >= 600) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loadingCorrecoes) {
    return <LoadingSpinner fullScreen size="xl" text="Carregando correções..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <Container>
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <ArrowLeftRight className="h-8 w-8 text-primary-600" />
            Comparar Redações
          </h1>
          <p className="mt-2 text-gray-600">
            Selecione de 2 a 5 redações para comparar lado a lado
          </p>
        </div>

        {/* Seleção de Correções */}
        {!comparacao && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card className="mb-6">
              <CardHeader>
                <h2 className="text-xl font-semibold text-gray-900">
                  Selecione as Redações ({correcoesSelecionadas.length}/5)
                </h2>
              </CardHeader>
              <CardBody>
                {correcoes.length === 0 ? (
                  <div className="text-center py-12">
                    <AlertCircle className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">
                      Você ainda não tem correções para comparar
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {correcoes.map((correcao) => (
                      <div
                        key={correcao.id}
                        onClick={() => toggleSelecao(correcao.id)}
                        className={`
                          p-4 border-2 rounded-lg cursor-pointer transition-all
                          ${correcoesSelecionadas.includes(correcao.id)
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-gray-200 hover:border-primary-300'
                          }
                        `}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <h3 className="font-medium text-gray-900">
                              {correcao.redacoes?.titulo || 'Sem título'}
                            </h3>
                            <p className="text-sm text-gray-500 mt-1">
                              {new Date(correcao.created_at).toLocaleDateString('pt-BR')}
                            </p>
                          </div>
                          <div className="text-right">
                            <div className={`text-2xl font-bold ${getScoreColor(correcao.score_total)}`}>
                              {correcao.score_total}
                            </div>
                            <div className="text-sm text-gray-500">pontos</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {correcoes.length > 0 && (
                  <div className="mt-6 flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                      {correcoesSelecionadas.length < 2 ? (
                        <span className="text-orange-600">
                          Selecione pelo menos 2 redações
                        </span>
                      ) : (
                        <span className="text-green-600">
                          ✓ {correcoesSelecionadas.length} redações selecionadas
                        </span>
                      )}
                    </div>
                    <Button
                      onClick={handleComparar}
                      disabled={correcoesSelecionadas.length < 2 || isPending}
                      loading={isPending}
                    >
                      Comparar Redações
                    </Button>
                  </div>
                )}
              </CardBody>
            </Card>
          </motion.div>
        )}

        {/* Erro */}
        {error && (
          <ErrorMessage
            title="Erro ao comparar"
            message={error.response?.data?.detail || error.message}
          />
        )}

        {/* Resultado da Comparação */}
        {comparacao && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Insights */}
            <Card>
              <CardHeader>
                <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-primary-600" />
                  Análise Comparativa
                </h2>
              </CardHeader>
              <CardBody>
                <div className="space-y-3">
                  {comparacao.analise.insights.map((insight, i) => (
                    <div key={i} className="flex items-start gap-2">
                      <Award className="h-5 w-5 text-primary-600 mt-0.5 flex-shrink-0" />
                      <p className="text-gray-700">{insight}</p>
                    </div>
                  ))}
                </div>

                <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Média dos Scores</div>
                    <div className="text-2xl font-bold text-gray-900 mt-1">
                      {Math.round(comparacao.analise.media_scores)}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Maior Score</div>
                    <div className="text-2xl font-bold text-green-600 mt-1">
                      {comparacao.analise.diferencas.max_score}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Menor Score</div>
                    <div className="text-2xl font-bold text-orange-600 mt-1">
                      {comparacao.analise.diferencas.min_score}
                    </div>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Tabela de Comparação */}
            <Card>
              <CardHeader>
                <h2 className="text-xl font-semibold text-gray-900">
                  Comparação Detalhada
                </h2>
              </CardHeader>
              <CardBody>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b-2 border-gray-200">
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Redação</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-900">Total</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-900">C1</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-900">C2</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-900">C3</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-900">C4</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-900">C5</th>
                      </tr>
                    </thead>
                    <tbody>
                      {comparacao.correcoes.map((corr, index) => {
                        const isMelhorScore = corr.id === comparacao.analise.melhor_score;
                        return (
                          <tr
                            key={corr.id}
                            className={`border-b border-gray-100 ${isMelhorScore ? 'bg-green-50' : ''}`}
                          >
                            <td className="py-3 px-4">
                              <div className="font-medium text-gray-900">
                                {corr.titulo || `Redação ${index + 1}`}
                              </div>
                              <div className="text-sm text-gray-500">
                                {new Date(corr.created_at).toLocaleDateString('pt-BR')}
                              </div>
                            </td>
                            <td className="text-center py-3 px-4">
                              <div className={`text-lg font-bold ${getScoreColor(corr.score_total)}`}>
                                {corr.score_total}
                                {isMelhorScore && (
                                  <Award className="inline h-4 w-4 ml-1 text-green-600" />
                                )}
                              </div>
                            </td>
                            <td className="text-center py-3 px-4">
                              <span className={corr.id === comparacao.analise.melhor_c1 ? 'font-bold text-green-600' : ''}>
                                {corr.c1}
                              </span>
                            </td>
                            <td className="text-center py-3 px-4">
                              <span className={corr.id === comparacao.analise.melhor_c2 ? 'font-bold text-green-600' : ''}>
                                {corr.c2}
                              </span>
                            </td>
                            <td className="text-center py-3 px-4">
                              <span className={corr.id === comparacao.analise.melhor_c3 ? 'font-bold text-green-600' : ''}>
                                {corr.c3}
                              </span>
                            </td>
                            <td className="text-center py-3 px-4">
                              <span className={corr.id === comparacao.analise.melhor_c4 ? 'font-bold text-green-600' : ''}>
                                {corr.c4}
                              </span>
                            </td>
                            <td className="text-center py-3 px-4">
                              <span className={corr.id === comparacao.analise.melhor_c5 ? 'font-bold text-green-600' : ''}>
                                {corr.c5}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </CardBody>
            </Card>

            {/* Botão Nova Comparação */}
            <div className="flex justify-center">
              <Button
                variant="outline"
                onClick={() => {
                  setCorrecoesSelecionadas([]);
                  window.location.reload();
                }}
              >
                Nova Comparação
              </Button>
            </div>
          </motion.div>
        )}
      </Container>
    </div>
  );
}
