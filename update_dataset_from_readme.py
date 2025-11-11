#!/usr/bin/env python3
"""
Atualizar labels.csv com novas imagens do README.md
"""

import pandas as pd
import os
from pathlib import Path
import re

print("="*70)
print("📝 ATUALIZANDO DATASET COM NOVAS IMAGENS DO README")
print("="*70)

# Ler README
with open('README.md', 'r', encoding='utf-8') as f:
    readme_content = f.read()

# Extrair linhas com imagens
pattern = r'img:\s*dataset/(.+?)\s+tipo:(\d+)'
matches = re.findall(pattern, readme_content)

print(f"\n✓ Encontradas {len(matches)} imagens no README")

# Carregar CSV atual
df_current = pd.read_csv('labels.csv')
print(f"✓ CSV atual tem {len(df_current)} imagens")

# Criar lista de novas imagens
new_images = []
existing_filenames = set(df_current['filename'].values)

for filename, tipo in matches:
    # Verificar se já existe
    if filename not in existing_filenames:
        # Verificar se arquivo existe
        filepath = Path('dataset') / filename
        if filepath.exists():
            new_images.append({
                'filename': filename,
                'bristol_type': int(tipo)
            })
            print(f"  ✓ Nova: {filename} (Tipo {tipo})")
        else:
            print(f"  ⚠️  Arquivo não encontrado: {filename}")
    else:
        print(f"  ⏭  Já existe: {filename}")

print(f"\n📊 RESUMO:")
print(f"  Total no README: {len(matches)} imagens")
print(f"  Já existentes: {len(matches) - len(new_images)} imagens")
print(f"  NOVAS para adicionar: {len(new_images)} imagens")

if len(new_images) == 0:
    print("\n✅ Nenhuma imagem nova para adicionar!")
    print("   Todas as imagens do README já estão no labels.csv")
else:
    # Criar DataFrame com novas imagens
    df_new = pd.DataFrame(new_images)

    # Combinar com CSV atual
    df_updated = pd.concat([df_current, df_new], ignore_index=True)

    # Ordenar por tipo Bristol
    df_updated = df_updated.sort_values('bristol_type').reset_index(drop=True)

    # Salvar backup do CSV antigo
    backup_file = 'labels_backup_before_update.csv'
    df_current.to_csv(backup_file, index=False)
    print(f"\n💾 Backup criado: {backup_file}")

    # Salvar CSV atualizado
    df_updated.to_csv('labels.csv', index=False)
    print(f"✓ CSV atualizado salvo: labels.csv")

    # Mostrar distribuição
    print(f"\n📈 DISTRIBUIÇÃO ATUALIZADA:")
    print(f"  Total de imagens: {len(df_updated)}")
    print(f"\n  Por tipo Bristol:")
    for tipo in range(1, 8):
        count_old = len(df_current[df_current['bristol_type'] == tipo])
        count_new = len(df_updated[df_updated['bristol_type'] == tipo])
        diff = count_new - count_old
        print(f"    Tipo {tipo}: {count_old} → {count_new} (+{diff})")

    print(f"\n📊 Distribuição detalhada:")
    print(df_updated['bristol_type'].value_counts().sort_index())

print("\n" + "="*70)
print("✅ ATUALIZAÇÃO COMPLETA!")
print("="*70)

# Verificar duplicatas
duplicates = df_updated[df_updated.duplicated(subset=['filename'], keep=False)]
if len(duplicates) > 0:
    print(f"\n⚠️  ATENÇÃO: {len(duplicates)} imagens duplicadas encontradas!")
    print(duplicates)
else:
    print(f"\n✓ Sem duplicatas - dataset limpo!")

print(f"\n📁 Arquivo pronto para treino: labels.csv ({len(df_updated)} imagens)")
print("\n")
