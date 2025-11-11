#!/usr/bin/env python3
"""
Balancear Dataset V2 - Criar versão balanceada do dataset de 360 imagens
Estratégia: Undersampling dos tipos majoritários (3 e 4)
"""

import pandas as pd
import numpy as np
from collections import Counter

print("="*70)
print("⚖️  BALANCEAMENTO DO DATASET V2")
print("="*70)

# Carregar dataset V2 desbalanceado (360 imagens)
df = pd.read_csv('labels_v2_desbalanceado.csv')
print(f"\n📊 Dataset original V2: {len(df)} imagens")

# Distribuição atual
print(f"\n📈 DISTRIBUIÇÃO ATUAL:")
counter = Counter(df['bristol_type'])
for tipo in range(1, 8):
    count = counter.get(tipo, 0)
    pct = (count / len(df)) * 100
    print(f"   Tipo {tipo}: {count:3d} ({pct:5.1f}%)")

# ============================================================
# ESTRATÉGIA DE BALANCEAMENTO
# ============================================================

print(f"\n" + "="*70)
print(f"🎯 ESTRATÉGIA DE BALANCEAMENTO")
print(f"="*70)

# Identificar tipos com muitas/poucas imagens
tipo_counts = {tipo: counter.get(tipo, 0) for tipo in range(1, 8)}

# Calcular média e mediana
counts = list(tipo_counts.values())
media = np.mean(counts)
mediana = np.median(counts)

print(f"\n📊 Estatísticas:")
print(f"   Média: {media:.1f} imagens/tipo")
print(f"   Mediana: {mediana:.1f} imagens/tipo")
print(f"   Mínimo: {min(counts)} (Tipo {min(tipo_counts, key=tipo_counts.get)})")
print(f"   Máximo: {max(counts)} (Tipo {max(tipo_counts, key=tipo_counts.get)})")

# ============================================================
# OPÇÃO 1: UNDERSAMPLING (reduzir tipos majoritários)
# ============================================================

print(f"\n" + "="*70)
print(f"📉 OPÇÃO 1: UNDERSAMPLING")
print(f"="*70)
print(f"\nLimitar cada tipo ao máximo da mediana ({int(mediana)} imagens)")

# Criar dataset balanceado
balanced_dfs = []

for tipo in range(1, 8):
    df_tipo = df[df['bristol_type'] == tipo]
    count = len(df_tipo)

    # Limitar ao máximo da mediana
    max_samples = int(mediana)

    if count > max_samples:
        # Reduzir aleatoriamente
        df_tipo_sampled = df_tipo.sample(n=max_samples, random_state=42)
        print(f"   Tipo {tipo}: {count} → {max_samples} (removidos {count - max_samples})")
    else:
        df_tipo_sampled = df_tipo
        print(f"   Tipo {tipo}: {count} → {count} (mantido)")

    balanced_dfs.append(df_tipo_sampled)

# Concatenar
df_balanced = pd.concat(balanced_dfs, ignore_index=True)

# Embaralhar
df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\n✅ Dataset balanceado criado: {len(df_balanced)} imagens")

# Nova distribuição
print(f"\n📈 NOVA DISTRIBUIÇÃO:")
counter_balanced = Counter(df_balanced['bristol_type'])
for tipo in range(1, 8):
    count = counter_balanced.get(tipo, 0)
    pct = (count / len(df_balanced)) * 100
    original = counter.get(tipo, 0)
    diff = count - original
    print(f"   Tipo {tipo}: {count:3d} ({pct:5.1f}%)  [{diff:+3d}]")

# ============================================================
# SALVAR DATASET BALANCEADO
# ============================================================

print(f"\n" + "="*70)
print(f"💾 SALVANDO DATASET BALANCEADO")
print(f"="*70)

# Fazer backup do dataset original
import shutil
shutil.copy('labels.csv', 'labels_v2_desbalanceado_backup.csv')
print(f"✓ Backup criado: labels_v2_desbalanceado_backup.csv")

# Salvar dataset balanceado
df_balanced.to_csv('labels_v2_balanced.csv', index=False)
print(f"✓ Dataset balanceado: labels_v2_balanced.csv ({len(df_balanced)} imagens)")

# ============================================================
# ESTATÍSTICAS DE BALANCEAMENTO
# ============================================================

print(f"\n" + "="*70)
print(f"📊 ESTATÍSTICAS DO BALANCEAMENTO")
print(f"="*70)

print(f"\n📉 Imagens removidas:")
removed = len(df) - len(df_balanced)
print(f"   Total: {removed} imagens ({(removed/len(df))*100:.1f}%)")

for tipo in range(1, 8):
    original = counter.get(tipo, 0)
    balanced = counter_balanced.get(tipo, 0)
    diff = original - balanced
    if diff > 0:
        print(f"   Tipo {tipo}: -{diff} imagens")

# Calcular coeficiente de variação (menor = mais balanceado)
counts_original = [counter.get(tipo, 0) for tipo in range(1, 8)]
counts_balanced = [counter_balanced.get(tipo, 0) for tipo in range(1, 8)]

cv_original = (np.std(counts_original) / np.mean(counts_original)) * 100
cv_balanced = (np.std(counts_balanced) / np.mean(counts_balanced)) * 100

print(f"\n📊 Coeficiente de Variação (quanto menor, melhor):")
print(f"   Original: {cv_original:.2f}%")
print(f"   Balanceado: {cv_balanced:.2f}%")
print(f"   Melhoria: {cv_original - cv_balanced:.2f}%")

# ============================================================
# PRÓXIMOS PASSOS
# ============================================================

print(f"\n" + "="*70)
print(f"🚀 PRÓXIMOS PASSOS")
print(f"="*70)

print(f"\n1️⃣  Retreinar modelos com dataset balanceado:")
print(f"   - Editar retrain_all_models.py para usar labels_v2_balanced.csv")
print(f"   - Ou criar novo script de treino")

print(f"\n2️⃣  Comparar resultados:")
print(f"   - Modelos V2 desbalanceados (37% e 20%)")
print(f"   - Modelos V2 balanceados (esperado: 65-75%)")

print(f"\n3️⃣  Se resultados melhorarem:")
print(f"   - Substituir labels.csv por labels_v2_balanced.csv")
print(f"   - Ou coletar mais imagens dos tipos raros")

print(f"\n" + "="*70)
print(f"✅ BALANCEAMENTO COMPLETO!")
print(f"="*70)
print()
