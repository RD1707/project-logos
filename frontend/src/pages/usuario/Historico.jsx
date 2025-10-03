import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import axios from 'axios';

import Container from '../../components/layout/Container';
import CorrecaoCard from '../../components/dashboard/CorrecaoCard';
import Button from '../../components/ui/Button';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import ErrorMessage from '../../components/ui/ErrorMessage';
import { API_BASE_URL } from '../../utils/constants';

export default function Historico() {
  const [correcoes, setCorrecoes] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [ordem, setOrdem] = useState('desc');

  const LIMIT = 10;

  useEffect(() => {
    carregarCorrecoes();
  }, [page, ordem]);

  const carregarCorrecoes = async () => {
    try {
      setLoading(true);
      setError(null);

      const offset = page * LIMIT;
      const response = await axios.get(`${API_BASE_URL}/usuario/correcoes`, {
        params: { limit: LIMIT, offset, ordem }
      });

      if (response.data.success) {
        setCorrecoes(response.data.correcoes);
        setPagination(response.data.pagination);
      }
    } catch (err) {
      console.error('Erro ao carregar histórico:', err);
      setError('Erro ao carregar histórico de correções');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (correcaoId) => {
    if (!confirm('Tem certeza que deseja deletar esta correção?')) {
      return;
    }

    try {
      await axios.delete(`${API_BASE_URL}/usuario/correcoes/${correcaoId}`);

      // Recarregar lista
      carregarCorrecoes();
    } catch (err) {
      console.error('Erro ao deletar:', err);
      alert('Erro ao deletar correção');
    }
  };

  const handleNextPage = () => {
    if (pagination?.has_more) {
      setPage(p => p + 1);
    }
  };

  const handlePrevPage = () => {
    if (page > 0) {
      setPage(p => p - 1);
    }
  };

  // Filtrar por termo de busca (client-side)
  const correcoesFiltradas = correcoes.filter(c => {
    if (!searchTerm) return true;
    const termo = searchTerm.toLowerCase();
    return (
      c.redacoes?.titulo?.toLowerCase().includes(termo) ||
      c.redacoes?.texto?.toLowerCase().includes(termo)
    );
  });

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <Container>
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Histórico de Correções
          </h1>
          <p className="mt-2 text-gray-600">
            Veja todas as suas redações corrigidas
          </p>
        </div>

        {/* Filtros e Busca */}
        <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Busca */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar por título ou conteúdo..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Ordenação */}
            <div className="flex items-center gap-2">
              <Filter className="h-5 w-5 text-gray-400" />
              <select
                value={ordem}
                onChange={(e) => {
                  setOrdem(e.target.value);
                  setPage(0);
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="desc">Mais recentes</option>
                <option value="asc">Mais antigas</option>
              </select>
            </div>
          </div>

          {/* Resultados */}
          {pagination && (
            <div className="mt-4 pt-4 border-t border-gray-100 text-sm text-gray-600">
              Exibindo {correcoesFiltradas.length} de {pagination.total} correções
            </div>
          )}
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" text="Carregando correções..." />
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <ErrorMessage title="Erro" message={error} />
        )}

        {/* Sem correções */}
        {!loading && !error && correcoesFiltradas.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg p-12 text-center shadow-sm border border-gray-200"
          >
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Nenhuma correção encontrada
            </h3>
            <p className="text-gray-600">
              {searchTerm
                ? 'Tente buscar com outros termos'
                : 'Você ainda não corrigiu nenhuma redação'}
            </p>
          </motion.div>
        )}

        {/* Lista de Correções */}
        {!loading && !error && correcoesFiltradas.length > 0 && (
          <div className="space-y-6">
            {correcoesFiltradas.map((correcao, index) => (
              <CorrecaoCard
                key={correcao.id}
                correcao={correcao}
                index={index}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}

        {/* Paginação */}
        {pagination && pagination.total > LIMIT && (
          <div className="mt-8 flex items-center justify-center gap-4">
            <Button
              variant="outline"
              onClick={handlePrevPage}
              disabled={page === 0}
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              Anterior
            </Button>

            <span className="text-sm text-gray-600">
              Página {page + 1} de {Math.ceil(pagination.total / LIMIT)}
            </span>

            <Button
              variant="outline"
              onClick={handleNextPage}
              disabled={!pagination.has_more}
            >
              Próxima
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        )}
      </Container>
    </div>
  );
}
