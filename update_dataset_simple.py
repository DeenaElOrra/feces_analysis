#!/usr/bin/env python3
"""
Atualizar labels.csv com novas imagens do README.md (versão simples sem pandas)
"""

import os
import re
import csv
from pathlib import Path
from collections import Counter

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
current_images = []
with open('labels.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        current_images.append(row)

print(f"✓ CSV atual tem {len(current_images)} imagens")

# Criar set de filenames existentes
existing_filenames = {img['filename'] for img in current_images}

# Identificar novas imagens
new_images = []
skipped_exist = 0
skipped_missing = 0

for filename, tipo in matches:
    if filename not in existing_filenames:
        # Verificar se arquivo existe
        filepath = Path('dataset') / filename
        if filepath.exists():
            new_images.append({
                'filename': filename,
                'bristol_type': tipo
            })
            print(f"  ✓ Nova: {filename} (Tipo {tipo})")
        else:
            print(f"  ⚠️  Arquivo não encontrado: {filename}")
            skipped_missing += 1
    else:
        skipped_exist += 1

print(f"\n📊 RESUMO:")
print(f"  Total no README: {len(matches)} imagens")
print(f"  Já existentes: {skipped_exist} imagens")
print(f"  Arquivos não encontrados: {skipped_missing} imagens")
print(f"  NOVAS para adicionar: {len(new_images)} imagens")

if len(new_images) == 0:
    print("\n✅ Nenhuma imagem nova para adicionar!")
    print("   Todas as imagens do README já estão no labels.csv")
else:
    # Criar backup
    backup_file = 'labels_backup_before_update.csv'
    with open(backup_file, 'w', encoding='utf-8') as f_out:
        with open('labels.csv', 'r', encoding='utf-8') as f_in:
            f_out.write(f_in.read())
    print(f"\n💾 Backup criado: {backup_file}")

    # Combinar imagens antigas e novas
    all_images = current_images + new_images

    # Contar distribuição antes
    count_before = Counter(img['bristol_type'] for img in current_images)

    # Contar distribuição depois
    count_after = Counter(img['bristol_type'] for img in all_images)

    # Salvar CSV atualizado
    with open('labels.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['filename', 'bristol_type'])
        writer.writeheader()
        writer.writerows(all_images)

    print(f"✓ CSV atualizado salvo: labels.csv")

    # Mostrar distribuição
    print(f"\n📈 DISTRIBUIÇÃO ATUALIZADA:")
    print(f"  Total de imagens: {len(current_images)} → {len(all_images)} (+{len(new_images)})")
    print(f"\n  Por tipo Bristol:")
    for tipo in ['1', '2', '3', '4', '5', '6', '7']:
        before = count_before.get(tipo, 0)
        after = count_after.get(tipo, 0)
        diff = after - before
        if diff > 0:
            print(f"    Tipo {tipo}: {before} → {after} (+{diff})")
        else:
            print(f"    Tipo {tipo}: {before} (sem mudança)")

    print(f"\n📊 Distribuição final:")
    for tipo in ['1', '2', '3', '4', '5', '6', '7']:
        count = count_after.get(tipo, 0)
        print(f"    Tipo {tipo}: {count} imagens")

print("\n" + "="*70)
print("✅ ATUALIZAÇÃO COMPLETA!")
print("="*70)

print(f"\n📁 Arquivo pronto para treino: labels.csv")
print("\n")
