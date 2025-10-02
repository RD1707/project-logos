import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle, TrendingUp } from 'lucide-react';
import Card, { CardBody } from '../ui/Card';
import Badge from '../ui/Badge';
import { getCorPorNota, getBgCorPorNota } from '../../utils/helpers';

export default function CompetenciaCard({ competencia, index }) {
  const { numero, nota, feedback, pontos_fortes, pontos_melhorar } = competencia;

  const notaColor = getCorPorNota(nota);
  const bgColor = getBgCorPorNota(nota);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      <Card hover>
        <CardBody className="space-y-4">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className={`${bgColor} p-3 rounded-lg`}>
                <span className="text-2xl font-bold text-gray-700">
                  C{numero}
                </span>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900">
                  Competência {numero}
                </h3>
                <p className="text-sm text-gray-500 mt-0.5">
                  {feedback.split('-')[0].trim()}
                </p>
              </div>
            </div>

            <div className="text-right">
              <div className={`text-3xl font-bold ${notaColor}`}>
                {nota}
              </div>
              <div className="text-sm text-gray-500 font-medium">
                / 200
              </div>
            </div>
          </div>

          {/* Feedback */}
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-700 leading-relaxed">
              {feedback}
            </p>
          </div>

          {/* Pontos Fortes */}
          {pontos_fortes && pontos_fortes.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <h4 className="text-sm font-semibold text-gray-900">
                  Pontos Fortes
                </h4>
              </div>
              <ul className="space-y-1.5">
                {pontos_fortes.map((ponto, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                    <span className="text-green-600 mt-0.5">✓</span>
                    <span>{ponto}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Pontos a Melhorar */}
          {pontos_melhorar && pontos_melhorar.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-4 w-4 text-blue-600" />
                <h4 className="text-sm font-semibold text-gray-900">
                  Pontos a Melhorar
                </h4>
              </div>
              <ul className="space-y-1.5">
                {pontos_melhorar.map((ponto, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                    <AlertCircle className="h-4 w-4 text-amber-500 flex-shrink-0 mt-0.5" />
                    <span>{ponto}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardBody>
      </Card>
    </motion.div>
  );
}
