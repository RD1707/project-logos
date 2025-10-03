import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import Home from './pages/Home';
import Corrigir from './pages/Corrigir';
import Resultado from './pages/Resultado';
import Login from './pages/auth/Login';
import Registro from './pages/auth/Registro';
import Dashboard from './pages/usuario/Dashboard';
import Historico from './pages/usuario/Historico';
import Perfil from './pages/usuario/Perfil';
import Temas from './pages/temas/Temas';
import Comparar from './pages/Comparar';

// Criar Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutos
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <div className="flex flex-col min-h-screen">
            <Header />

            <main className="flex-1">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/registro" element={<Registro />} />
                <Route path="/temas" element={<Temas />} />
                <Route path="/corrigir" element={<Corrigir />} />
                <Route path="/resultado/:id" element={<Resultado />} />

                {/* Rotas Protegidas */}
                <Route path="/dashboard" element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } />
                <Route path="/historico" element={
                  <ProtectedRoute>
                    <Historico />
                  </ProtectedRoute>
                } />
                <Route path="/perfil" element={
                  <ProtectedRoute>
                    <Perfil />
                  </ProtectedRoute>
                } />
                <Route path="/comparar" element={
                  <ProtectedRoute>
                    <Comparar />
                  </ProtectedRoute>
                } />
              </Routes>
            </main>

            <Footer />
          </div>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
