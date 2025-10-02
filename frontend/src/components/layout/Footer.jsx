import { Heart, Github } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-1 text-sm text-gray-600">
            <span>Desenvolvido com</span>
            <Heart className="h-4 w-4 text-red-500 fill-current" />
            <span>para estudantes ENEM</span>
          </div>

          <div className="flex items-center gap-6">
            <p className="text-sm text-gray-500">
              © {currentYear} Redator ENEM. Todos os direitos reservados.
            </p>

            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-gray-700 transition-colors"
              aria-label="GitHub"
            >
              <Github className="h-5 w-5" />
            </a>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            Este sistema utiliza inteligência artificial para correção automática de redações.
            Os resultados são orientativos e devem ser validados por professores.
          </p>
        </div>
      </div>
    </footer>
  );
}
