#!/bin/bash

# Script para limpar e organizar o repositório git
# Execute este script para preparar o commit

set -e

echo "🧹 Limpando repositório git..."
echo ""

# 1. Remover lock se existir
if [ -f ".git/index.lock" ]; then
    echo "Removendo .git/index.lock..."
    rm -f .git/index.lock
fi

# 2. Resetar staging area
echo "Resetando staging area..."
git reset 2>/dev/null || true

# 3. Limpar arquivos não rastreados que estão no .gitignore
echo "Limpando arquivos ignorados..."
git clean -fdX

# 4. Adicionar apenas os arquivos importantes
echo ""
echo "📝 Adicionando arquivos importantes..."

# Backend
git add backend/

# Frontend mobile
git add mobile-app/

# Documentação
git add *.md

# Scripts de deployment
git add deploy_*.sh
git add *.sh

# Configurações
git add .gitignore
git add requirements.txt 2>/dev/null || true

# Labels (manter apenas os principais)
git add labels.csv 2>/dev/null || true
git add labels_v2_balanced.csv 2>/dev/null || true

echo ""
echo "✅ Repositório limpo!"
echo ""
echo "📊 Status atual:"
git status --short | head -20
echo ""
echo "💡 Próximos passos:"
echo "   1. Revisar os arquivos adicionados: git status"
echo "   2. Fazer commit: git commit -m 'Add backend, mobile app and deployment guides'"
echo "   3. Push para o GitHub: git push origin main"
echo ""
