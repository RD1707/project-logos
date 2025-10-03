import { motion } from 'framer-motion';

export default function SimpleLineChart({ data, title, height = 200 }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="flex items-center justify-center h-48 text-gray-400">
          Sem dados para exibir
        </div>
      </div>
    );
  }

  // Calcular dimensões
  const padding = 40;
  const width = 600;
  const chartHeight = height - padding * 2;
  const chartWidth = width - padding * 2;

  // Encontrar min e max
  const values = data.map(d => d.nota);
  const maxValue = Math.max(...values);
  const minValue = Math.min(...values);
  const range = maxValue - minValue || 1;

  // Criar pontos para o gráfico
  const points = data.map((d, i) => {
    const x = padding + (i / (data.length - 1 || 1)) * chartWidth;
    const y = padding + chartHeight - ((d.nota - minValue) / range) * chartHeight;
    return { x, y, nota: d.nota };
  });

  // Criar path do gráfico
  const pathData = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x},${p.y}`)
    .join(' ');

  // Criar path da área
  const areaData = `${pathData} L ${points[points.length - 1].x},${height - padding} L ${padding},${height - padding} Z`;

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full"
        style={{ maxHeight: height }}
      >
        {/* Grid horizontal */}
        {[0, 0.25, 0.5, 0.75, 1].map((percent, i) => {
          const y = padding + (1 - percent) * chartHeight;
          const value = Math.round(minValue + percent * range);
          return (
            <g key={i}>
              <line
                x1={padding}
                y1={y}
                x2={width - padding}
                y2={y}
                stroke="#E5E7EB"
                strokeWidth="1"
              />
              <text
                x={padding - 10}
                y={y + 4}
                textAnchor="end"
                className="text-xs fill-gray-500"
              >
                {value}
              </text>
            </g>
          );
        })}

        {/* Área sob a linha */}
        <motion.path
          d={areaData}
          fill="url(#gradient)"
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.2 }}
          transition={{ duration: 0.8 }}
        />

        {/* Linha principal */}
        <motion.path
          d={pathData}
          fill="none"
          stroke="#2563EB"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1, ease: "easeInOut" }}
        />

        {/* Pontos */}
        {points.map((point, i) => (
          <motion.g key={i}>
            <motion.circle
              cx={point.x}
              cy={point.y}
              r="4"
              fill="#2563EB"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.8 + i * 0.1 }}
            />
            <motion.circle
              cx={point.x}
              cy={point.y}
              r="6"
              fill="white"
              stroke="#2563EB"
              strokeWidth="2"
              opacity="0"
              whileHover={{ opacity: 1, scale: 1.2 }}
            />
            <title>{`Nota: ${point.nota}`}</title>
          </motion.g>
        ))}

        {/* Gradiente */}
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#2563EB" />
            <stop offset="100%" stopColor="#2563EB" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>

      {/* Legendas do eixo X (apenas primeira e última) */}
      <div className="flex justify-between mt-2 text-xs text-gray-500 px-10">
        <span>Início</span>
        <span>Mais recente</span>
      </div>
    </div>
  );
}
