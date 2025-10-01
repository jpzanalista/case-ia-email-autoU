#!/usr/bin/env python3
"""
Script para executar a aplicação AutoU Classificador
"""

import os
import sys
import subprocess
from pathlib import Path

def check_env_file():
    """Verifica se o arquivo .env existe e está configurado"""
    if not Path(".env").exists():
        print("❌ Arquivo .env não encontrado!")
        print("Execute 'python setup.py' primeiro para configurar o projeto.")
        return False
    
    # Verificar se a chave da Gemini está configurada
    with open(".env", "r") as f:
        content = f.read()
        if "SUA_CHAVE_GEMINI_AQUI" in content:
            print("⚠️  IMPORTANTE: Configure sua chave da Gemini no arquivo .env")
            print("Edite o arquivo .env e substitua 'SUA_CHAVE_GEMINI_AQUI' pela sua chave real")
            return False
    
    return True

def run_flask_app():
    """Executa a aplicação Flask"""
    print("🚀 Iniciando aplicação Flask...")
    print("📱 Acesse: http://localhost:5000")
    print("⏹️  Para parar: Ctrl+C")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar aplicação: {e}")

def run_streamlit_app():
    """Executa a aplicação Streamlit"""
    print("🚀 Iniciando aplicação Streamlit...")
    print("📱 Acesse: http://localhost:8501")
    print("⏹️  Para parar: Ctrl+C")
    print("-" * 50)
    
    try:
        subprocess.run(["streamlit", "run", "streamlit_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar aplicação: {e}")

def main():
    """Função principal"""
    print("🎯 AutoU Classificador de Emails")
    print("=" * 40)
    
    # Verificar configuração
    if not check_env_file():
        return
    
    # Escolher versão da aplicação
    print("\nEscolha a versão da aplicação:")
    print("1. Flask (Interface web tradicional)")
    print("2. Streamlit (Interface moderna)")
    
    choice = input("\nDigite sua escolha (1 ou 2): ").strip()
    
    if choice == "1":
        run_flask_app()
    elif choice == "2":
        run_streamlit_app()
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    main()

