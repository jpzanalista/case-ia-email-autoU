#!/usr/bin/env python3
"""
Script para facilitar o deploy da aplicação AutoU Classificador
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_git_repo():
    """Verifica se estamos em um repositório Git"""
    if not Path(".git").exists():
        print("❌ Não é um repositório Git!")
        print("Execute 'git init' primeiro")
        return False
    print("✅ Repositório Git detectado")
    return True

def check_env_file():
    """Verifica se o arquivo .env está configurado"""
    if not Path(".env").exists():
        print("❌ Arquivo .env não encontrado!")
        return False
    
    with open(".env", "r") as f:
        content = f.read()
        if "SUA_CHAVE_GEMINI_AQUI" in content:
            print("⚠️  Configure sua chave da Gemini no arquivo .env")
            return False
    
    print("✅ Arquivo .env configurado")
    return True

def create_gitignore():
    """Cria/atualiza .gitignore"""
    gitignore_content = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
#Pipfile.lock

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Uploads directory
uploads/
*.pdf
*.txt

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content.strip())
    print("✅ .gitignore atualizado")

def commit_changes():
    """Faz commit das mudanças"""
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Deploy: AutoU Classificador de Emails"], check=True)
        print("✅ Mudanças commitadas")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao fazer commit")
        return False

def push_to_github():
    """Faz push para o GitHub"""
    try:
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Push para GitHub realizado")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao fazer push para GitHub")
        print("Verifique se o repositório remoto está configurado")
        return False

def show_deploy_instructions():
    """Mostra instruções de deploy"""
    print("\n" + "="*60)
    print("🚀 INSTRUÇÕES DE DEPLOY")
    print("="*60)
    
    print("\n1. RENDER (Recomendado para Flask):")
    print("   - Acesse: https://render.com")
    print("   - Conecte seu repositório GitHub")
    print("   - Crie um Web Service")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: gunicorn app:app")
    print("   - Adicione variável: GEMINI_API_KEY")
    
    print("\n2. STREAMLIT CLOUD (Para versão Streamlit):")
    print("   - Acesse: https://share.streamlit.io")
    print("   - Conecte seu repositório")
    print("   - Main file: streamlit_app.py")
    print("   - Adicione variável: GEMINI_API_KEY")
    
    print("\n3. HUGGING FACE SPACES (Para versão Gradio):")
    print("   - Acesse: https://huggingface.co/spaces")
    print("   - Crie um novo Space")
    print("   - SDK: Gradio")
    print("   - Upload dos arquivos")
    print("   - Adicione variável: GEMINI_API_KEY")
    
    print("\n4. HEROKU:")
    print("   - Instale Heroku CLI")
    print("   - heroku create autou-classificador")
    print("   - heroku config:set GEMINI_API_KEY=sua_chave")
    print("   - git push heroku main")

def main():
    """Função principal"""
    print("🚀 Preparando deploy da aplicação AutoU Classificador...")
    print("="*60)
    
    # Verificações
    if not check_git_repo():
        return
    
    if not check_env_file():
        print("\n⚠️  Configure sua chave da Gemini no arquivo .env antes de continuar")
        return
    
    # Preparar repositório
    create_gitignore()
    
    # Fazer commit e push
    if commit_changes():
        if push_to_github():
            print("\n✅ Repositório preparado para deploy!")
            show_deploy_instructions()
        else:
            print("\n⚠️  Repositório preparado, mas push falhou")
            print("Configure o repositório remoto manualmente")
            show_deploy_instructions()
    else:
        print("\n⚠️  Erro ao preparar repositório")
        show_deploy_instructions()

if __name__ == "__main__":
    main()
