"""
Script para criar toda a estrutura do backend FastAPI
"""
import os

# Estrutura de diretórios
DIRS = [
    "backend/core",
    "backend/models",
    "backend/schemas",
    "backend/routers",
    "backend/services",
    "backend/uploads"
]

# Criar diretórios
for dir_path in DIRS:
    os.makedirs(dir_path, exist_ok=True)
    # Criar __init__.py
    init_file = os.path.join(dir_path, "__init__.py")
    if not os.path.exists(init_file):
        open(init_file, 'w').close()

print("✅ Estrutura de diretórios criada!")
print("\nPróximos passos:")
print("1. cd backend")
print("2. python3 -m venv venv")
print("3. source venv/bin/activate")
print("4. pip install -r requirements.txt")
print("5. cp .env.example .env  # e edite as configurações")
print("6. python main.py")
