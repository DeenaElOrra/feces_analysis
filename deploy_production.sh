#!/bin/bash

# Flora App - Production Deployment Helper Script
# Este script ajuda a preparar o projeto para deploy

set -e

echo "🚀 Flora App - Preparação para Deploy em Produção"
echo "================================================"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se estamos no diretório correto
if [ ! -d "backend" ] || [ ! -d "mobile-app" ]; then
    echo -e "${RED}❌ Erro: Execute este script na raiz do projeto${NC}"
    exit 1
fi

echo "📋 Checklist de Deploy"
echo "====================="
echo ""

# 1. Verificar backend
echo "1️⃣  Verificando Backend..."
if [ -f "backend/requirements.txt" ] && [ -f "backend/main.py" ]; then
    echo -e "${GREEN}✅ Backend OK${NC}"
else
    echo -e "${RED}❌ Arquivos do backend faltando${NC}"
    exit 1
fi

# 2. Verificar mobile app
echo "2️⃣  Verificando Mobile App..."
if [ -f "mobile-app/package.json" ] && [ -f "mobile-app/app.json" ]; then
    echo -e "${GREEN}✅ Mobile App OK${NC}"
else
    echo -e "${RED}❌ Arquivos do mobile app faltando${NC}"
    exit 1
fi

# 3. Verificar modelo de ML
echo "3️⃣  Verificando Modelo de ML..."
if [ -f "best_model_fe.h5" ]; then
    echo -e "${GREEN}✅ Modelo encontrado${NC}"
else
    echo -e "${YELLOW}⚠️  Modelo não encontrado (best_model_fe.h5)${NC}"
fi

echo ""
echo "🎯 Próximos Passos:"
echo "==================="
echo ""
echo "📖 Leia o guia completo: PRODUCTION_DEPLOY_GUIDE.md"
echo ""
echo "Opção A - Deploy Rápido (Recomendado):"
echo "  1. Crie conta em https://railway.app"
echo "  2. Suba o código do backend para GitHub"
echo "  3. Conecte Railway ao seu repositório"
echo "  4. Configure variáveis de ambiente"
echo "  5. Obtenha a URL do backend"
echo "  6. Atualize API_URL no mobile-app/src/services/api.js"
echo "  7. Instale EAS CLI: npm install -g eas-cli"
echo "  8. Faça build: cd mobile-app && eas build --platform android"
echo ""
echo "Opção B - Deploy Manual:"
echo "  1. Configure um servidor (AWS EC2, DigitalOcean, etc)"
echo "  2. Instale Python 3.11+"
echo "  3. Clone o repositório"
echo "  4. Execute: cd backend && pip install -r requirements.txt"
echo "  5. Execute: uvicorn main:app --host 0.0.0.0 --port 8000"
echo "  6. Configure nginx como reverse proxy"
echo "  7. Configure SSL com Let's Encrypt"
echo ""
echo "💡 Dica: Para começar rápido, use Railway (opção A)"
echo ""
echo "📞 Precisa de ajuda? Leia PRODUCTION_DEPLOY_GUIDE.md"
echo ""
