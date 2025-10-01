#!/usr/bin/env python3
"""
Script de configuração para o projeto AutoU Classificador
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário. Versão atual:", sys.version)
        return False
    print(f"✅ Python {sys.version.split()[0]} detectado")
    return True

def create_virtual_environment():
    """Cria ambiente virtual"""
    if not Path("venv").exists():
        print("📦 Criando ambiente virtual...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Ambiente virtual criado")
    else:
        print("✅ Ambiente virtual já existe")

def install_dependencies():
    """Instala dependências"""
    print("📦 Instalando dependências...")
    
    # Determinar o comando pip correto
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        pip_cmd = "venv/bin/pip"
    
    subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
    print("✅ Dependências instaladas")

def create_env_file():
    """Cria arquivo .env se não existir"""
    if not Path(".env").exists():
        print("📝 Criando arquivo .env...")
        with open(".env", "w") as f:
            f.write("GEMINI_API_KEY=SUA_CHAVE_GEMINI_AQUI\n")
            f.write("FLASK_ENV=development\n")
            f.write("FLASK_DEBUG=True\n")
        print("✅ Arquivo .env criado")
        print("⚠️  IMPORTANTE: Edite o arquivo .env e adicione sua chave da Gemini!")
    else:
        print("✅ Arquivo .env já existe")

def create_directories():
    """Cria diretórios necessários"""
    directories = ["uploads", "static", "templates"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Diretórios criados")

def main():
    """Função principal de setup"""
    print("🚀 Configurando projeto AutoU Classificador...")
    print("=" * 50)
    
    # Verificar Python
    if not check_python_version():
        return
    
    # Criar ambiente virtual
    create_virtual_environment()
    
    # Instalar dependências
    try:
        install_dependencies()
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return
    
    # Criar arquivo .env
    create_env_file()
    
    # Criar diretórios
    create_directories()
    
    print("\n" + "=" * 50)
    print("🎉 Setup concluído!")
    print("\nPróximos passos:")
    print("1. Edite o arquivo .env e adicione sua chave da Gemini")
    print("2. Ative o ambiente virtual:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Execute a aplicação:")
    print("   python app.py")
    print("4. Acesse http://localhost:5000")

if __name__ == "__main__":
    main()

