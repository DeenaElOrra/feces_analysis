#!/usr/bin/env python3
"""
Investigar por que os modelos V2 pioraram drasticamente
"""

import pandas as pd
import numpy as np
from PIL import Image
from pathlib import Path
from collections import Counter
import os

print("="*70)
print("🔍 INVESTIGAÇÃO: Por que V2 piorou de 68% para 30%?")
print("="*70)

# Carregar CSV
df = pd.read_csv('labels.csv')

# Separar imagens originais (211) das novas (149)
# As novas são de 2025-11-09 e 2025-11-10
df['is_new'] = df['filename'].str.contains('2025-11-09|2025-11-10')

df_original = df[~df['is_new']]
df_new = df[df['is_new']]

print(f"\n📊 SEPARAÇÃO DO DATASET:")
print(f"   Originais: {len(df_original)} imagens")
print(f"   Novas: {len(df_new)} imagens")
print(f"   Total: {len(df)} imagens")

# ============================================================
# 1. COMPARAR DISTRIBUIÇÃO DE LABELS
# ============================================================

print(f"\n" + "="*70)
print(f"1️⃣  ANÁLISE DE DISTRIBUIÇÃO DE LABELS")
print(f"="*70)

print(f"\n📊 ORIGINAIS (211 imagens):")
counter_orig = Counter(df_original['bristol_type'])
for tipo in range(1, 8):
    count = counter_orig.get(tipo, 0)
    percent = (count / len(df_original)) * 100 if len(df_original) > 0 else 0
    print(f"   Tipo {tipo}: {count:3d} ({percent:5.1f}%)")

print(f"\n📊 NOVAS (149 imagens):")
counter_new = Counter(df_new['bristol_type'])
for tipo in range(1, 8):
    count = counter_new.get(tipo, 0)
    percent = (count / len(df_new)) * 100 if len(df_new) > 0 else 0
    print(f"   Tipo {tipo}: {count:3d} ({percent:5.1f}%)")

# Detectar desbalanço
print(f"\n⚠️  DESBALANÇO NAS NOVAS IMAGENS:")
for tipo in range(1, 8):
    orig_pct = (counter_orig.get(tipo, 0) / len(df_original)) * 100
    new_pct = (counter_new.get(tipo, 0) / len(df_new)) * 100
    diff = new_pct - orig_pct

    if abs(diff) > 10:
        status = "🔴" if abs(diff) > 20 else "🟡"
        print(f"   {status} Tipo {tipo}: {diff:+.1f}% de diferença!")

# ============================================================
# 2. VERIFICAR FORMATO E TAMANHO DAS IMAGENS
# ============================================================

print(f"\n" + "="*70)
print(f"2️⃣  ANÁLISE DE FORMATO E TAMANHO")
print(f"="*70)

def analyze_images(df_subset, label):
    sizes = []
    formats = []
    modes = []

    for idx, row in df_subset.iterrows():
        filename = row['filename']
        if not filename.startswith('dataset/'):
            filepath = Path('dataset') / filename
        else:
            filepath = Path(filename)

        if filepath.exists():
            try:
                with Image.open(filepath) as img:
                    sizes.append(img.size)
                    formats.append(img.format)
                    modes.append(img.mode)
            except:
                pass

    if sizes:
        sizes_counter = Counter(sizes)
        formats_counter = Counter(formats)
        modes_counter = Counter(modes)

        print(f"\n{label}:")
        print(f"   Formatos: {dict(formats_counter)}")
        print(f"   Modos de cor: {dict(modes_counter)}")
        print(f"   Tamanhos principais:")
        for size, count in sizes_counter.most_common(5):
            print(f"      {size}: {count} imagens")

    return sizes, formats, modes

print(f"\n📐 COMPARANDO DIMENSÕES...")
sizes_orig, formats_orig, modes_orig = analyze_images(df_original.head(50), "ORIGINAIS (amostra 50)")
sizes_new, formats_new, modes_new = analyze_images(df_new.head(50), "NOVAS (amostra 50)")

# ============================================================
# 3. VERIFICAR PATHS
# ============================================================

print(f"\n" + "="*70)
print(f"3️⃣  VERIFICAÇÃO DE PATHS")
print(f"="*70)

# Verificar se todas as imagens existem
missing = 0
for idx, row in df.iterrows():
    filename = row['filename']
    if not filename.startswith('dataset/'):
        filepath = Path('dataset') / filename
    else:
        filepath = Path(filename)

    if not filepath.exists():
        missing += 1
        if missing <= 5:
            print(f"   ❌ Não encontrado: {filename}")

if missing == 0:
    print(f"   ✅ Todas as {len(df)} imagens existem!")
else:
    print(f"   ⚠️  {missing} imagens não encontradas!")

# ============================================================
# 4. SUSPEITA PRINCIPAL
# ============================================================

print(f"\n" + "="*70)
print(f"💡 DIAGNÓSTICO")
print(f"="*70)

# Contar Tipos 3 e 4 nas novas
tipo3_new = counter_new.get(3, 0)
tipo4_new = counter_new.get(4, 0)
total_34_new = tipo3_new + tipo4_new
pct_34_new = (total_34_new / len(df_new)) * 100

print(f"\n🎯 CONCENTRAÇÃO NAS NOVAS IMAGENS:")
print(f"   Tipos 3+4: {total_34_new}/{len(df_new)} ({pct_34_new:.1f}%)")

if pct_34_new > 70:
    print(f"\n🔴 PROBLEMA DETECTADO:")
    print(f"   As novas imagens têm {pct_34_new:.1f}% de Tipos 3 e 4!")
    print(f"   Isso DESEQUILIBROU muito o dataset.")
    print(f"\n   O modelo V2 aprendeu a 'chutar' Tipo 4 sempre,")
    print(f"   porque estatisticamente tem mais chance de acertar!")

# Verificar qualidade dos labels
print(f"\n🏷️  POSSÍVEIS PROBLEMAS NOS LABELS:")

# Labels das novas imagens
print(f"\n   Primeiras 10 novas imagens:")
for idx, row in df_new.head(10).iterrows():
    print(f"      {row['filename']:60s} → Tipo {row['bristol_type']}")

# ============================================================
# 5. RECOMENDAÇÃO
# ============================================================

print(f"\n" + "="*70)
print(f"📋 RECOMENDAÇÕES")
print(f"="*70)

print(f"\n1️⃣  VERIFICAR LABELS MANUALMENTE:")
print(f"   - As 149 novas imagens estão rotuladas corretamente?")
print(f"   - Tipo 3 e 4 realmente dominam?")

print(f"\n2️⃣  BALANCEAR DATASET:")
print(f"   - Reduzir Tipos 3 e 4 nas novas imagens")
print(f"   - OU adicionar mais imagens dos outros tipos")

print(f"\n3️⃣  TREINAR COM DATASET ORIGINAL:")
print(f"   - Confirmar que código de treino está OK")
print(f"   - Espera-se ~68-70% de acurácia")

print(f"\n4️⃣  RETREINAR V2 BALANCEADO:")
print(f"   - Após balancear, retreinar modelos")

print(f"\n" + "="*70)
print(f"✅ INVESTIGAÇÃO COMPLETA!")
print(f"="*70)
