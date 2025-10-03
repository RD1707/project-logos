import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Send, AlertCircle, BookOpen, X } from 'lucide-react';
import axios from 'axios';
import Container from '../components/layout/Container';
import Card, { CardBody, CardHeader } from '../components/ui/Card';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ErrorMessage from '../components/ui/ErrorMessage';
import { useCorrigirRedacao } from '../hooks/useCorrecao';
import { contarCaracteres, contarPalavras, validarTextoRedacao } from '../utils/helpers';

export default function Corrigir() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [texto, setTexto] = useState('');
  const [titulo, setTitulo] = useState('');
  const [errors, setErrors] = useState([]);
  const [temaSelecionado, setTemaSelecionado] = useState(null);
  const [loadingTema, setLoadingTema] = useState(false);

  const { mutate: corrigir, isPending, error } = useCorrigirRedacao();

  const caracteres = contarCaracteres(texto);
  const palavras = contarPalavras(texto);

  // Carregar tema se vier da URL
  useEffect(() => {
    const temaId = searchParams.get('tema');
    if (temaId) {
      carregarTema(temaId);
    }
  }, [searchParams]);

  const carregarTema = async (temaId) => {
    try {
      setLoadingTema(true);
      const response = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/temas/${temaId}`);

      if (response.data.success) {
        setTemaSelecionado(response.data.tema);
        setTitulo(response.data.tema.titulo);
      }
    } catch (err) {
      console.error('Erro ao carregar tema:', err);
    } finally {
      setLoadingTema(false);
    }
  };

  const removerTema = () => {
    setTemaSelecionado(null);
    setSearchParams({});
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Validar
    const validation = validarTextoRedacao(texto);
    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    setErrors([]);

    // Corrigir
    corrigir(
      {
        texto,
        titulo: titulo || null,
        prompt_id: temaSelecionado?.id || null,
      },
      {
        onSuccess: (data) => {
          // Redirecionar para página de resultado
          navigate(`/resultado/${data.correcao.id}`);
        },
      }
    );
  };

  const getCaracteresColor = () => {
    if (caracteres < 100) return 'text-red-600';
    if (caracteres > 5000) return 'text-red-600';
    if (caracteres < 200) return 'text-yellow-600';
    if (caracteres > 1500) return 'text-yellow-600';
    return 'text-green-600';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <Container size="sm">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Corrigir Redação
            </h1>
            <p className="mt-3 text-lg text-gray-600">
              Digite ou cole sua redação abaixo para receber correção completa
            </p>
          </div>

          {/* Tema Selecionado */}
          {temaSelecionado && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-primary-50 border-2 border-primary-200 rounded-lg p-6 mb-6"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  <div className="bg-primary-600 p-3 rounded-lg">
                    <BookOpen className="h-6 w-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-primary-900">Tema Selecionado</h3>
                      {temaSelecionado.ano && (
                        <span className="text-xs bg-primary-200 text-primary-800 px-2 py-1 rounded">
                          ENEM {temaSelecionado.ano}
                        </span>
                      )}
                    </div>
                    <p className="text-primary-800 font-medium mb-2">{temaSelecionado.titulo}</p>
                    <p className="text-sm text-primary-700">{temaSelecionado.descricao}</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={removerTema}
                  className="p-2 hover:bg-primary-200 rounded-lg transition-colors"
                  title="Remover tema"
                >
                  <X className="h-5 w-5 text-primary-700" />
                </button>
              </div>
            </motion.div>
          )}

          {/* Form */}
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold text-gray-900">
                Sua Redação
              </h2>
            </CardHeader>

            <CardBody>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Título (opcional) */}
                <div>
                  <label htmlFor="titulo" className="block text-sm font-medium text-gray-700 mb-2">
                    Título da Redação <span className="text-gray-400">(opcional)</span>
                  </label>
                  <input
                    type="text"
                    id="titulo"
                    value={titulo}
                    onChange={(e) => setTitulo(e.target.value)}
                    placeholder="Ex: Violência no Brasil: Causas e Soluções"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                    maxLength={200}
                  />
                </div>

                {/* Texto da redação */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label htmlFor="texto" className="block text-sm font-medium text-gray-700">
                      Texto da Redação <span className="text-red-500">*</span>
                    </label>
                    <div className="flex items-center gap-4 text-sm">
                      <span className={`font-medium ${getCaracteresColor()}`}>
                        {caracteres} caracteres
                      </span>
                      <span className="text-gray-500">
                        {palavras} palavras
                      </span>
                    </div>
                  </div>

                  <textarea
                    id="texto"
                    value={texto}
                    onChange={(e) => setTexto(e.target.value)}
                    placeholder="Digite ou cole o texto da sua redação aqui...

Lembre-se:
• Mínimo de 100 caracteres
• Recomendado entre 200 e 1500 caracteres
• Máximo de 5000 caracteres"
                    rows={16}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors resize-none font-mono text-sm leading-relaxed"
                    required
                  />

                  {/* Dicas */}
                  <div className="mt-2 flex items-start gap-2 text-sm text-gray-500">
                    <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <p>
                      Cole seu texto diretamente aqui. A análise leva cerca de 2-3 segundos.
                    </p>
                  </div>
                </div>

                {/* Errors */}
                {errors.length > 0 && (
                  <ErrorMessage
                    title="Erro na validação"
                    message={
                      <ul className="list-disc list-inside space-y-1">
                        {errors.map((err, i) => (
                          <li key={i}>{err}</li>
                        ))}
                      </ul>
                    }
                  />
                )}

                {/* API Error */}
                {error && (
                  <ErrorMessage
                    title="Erro ao corrigir"
                    message={error.response?.data?.detail || error.message || 'Erro desconhecido'}
                  />
                )}

                {/* Submit Button */}
                <div className="flex justify-end">
                  <Button
                    type="submit"
                    size="lg"
                    loading={isPending}
                    disabled={isPending || caracteres === 0}
                    className="w-full sm:w-auto"
                  >
                    {isPending ? (
                      'Analisando...'
                    ) : (
                      <>
                        Corrigir Redação
                        <Send className="ml-2 h-5 w-5" />
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardBody>
          </Card>

          {/* Loading State */}
          {isPending && (
            <LoadingSpinner
              fullScreen
              size="xl"
              text="Analisando sua redação com IA..."
            />
          )}
        </motion.div>
      </Container>
    </div>
  );
}
