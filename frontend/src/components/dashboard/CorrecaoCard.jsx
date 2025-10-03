import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FileText, Calendar, TrendingUp, Trash2 } from 'lucide-react';
import Badge from '../ui/Badge';

export default function CorrecaoCard({ correcao, index = 0, onDelete }) {
  const getNivelVariant = (score) => {
    if (score >= 900) return 'success';
    if (score >= 800) return 'info';
    if (score >= 700) return 'default';
    if (score >= 600) return 'warning';
    return 'danger';
  };

  const getNivelLabel = (score) => {
    if (score >= 900) return 'Excelente';
    if (score >= 800) return 'Muito Bom';
    if (score >= 700) return 'Bom';
    if (score >= 600) return 'Regular';
    return 'Precisa Melhorar';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const truncateText = (text, maxLength = 100) => {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 hover:shadow-md transition-all hover:border-primary-300 group"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <Link
            to={`/resultado/${correcao.id}`}
            className="text-lg font-semibold text-gray-900 hover:text-primary-600 transition-colors"
          >
            {correcao.redacoes?.titulo || 'Redação sem título'}
          </Link>

          <div className="flex items-center gap-3 mt-2 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              {formatDate(correcao.created_at)}
            </span>
            <span className="flex items-center gap-1">
              <FileText className="h-4 w-4" />
              {correcao.redacoes?.texto?.length || 0} caracteres
            </span>
          </div>
        </div>

        {/* Nota */}
        <div className="text-right ml-4">
          <div className="text-3xl font-bold text-primary-600">
            {correcao.score_total}
          </div>
          <div className="text-xs text-gray-500">de 1000</div>
        </div>
      </div>

      {/* Texto preview */}
      {correcao.redacoes?.texto && (
        <p className="text-sm text-gray-600 mb-4 line-clamp-2">
          {truncateText(correcao.redacoes.texto, 150)}
        </p>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex items-center gap-2">
          <Badge variant={getNivelVariant(correcao.score_total)} size="sm">
            {getNivelLabel(correcao.score_total)}
          </Badge>

          {correcao.confianca && (
            <Badge variant="default" size="sm">
              {Math.round(correcao.confianca * 100)}% confiança
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Link
            to={`/resultado/${correcao.id}`}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Ver detalhes →
          </Link>

          {onDelete && (
            <button
              onClick={() => onDelete(correcao.id)}
              className="p-2 text-gray-400 hover:text-red-600 transition-colors opacity-0 group-hover:opacity-100"
              title="Deletar correção"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Competências mini */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="grid grid-cols-5 gap-2">
          {[
            { label: 'C1', value: correcao.c1 },
            { label: 'C2', value: correcao.c2 },
            { label: 'C3', value: correcao.c3 },
            { label: 'C4', value: correcao.c4 },
            { label: 'C5', value: correcao.c5 }
          ].map((comp) => (
            <div key={comp.label} className="text-center">
              <div className="text-xs text-gray-500 mb-1">{comp.label}</div>
              <div className="text-sm font-semibold text-gray-900">{comp.value}</div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
