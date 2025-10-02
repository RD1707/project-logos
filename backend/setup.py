"""
Script de setup inicial do backend

Cria diretórios, copia .env, etc.
"""
import os
import shutil
from pathlib import Path

def setup():
    """Setup inicial do backend"""
    print("=" * 60)
    print(" Setup Inicial - Redator ENEM Backend")
    print("=" * 60)

    base_dir = Path(__file__).parent

    # 1. Criar diretórios necessários
    print("\n📁 Criando diretórios...")
    dirs = [
        "data/models",
        "data/cache",
        "logs"
    ]

    for dir_path in dirs:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")

    # 2. Copiar .env.example para .env se não existir
    env_example = base_dir / ".env.example"
    env_file = base_dir / ".env"

    if not env_file.exists():
        print("\n📝 Criando arquivo .env...")
        shutil.copy(env_example, env_file)
        print("  ✓ .env criado")
        print("  ⚠ IMPORTANTE: Edite o arquivo .env com suas credenciais Supabase!")
    else:
        print("\n✓ Arquivo .env já existe")

    # 3. Criar .gitkeep nos diretórios de data
    print("\n Criando .gitkeep...")
    gitkeep_dirs = [
        "data/models",
        "data/cache"
    ]

    for dir_path in gitkeep_dirs:
        gitkeep = base_dir / dir_path / ".gitkeep"
        gitkeep.touch(exist_ok=True)

    print("\n" + "=" * 60)
    print("✨ Setup concluído!")
    print("=" * 60)
    print("\n Próximos passos:")
    print("\n1. Editar .env com credenciais Supabase")
    print("2. Executar SQL em app/db/migrations.sql no Supabase")
    print("3. Preparar dataset: cd .. && python build_dataset.py")
    print("4. Treinar modelo: python training/train_initial.py")
    print("5. Iniciar API: python main.py")
    print("\n Veja README.md para instruções completas")
    print("=" * 60)


if __name__ == "__main__":
    setup()
