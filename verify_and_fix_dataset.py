#!/usr/bin/env python3
"""
Verificar e Corrigir Dataset V2 - Remover Imagens Corrompidas
"""

import csv
from PIL import Image
from pathlib import Path

print("="*70)
print("🔍 VERIFICANDO DATASET V2 - 360 IMAGENS")
print("="*70)

# Ler CSV
with open('labels.csv', 'r') as f:
    reader = csv.DictReader(f)
    all_images = list(reader)

print(f"\n📊 Total no CSV: {len(all_images)} imagens")

# Verificar cada imagem
valid_images = []
corrupted_images = []

print(f"\n🔍 Verificando imagens...")

for i, row in enumerate(all_images, 1):
    filename = row['filename']
    bristol_type = row['bristol_type']

    # Ajustar path se necessário
    if not filename.startswith('dataset/'):
        filepath = Path('dataset') / filename
    else:
        filepath = Path(filename)

    # Verificar se arquivo existe
    if not filepath.exists():
        print(f"  ⚠️  [{i}/{len(all_images)}] Arquivo não encontrado: {filename}")
        corrupted_images.append((filename, bristol_type, "Arquivo não encontrado"))
        continue

    # Verificar se pode ser aberto
    try:
        with Image.open(filepath) as img:
            img.verify()

        # Verificar novamente (verify() fecha o arquivo)
        with Image.open(filepath) as img:
            img.load()

        # Imagem válida
        valid_images.append({
            'filename': filename,
            'bristol_type': bristol_type
        })

        if i % 50 == 0:
            print(f"  ✓ Verificadas {i}/{len(all_images)} imagens...")

    except Exception as e:
        print(f"  ❌ [{i}/{len(all_images)}] CORROMPIDA: {filename} - {str(e)[:50]}")
        corrupted_images.append((filename, bristol_type, str(e)[:50]))

print(f"\n" + "="*70)
print(f"📊 RESULTADO DA VERIFICAÇÃO")
print(f"="*70)

print(f"\n✅ Imagens válidas: {len(valid_images)}")
print(f"❌ Imagens corrompidas: {len(corrupted_images)}")

if corrupted_images:
    print(f"\n❌ IMAGENS PROBLEMÁTICAS:")
    for filename, tipo, error in corrupted_images:
        print(f"   - {filename} (Tipo {tipo})")
        print(f"     Erro: {error}")

    print(f"\n🔧 CORRIGINDO labels.csv...")

    # Criar backup
    with open('labels_backup_before_fix.csv', 'w') as f_out:
        with open('labels.csv', 'r') as f_in:
            f_out.write(f_in.read())
    print(f"   ✓ Backup criado: labels_backup_before_fix.csv")

    # Salvar CSV limpo
    with open('labels.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['filename', 'bristol_type'])
        writer.writeheader()
        writer.writerows(valid_images)

    print(f"   ✓ CSV atualizado: {len(valid_images)} imagens válidas")

    # Distribuição após limpeza
    from collections import Counter
    tipos = [img['bristol_type'] for img in valid_images]
    counter = Counter(tipos)

    print(f"\n📈 DISTRIBUIÇÃO APÓS LIMPEZA:")
    for tipo in sorted([str(i) for i in range(1, 8)]):
        count = counter.get(tipo, 0)
        print(f"   Tipo {tipo}: {count} imagens")

else:
    print(f"\n✅ TODAS AS IMAGENS ESTÃO VÁLIDAS!")
    print(f"   Nenhuma correção necessária.")

print(f"\n" + "="*70)
print(f"✅ VERIFICAÇÃO COMPLETA!")
print(f"="*70)
print(f"\n📁 Dataset limpo: {len(valid_images)} imagens")
print(f"📁 Arquivo: labels.csv")
print(f"\n🚀 Agora você pode treinar os modelos sem erros!")
print()
