import { motion } from 'framer-motion';
import { FileText, Brain, CheckCircle } from 'lucide-react';

export default function ComoFunciona() {
  const steps = [
    {
      icon: FileText,
      title: 'Envie sua Redação',
      description: 'Digite ou cole o texto da sua redação no formulário. Mínimo 100 caracteres.',
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      icon: Brain,
      title: 'IA Analisa em Segundos',
      description: 'Nosso ensemble de modelos BERTimbau avalia todas as 5 competências simultaneamente.',
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      icon: CheckCircle,
      title: 'Receba Feedback Detalhado',
      description: 'Veja sua nota, pontos fortes, a melhorar e trechos destacados em cada competência.',
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
  ];

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl sm:text-4xl font-bold text-gray-900"
          >
            Como Funciona
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto"
          >
            3 passos simples para receber correção completa da sua redação
          </motion.p>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {/* Connecting lines (desktop) */}
          <div className="hidden md:block absolute top-16 left-1/4 right-1/4 h-0.5 bg-gradient-to-r from-blue-600 via-purple-600 to-green-600"></div>

          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.2 }}
                className="relative"
              >
                <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-200 h-full">
                  {/* Step number */}
                  <div className="absolute -top-4 -left-4 bg-gradient-to-br from-primary-600 to-blue-600 text-white w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg shadow-lg">
                    {index + 1}
                  </div>

                  {/* Icon */}
                  <div className={`${step.bgColor} ${step.color} w-16 h-16 rounded-2xl flex items-center justify-center mb-6`}>
                    <Icon className="h-8 w-8" />
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.6 }}
          className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6"
        >
          {[
            { label: 'Correção Instantânea', icon: '⚡' },
            { label: 'Sempre Aprendendo', icon: '🧠' },
            { label: '100% Gratuito', icon: '🎁' },
            { label: 'Dados Seguros', icon: '🔒' },
          ].map((feature, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl mb-2">{feature.icon}</div>
              <div className="text-sm font-medium text-gray-700">{feature.label}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
