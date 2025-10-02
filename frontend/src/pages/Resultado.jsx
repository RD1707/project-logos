import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, FileText, AlertTriangle, CheckCircle2, Share2 } from 'lucide-react';
import Container from '../components/layout/Container';
import Card, { CardBody, CardHeader } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ErrorMessage from '../components/ui/ErrorMessage';
import ScoreGauge from '../components/correcao/ScoreGauge';
import CompetenciaCard from '../components/correcao/CompetenciaCard';
import { useBuscarCorrecao } from '../hooks/useCorrecao';

export default function Resultado() {
  const { id } = useParams();
  const { data, isLoading, error } = useBuscarCorrecao(id);

  if (isLoading) {
    return <LoadingSpinner fullScreen size="xl" text="Carregando correção..." />;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <Container size="sm">
          <ErrorMessage
            title="Erro ao carregar correção"
            message={error.response?.data?.detail || error.message}
          />
          <div className="mt-6">
            <Link to="/corrigir">
              <Button>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Voltar
              </Button>
            </Link>
          </div>
        </Container>
      </div>
    );
  }

  const correcao = data?.correcao;

  if (!correcao) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <Container size="sm">
          <ErrorMessage title="Correção não encontrada" />
        </Container>
      </div>
    );
  }

  const getConfiancaVariant = (nivel) => {
    if (nivel === 'alta') return 'success';
    if (nivel === 'média') return 'warning';
    return 'danger';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <Container>
        {/* Header */}
        <div className="mb-8">
          <Link to="/corrigir">
            <Button variant="ghost" size="sm" className="mb-4">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Nova Correção
            </Button>
          </Link>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Resultado da Correção
              </h1>
              <p className="mt-2 text-gray-600">
                Análise completa da sua redação
              </p>
            </div>

            <Button variant="outline">
              <Share2 className="mr-2 h-4 w-4" />
              Compartilhar
            </Button>
          </div>
        </div>

        {/* Score Principal */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card className="mb-8">
            <CardBody className="py-12">
              <div className="flex flex-col md:flex-row items-center gap-12">
                {/* Gauge */}
                <div className="flex-shrink-0">
                  <ScoreGauge score={correcao.score_total} />
                </div>

                {/* Informações */}
                <div className="flex-1 space-y-6 text-center md:text-left">
                  {/* Feedback Geral */}
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                      {correcao.resumo_avaliacao}
                    </h2>
                    <p className="text-gray-600 leading-relaxed">
                      {correcao.feedback_geral}
                    </p>
                  </div>

                  {/* Badges */}
                  <div className="flex flex-wrap items-center gap-3 justify-center md:justify-start">
                    <Badge variant={getConfiancaVariant(correcao.confianca_nivel)} size="lg">
                      Confiança: {correcao.confianca_nivel} ({Math.round(correcao.confianca * 100)}%)
                    </Badge>

                    <Badge variant="info" size="lg">
                      <FileText className="mr-1 h-3 w-3" />
                      Modelo {correcao.modelo_version}
                    </Badge>

                    <Badge variant="default" size="lg">
                      ⏱️ {correcao.tempo_processamento?.toFixed(1)}s
                    </Badge>
                  </div>

                  {/* Aviso de baixa confiança */}
                  {correcao.confianca_nivel === 'baixa' && (
                    <div className="flex items-start gap-2 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                      <div className="text-sm text-yellow-800">
                        <strong>Atenção:</strong> Esta correção possui baixa confiança.
                        Recomendamos validação por um professor.
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </CardBody>
          </Card>
        </motion.div>

        {/* Competências */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Avaliação por Competência
          </h2>

          <div className="grid grid-cols-1 gap-6">
            {correcao.competencias.map((comp, index) => (
              <CompetenciaCard key={comp.numero} competencia={comp} index={index} />
            ))}
          </div>
        </div>

        {/* Análise Gramatical e Estrutural */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Análise Gramatical */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-gray-900">
                  Análise Gramatical
                </h3>
              </CardHeader>
              <CardBody className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-red-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-red-600">
                      {correcao.num_erros_ortografia}
                    </div>
                    <div className="text-sm text-red-700">Erros de Ortografia</div>
                  </div>

                  <div className="bg-orange-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {correcao.num_erros_gramatica}
                    </div>
                    <div className="text-sm text-orange-700">Erros de Gramática</div>
                  </div>
                </div>

                {correcao.erros_gramaticais?.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-sm text-gray-900 mb-2">
                      Principais Erros:
                    </h4>
                    <ul className="space-y-2">
                      {correcao.erros_gramaticais.slice(0, 5).map((erro, i) => (
                        <li key={i} className="text-sm text-gray-600 border-l-2 border-red-300 pl-3">
                          <strong className="text-red-600">{erro.tipo}:</strong> {erro.mensagem}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardBody>
            </Card>
          </motion.div>

          {/* Análise Estrutural */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-gray-900">
                  Análise Estrutural
                </h3>
              </CardHeader>
              <CardBody className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Introdução</span>
                    {correcao.analise_estrutura.tem_introducao ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    ) : (
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Desenvolvimento</span>
                    {correcao.analise_estrutura.tem_desenvolvimento ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    ) : (
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Conclusão</span>
                    {correcao.analise_estrutura.tem_conclusao ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    ) : (
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                    )}
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Parágrafos:</span>
                    <span className="font-medium">{correcao.analise_estrutura.num_paragrafos}</span>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Uso de Conectivos:</span>
                    <Badge variant="default" size="sm">
                      {correcao.analise_estrutura.uso_conectivos}
                    </Badge>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Coesão:</span>
                    <span className="font-medium">
                      {Math.round(correcao.analise_estrutura.coesao_score * 100)}%
                    </span>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Coerência:</span>
                    <span className="font-medium">
                      {Math.round(correcao.analise_estrutura.coerencia_score * 100)}%
                    </span>
                  </div>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center"
        >
          <Link to="/corrigir">
            <Button size="lg">
              Corrigir Outra Redação
            </Button>
          </Link>
        </motion.div>
      </Container>
    </div>
  );
}
