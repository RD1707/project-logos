// Configurações da aplicação
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Competências do ENEM
export const COMPETENCIAS_ENEM = [
  {
    numero: 1,
    titulo: 'Domínio da Norma Culta',
    descricao: 'Demonstrar domínio da modalidade escrita formal da língua portuguesa.',
    icon: '📝'
  },
  {
    numero: 2,
    titulo: 'Compreensão do Tema',
    descricao: 'Compreender a proposta de redação e aplicar conceitos das várias áreas de conhecimento.',
    icon: '🎯'
  },
  {
    numero: 3,
    titulo: 'Seleção e Organização',
    descricao: 'Selecionar, relacionar, organizar e interpretar informações em defesa de um ponto de vista.',
    icon: '📊'
  },
  {
    numero: 4,
    titulo: 'Coesão Textual',
    descricao: 'Demonstrar conhecimento dos mecanismos linguísticos necessários para a construção da argumentação.',
    icon: '🔗'
  },
  {
    numero: 5,
    titulo: 'Proposta de Intervenção',
    descricao: 'Elaborar proposta de intervenção para o problema abordado, respeitando os direitos humanos.',
    icon: '💡'
  }
];

// Níveis de nota
export const NIVEIS_NOTA = {
  EXCELENTE: { min: 900, max: 1000, label: 'Excelente', color: 'green' },
  MUITO_BOM: { min: 800, max: 899, label: 'Muito Bom', color: 'blue' },
  BOM: { min: 700, max: 799, label: 'Bom', color: 'cyan' },
  REGULAR: { min: 600, max: 699, label: 'Regular', color: 'yellow' },
  PRECISA_MELHORAR: { min: 0, max: 599, label: 'Precisa Melhorar', color: 'red' }
};

// Cores por nível de confiança
export const CORES_CONFIANCA = {
  alta: 'green',
  média: 'yellow',
  baixa: 'red'
};

// Limites de texto
export const LIMITES_TEXTO = {
  MIN: 100,
  MAX: 5000,
  RECOMENDADO_MIN: 200,
  RECOMENDADO_MAX: 1500
};
