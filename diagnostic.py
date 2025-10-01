# diagnostic.py
import os

print("=== ESTRUTURA DE DIRETÓRIOS NO RENDER ===")
print(f"Diretório atual: {os.getcwd()}")

print("\n=== LISTANDO ARQUIVOS NA RAIZ ===")
for item in os.listdir('.'):
    print(f" - {item}")

print("\n=== PROCURANDO app.py ===")
for root, dirs, files in os.walk('.'):
    if 'app.py' in files:
        print(f"Encontrado: {os.path.join(root, 'app.py')}")

print("\n=== CONTEÚDO DO DIRETÓRIO ATUAL ===")
for item in os.listdir('.'):
    full_path = os.path.join('.', item)
    if os.path.isfile(full_path):
        print(f"Arquivo: {item}")
    else:
        print(f"Diretório: {item}/")