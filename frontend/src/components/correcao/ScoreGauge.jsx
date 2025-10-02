import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getNivelNota, getEmojiPorNota } from '../../utils/helpers';

export default function ScoreGauge({ score, size = 'lg' }) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const nivel = getNivelNota(score);
  const emoji = getEmojiPorNota(score);

  // Animar score
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedScore(score);
    }, 100);

    return () => clearTimeout(timer);
  }, [score]);

  const sizes = {
    sm: { radius: 60, stroke: 8, textSize: 'text-2xl', labelSize: 'text-xs' },
    md: { radius: 80, stroke: 10, textSize: 'text-3xl', labelSize: 'text-sm' },
    lg: { radius: 100, stroke: 12, textSize: 'text-4xl', labelSize: 'text-base' },
  };

  const config = sizes[size];
  const circumference = 2 * Math.PI * config.radius;
  const progress = (animatedScore / 1000) * circumference;

  // Cores baseadas no nível
  const colors = {
    green: '#059669',
    blue: '#2563eb',
    cyan: '#0891b2',
    yellow: '#f59e0b',
    red: '#dc2626',
  };

  const strokeColor = colors[nivel.color];

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative">
        <svg
          width={(config.radius + config.stroke) * 2}
          height={(config.radius + config.stroke) * 2}
          className="transform -rotate-90"
        >
          {/* Background circle */}
          <circle
            cx={config.radius + config.stroke}
            cy={config.radius + config.stroke}
            r={config.radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth={config.stroke}
          />

          {/* Progress circle */}
          <motion.circle
            cx={config.radius + config.stroke}
            cy={config.radius + config.stroke}
            r={config.radius}
            fill="none"
            stroke={strokeColor}
            strokeWidth={config.stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference - progress }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
          />
        </svg>

        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="flex flex-col items-center"
          >
            <span className={`font-bold text-gray-900 ${config.textSize}`}>
              {Math.round(animatedScore)}
            </span>
            <span className={`text-gray-500 font-medium ${config.labelSize}`}>
              / 1000
            </span>
          </motion.div>
        </div>
      </div>

      {/* Level badge */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="flex items-center gap-2"
      >
        <span className="text-2xl">{emoji}</span>
        <span
          className="px-4 py-2 rounded-full font-semibold text-sm"
          style={{
            backgroundColor: `${strokeColor}20`,
            color: strokeColor
          }}
        >
          {nivel.label}
        </span>
      </motion.div>
    </div>
  );
}
