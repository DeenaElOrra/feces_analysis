#!/bin/bash
# Script de Backup Automático - Antes de Qualquer Mudança

echo "=============================================="
echo "🛡️  CRIANDO BACKUP COMPLETO DO PROJETO"
echo "=============================================="

# Data atual para nome do backup
BACKUP_DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups/backup_${BACKUP_DATE}"

# Criar diretório de backup
mkdir -p "$BACKUP_DIR"

echo ""
echo "📦 Fazendo backup de:"
echo "  - Modelo treinado (best_model_fe.h5)"
echo "  - Labels (labels.csv)"
echo "  - Dataset original (dataset/)"
echo ""

# 1. Backup do modelo
if [ -f "best_model_fe.h5" ]; then
    cp best_model_fe.h5 "$BACKUP_DIR/"
    echo "✓ Modelo salvo"
else
    echo "⚠️  Modelo não encontrado"
fi

# 2. Backup dos labels
if [ -f "labels.csv" ]; then
    cp labels.csv "$BACKUP_DIR/"
    echo "✓ Labels salvos"
else
    echo "⚠️  Labels não encontrados"
fi

# 3. Backup do dataset (opcional - pode ser grande)
if [ -d "dataset" ]; then
    echo "📁 Copiando dataset... (pode demorar)"
    cp -r dataset "$BACKUP_DIR/"
    echo "✓ Dataset salvo"
else
    echo "⚠️  Dataset não encontrado"
fi

# 4. Salvar informações sobre o backup
cat > "$BACKUP_DIR/backup_info.txt" << EOF
Backup criado em: $(date)
Modelo: best_model_fe.h5
Acurácia: 70.14%
Total de imagens: 211
Labels: labels.csv

Para restaurar:
1. cp $BACKUP_DIR/best_model_fe.h5 .
2. cp $BACKUP_DIR/labels.csv .
3. cp -r $BACKUP_DIR/dataset .
EOF

echo ""
echo "=============================================="
echo "✅ BACKUP COMPLETO!"
echo "=============================================="
echo "📂 Local: $BACKUP_DIR"
echo ""

# Listar tamanho
du -sh "$BACKUP_DIR"

echo ""
echo "Para restaurar tudo:"
echo "  ./restore_backup.sh $BACKUP_DIR"
echo ""
