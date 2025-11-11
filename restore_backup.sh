#!/bin/bash
# Script para Restaurar Backup

if [ -z "$1" ]; then
    echo "❌ Erro: Especifique o diretório do backup"
    echo ""
    echo "Backups disponíveis:"
    ls -lh backups/
    echo ""
    echo "Uso: ./restore_backup.sh backups/backup_YYYYMMDD_HHMMSS"
    exit 1
fi

BACKUP_DIR="$1"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Erro: Backup não encontrado: $BACKUP_DIR"
    exit 1
fi

echo "=============================================="
echo "🔄 RESTAURANDO BACKUP"
echo "=============================================="
echo "De: $BACKUP_DIR"
echo ""

# Perguntar confirmação
read -p "Tem certeza? Isso vai SUBSTITUIR os arquivos atuais (s/N): " confirm
if [ "$confirm" != "s" ] && [ "$confirm" != "S" ]; then
    echo "❌ Cancelado pelo usuário"
    exit 1
fi

echo ""
echo "📦 Restaurando arquivos..."

# Restaurar modelo
if [ -f "$BACKUP_DIR/best_model_fe.h5" ]; then
    cp "$BACKUP_DIR/best_model_fe.h5" .
    echo "✓ Modelo restaurado"
fi

# Restaurar labels
if [ -f "$BACKUP_DIR/labels.csv" ]; then
    cp "$BACKUP_DIR/labels.csv" .
    echo "✓ Labels restaurados"
fi

# Restaurar dataset
if [ -d "$BACKUP_DIR/dataset" ]; then
    rm -rf dataset
    cp -r "$BACKUP_DIR/dataset" .
    echo "✓ Dataset restaurado"
fi

echo ""
echo "=============================================="
echo "✅ BACKUP RESTAURADO COM SUCESSO!"
echo "=============================================="
echo ""
cat "$BACKUP_DIR/backup_info.txt" 2>/dev/null || echo "Info não disponível"
