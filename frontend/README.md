# 🎨 Redator ENEM - Frontend

Interface web moderna e minimalista para o sistema de correção automática de redações ENEM.

## 🚀 Tecnologias

- **React 18** - Biblioteca UI
- **Vite** - Build tool ultrarrápido
- **Tailwind CSS** - Estilização utilitária
- **React Router** - Navegação SPA
- **React Query** - Gerenciamento de estado e cache
- **Framer Motion** - Animações suaves
- **Lucide React** - Ícones minimalistas
- **Axios** - Cliente HTTP
- **Fonte Inter** - Tipografia moderna (Google Fonts)

## 📦 Instalação

```bash
cd frontend

# Instalar dependências
npm install

# Copiar variáveis de ambiente
cp .env.example .env

# Editar .env e configurar URL da API
# VITE_API_URL=http://localhost:8000/api/v1
```

## 🏃 Executar

```bash
# Modo desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview
```

Acesse: http://localhost:3000

## 📁 Estrutura do Projeto

```
frontend/
├── public/             # Arquivos estáticos
├── src/
│   ├── components/     # Componentes React
│   │   ├── layout/    # Header, Footer, Container
│   │   ├── ui/        # Button, Badge, Card, etc
│   │   ├── correcao/  # ScoreGauge, CompetenciaCard
│   │   └── home/      # Hero, Competencias, ComoFunciona
│   ├── pages/         # Páginas principais
│   │   ├── Home.jsx
│   │   ├── Corrigir.jsx
│   │   └── Resultado.jsx
│   ├── services/      # API client
│   │   └── api.js
│   ├── hooks/         # Custom hooks
│   │   └── useCorrecao.js
│   ├── utils/         # Helpers e constantes
│   │   ├── helpers.js
│   │   └── constants.js
│   ├── App.jsx        # App principal com Router
│   ├── main.jsx       # Entry point
│   └── index.css      # Estilos globais
├── index.html         # HTML template
├── package.json       # Dependências
├── vite.config.js     # Config Vite
├── tailwind.config.js # Config Tailwind
└── README.md          # Este arquivo
```

## 🎨 Design System

### Cores

- **Primary**: Azul (#2563eb)
- **Success**: Verde (#059669)
- **Warning**: Amarelo (#f59e0b)
- **Danger**: Vermelho (#dc2626)
- **Gray**: Tons de cinza para texto e backgrounds

### Tipografia

- **Fonte**: Inter (Google Fonts)
- **Weights**: 400 (regular), 600 (semibold), 700 (bold)

### Componentes

- **Button** - 5 variantes (primary, secondary, outline, ghost, danger)
- **Badge** - 6 variantes de cor
- **Card** - Com Header, Body e Footer
- **LoadingSpinner** - Com suporte a fullscreen
- **ErrorMessage** - 3 variantes (error, warning, info)

## 📄 Páginas

### Home (Landing)
- Hero section com CTA
- Explicação das 5 competências
- Como funciona (3 passos)
- Estatísticas

### Corrigir
- Formulário de redação
- Validação em tempo real
- Contador de caracteres/palavras
- Loading state durante correção

### Resultado
- Score gauge animado
- 5 cards de competências detalhados
- Análise gramatical e estrutural
- Badges de confiança e tempo
- Compartilhamento

## 🔌 Integração com Backend

O frontend se comunica com o backend via:

```javascript
// Corrigir redação
POST /api/v1/correcao/corrigir
Body: { texto, titulo?, prompt_id?, usuario_id? }

// Buscar correção
GET /api/v1/correcao/correcao/:id

// Informações do modelo
GET /api/v1/modelo/version
GET /api/v1/modelo/metrics
GET /api/v1/modelo/health
```

## ✨ Features

- ✅ Design minimalista e elegante
- ✅ Totalmente responsivo (mobile-first)
- ✅ Animações suaves com Framer Motion
- ✅ Loading states e tratamento de erros
- ✅ Cache inteligente com React Query
- ✅ Validação de formulários
- ✅ Feedback visual em tempo real
- ✅ Acessível (ARIA labels)
- ✅ Performance otimizada

## 🎯 Fluxo de Uso

1. **Landing Page** - Usuário conhece o sistema
2. **Corrigir** - Usuário envia redação
3. **Loading** - Sistema processa (2-3s)
4. **Resultado** - Visualiza correção completa
   - Score total com gauge
   - 5 competências detalhadas
   - Erros gramaticais
   - Análise estrutural
5. **Nova Correção** - Botão para corrigir outra

## 🚢 Deploy

### Build

```bash
npm run build
```

O build gera arquivos estáticos em `dist/` prontos para deploy.

### Opções de Deploy

- **Vercel** (recomendado)
  ```bash
  npm i -g vercel
  vercel
  ```

- **Netlify**
  ```bash
  npm run build
  # Arraste pasta dist/ para Netlify
  ```

- **Docker**
  ```dockerfile
  FROM node:18-alpine AS builder
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci
  COPY . .
  RUN npm run build

  FROM nginx:alpine
  COPY --from=builder /app/dist /usr/share/nginx/html
  ```

## 🔧 Configuração de Proxy

O Vite está configurado para fazer proxy das requisições `/api` para o backend:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

## 📱 Responsividade

O design é **mobile-first** e se adapta a todos os tamanhos de tela:

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

Todos os componentes são testados em diferentes resoluções.

## 🎨 Customização

### Cores

Edite `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: { /* suas cores */ }
    }
  }
}
```

### Fonte

Edite `index.html` para trocar a fonte:

```html
<link href="https://fonts.googleapis.com/css2?family=SuaFonte&display=swap" rel="stylesheet">
```

E `tailwind.config.js`:

```javascript
fontFamily: {
  sans: ['SuaFonte', 'sans-serif']
}
```

## 🐛 Troubleshooting

### Erro de CORS

Certifique-se de que o backend permite requisições de `http://localhost:3000`:

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    ...
)
```

### Erro de conexão com API

Verifique se:
1. Backend está rodando (`http://localhost:8000`)
2. `.env` tem a URL correta
3. Proxy do Vite está configurado

## 📄 Licença

MIT

---

**Desenvolvido com ❤️ usando React e Tailwind CSS**
