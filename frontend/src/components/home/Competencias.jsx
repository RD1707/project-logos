import { motion } from 'framer-motion';
import { COMPETENCIAS_ENEM } from '../../utils/constants';
import Card, { CardBody } from '../ui/Card';

export default function Competencias() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl sm:text-4xl font-bold text-gray-900"
          >
            5 Competências Avaliadas
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto"
          >
            Nossa IA avalia sua redação seguindo exatamente os mesmos critérios
            dos corretores do ENEM
          </motion.p>
        </div>

        {/* Grid de Competências */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {COMPETENCIAS_ENEM.map((comp, index) => (
            <motion.div
              key={comp.numero}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
            >
              <Card hover className="h-full">
                <CardBody className="space-y-4">
                  {/* Icon e Número */}
                  <div className="flex items-center gap-3">
                    <div className="text-4xl">{comp.icon}</div>
                    <div className="flex items-center gap-2">
                      <div className="bg-primary-100 text-primary-700 px-3 py-1 rounded-lg font-bold text-sm">
                        C{comp.numero}
                      </div>
                    </div>
                  </div>

                  {/* Título */}
                  <h3 className="text-lg font-semibold text-gray-900">
                    {comp.titulo}
                  </h3>

                  {/* Descrição */}
                  <p className="text-sm text-gray-600 leading-relaxed">
                    {comp.descricao}
                  </p>

                  {/* Nota máxima */}
                  <div className="pt-4 border-t border-gray-100">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Nota máxima:</span>
                      <span className="font-semibold text-primary-600">200 pontos</span>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </motion.div>
          ))}

          {/* Card do Score Total */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5 }}
          >
            <Card hover className="h-full bg-gradient-to-br from-primary-500 to-blue-600 border-none">
              <CardBody className="space-y-4 text-white">
                <div className="text-4xl">🏆</div>

                <h3 className="text-lg font-semibold">
                  Nota Total
                </h3>

                <p className="text-sm text-white/90 leading-relaxed">
                  A soma das 5 competências resulta na sua nota final,
                  de 0 a 1000 pontos.
                </p>

                <div className="pt-4 border-t border-white/20">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/90">Nota máxima:</span>
                    <span className="font-bold text-xl">1000 pontos</span>
                  </div>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
