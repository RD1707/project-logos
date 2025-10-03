import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, BookOpen } from 'lucide-react';
import axios from 'axios';

import Container from '../../components/layout/Container';
import TemaCard from '../../components/temas/TemaCard';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import ErrorMessage from '../../components/ui/ErrorMessage';
import Badge from '../../components/ui/Badge';
import { API_BASE_URL } from '../../utils/constants';

export default function Temas() {
  const [temas, setTemas] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [anoFiltro, setAnoFiltro] = useState('');
  const [categoriaFiltro, setCategoriaFiltro] = useState('');
  const [dificuldadeFiltro, setDificuldadeFiltro] = useState('');
  const [origemFiltro, setOrigemFiltro] = useState('');

  useEffect(() => {
    carregarDados();
  }, []);

  useEffect(() => {
    carregarTemas();
  }, [anoFiltro, categoriaFiltro, dificuldadeFiltro, origemFiltro]);

  const carregarDados = async () => {
    await Promise.all([
      carregarTemas(),
      carregarCategorias()
    ]);
  };

  const carregarTemas = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {};
      if (anoFiltro) params.ano = anoFiltro;
      if (categoriaFiltro) params.categoria = categoriaFiltro;
      if (dificuldadeFiltro) params.dificuldade = dificuldadeFiltro;
      if (origemFiltro) params.origem = origemFiltro;

      const response = await axios.get(`${API_BASE_URL}/temas`, { params });

      if (response.data.success) {
        setTemas(response.data.temas);
      }
    } catch (err) {
      console.error('Erro ao carregar temas:', err);
      setError('Erro ao carregar temas');
    } finally {
      setLoading(false);
    }
  };

  const carregarCategorias = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/temas/categorias`);
      if (response.data.success) {
        setCategorias(response.data.categorias);
      }
    } catch (err) {
      console.error('Erro ao carregar categorias:', err);
    }
  };

  const limparFiltros = () => {
    setAnoFiltro('');
    setCategoriaFiltro('');
    setDificuldadeFiltro('');
    setOrigemFiltro('');
    setSearchTerm('');
  };

  // Filtro de busca (client-side)
  const temasFiltrados = temas.filter(tema => {
    if (!searchTerm) return true;
    const termo = searchTerm.toLowerCase();
    return (
      tema.titulo?.toLowerCase().includes(termo) ||
      tema.descricao?.toLowerCase().includes(termo)
    );
  });

  // Anos únicos para filtro
  const anos = [...new Set(temas.filter(t => t.ano).map(t => t.ano))].sort((a, b) => b - a);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <Container>
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <BookOpen className="h-8 w-8 text-primary-600" />
            Temas ENEM
          </h1>
          <p className="mt-2 text-gray-600">
            Explore temas de redação ENEM de anos anteriores e pratique sua escrita
          </p>
        </div>

        {/* Busca e Filtros */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 mb-8">
          {/* Busca */}
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por título ou descrição..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Filtros */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Ano */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ano
              </label>
              <select
                value={anoFiltro}
                onChange={(e) => setAnoFiltro(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Todos os anos</option>
                {anos.map(ano => (
                  <option key={ano} value={ano}>{ano}</option>
                ))}
              </select>
            </div>

            {/* Categoria */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Categoria
              </label>
              <select
                value={categoriaFiltro}
                onChange={(e) => setCategoriaFiltro(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Todas as categorias</option>
                {categorias.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            {/* Dificuldade */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dificuldade
              </label>
              <select
                value={dificuldadeFiltro}
                onChange={(e) => setDificuldadeFiltro(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Todas</option>
                <option value="facil">Fácil</option>
                <option value="medio">Médio</option>
                <option value="dificil">Difícil</option>
              </select>
            </div>

            {/* Origem */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Origem
              </label>
              <select
                value={origemFiltro}
                onChange={(e) => setOrigemFiltro(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Todas</option>
                <option value="ENEM">ENEM Oficial</option>
                <option value="Treino">Treino</option>
              </select>
            </div>
          </div>

          {/* Filtros Ativos e Limpar */}
          {(anoFiltro || categoriaFiltro || dificuldadeFiltro || origemFiltro || searchTerm) && (
            <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sm text-gray-600">Filtros ativos:</span>
                {anoFiltro && <Badge variant="info" size="sm">{anoFiltro}</Badge>}
                {categoriaFiltro && <Badge variant="info" size="sm">{categoriaFiltro}</Badge>}
                {dificuldadeFiltro && <Badge variant="info" size="sm">{dificuldadeFiltro}</Badge>}
                {origemFiltro && <Badge variant="info" size="sm">{origemFiltro}</Badge>}
                {searchTerm && <Badge variant="info" size="sm">"{searchTerm}"</Badge>}
              </div>
              <button
                onClick={limparFiltros}
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Limpar filtros
              </button>
            </div>
          )}

          {/* Contador de resultados */}
          <div className="mt-4 text-sm text-gray-600">
            {temasFiltrados.length} {temasFiltrados.length === 1 ? 'tema encontrado' : 'temas encontrados'}
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" text="Carregando temas..." />
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <ErrorMessage title="Erro" message={error} />
        )}

        {/* Sem resultados */}
        {!loading && !error && temasFiltrados.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg p-12 text-center shadow-sm border border-gray-200"
          >
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Nenhum tema encontrado
            </h3>
            <p className="text-gray-600 mb-4">
              Tente ajustar os filtros para ver mais resultados
            </p>
            <button
              onClick={limparFiltros}
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Limpar todos os filtros
            </button>
          </motion.div>
        )}

        {/* Grid de Temas */}
        {!loading && !error && temasFiltrados.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {temasFiltrados.map((tema, index) => (
              <TemaCard key={tema.id} tema={tema} index={index} />
            ))}
          </div>
        )}
      </Container>
    </div>
  );
}
