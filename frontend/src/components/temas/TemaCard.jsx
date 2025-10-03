import { motion } from 'framer-motion';
import { Calendar, Tag, TrendingUp, FileText } from 'lucide-react';
import { Link } from 'react-router-dom';
import Badge from '../ui/Badge';
import Button from '../ui/Button';

export default function TemaCard({ tema, index = 0 }) {
  const getDificuldadeVariant = (dificuldade) => {
    if (dificuldade === 'facil') return 'success';
    if (dificuldade === 'medio') return 'warning';
    return 'danger';
  };

  const getDificuldadeLabel = (dificuldade) => {
    const labels = {
      facil: 'Fácil',
      medio: 'Médio',
      dificil: 'Difícil'
    };
    return labels[dificuldade] || dificuldade;
  };

  const getOrigemVariant = (origem) => {
    return origem === 'ENEM' ? 'info' : 'default';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 hover:shadow-md hover:border-primary-300 transition-all group"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-2">
            {tema.titulo}
          </h3>

          {/* Badges */}
          <div className="flex flex-wrap items-center gap-2 mt-3">
            {tema.ano && (
              <Badge variant="default" size="sm">
                <Calendar className="h-3 w-3 mr-1" />
                {tema.ano}
              </Badge>
            )}

            {tema.origem && (
              <Badge variant={getOrigemVariant(tema.origem)} size="sm">
                {tema.origem}
              </Badge>
            )}

            {tema.dificuldade && (
              <Badge variant={getDificuldadeVariant(tema.dificuldade)} size="sm">
                {getDificuldadeLabel(tema.dificuldade)}
              </Badge>
            )}

            {tema.categoria && (
              <Badge variant="default" size="sm">
                <Tag className="h-3 w-3 mr-1" />
                {tema.categoria}
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Descrição */}
      <p className="text-sm text-gray-600 leading-relaxed line-clamp-3 mb-4">
        {tema.descricao}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <Link to={`/corrigir?tema=${tema.id}`}>
          <Button size="sm" variant="outline" className="group-hover:bg-primary-50 group-hover:border-primary-600 group-hover:text-primary-600">
            <FileText className="h-4 w-4 mr-2" />
            Escrever redação
          </Button>
        </Link>
      </div>
    </motion.div>
  );
}
