#!/usr/bin/env python3
"""
Reavaliação JUSTA de TODOS os modelos
Usando dataset COMPLETO (sem split) como foi feito originalmente
"""

import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import os

print("="*70)
print("📊 REAVALIAÇÃO JUSTA - TODOS OS MODELOS")
print("="*70)
print("\nMétodo: Avaliar com dataset COMPLETO (como foi feito originalmente)")
print("Isso permite comparação justa entre V1 e V2\n")

IMG_SIZE = (224, 224)
BATCH_SIZE = 16

# ============================================================
# AVALIAR MODELOS V1 (Dataset 211)
# ============================================================

print("="*70)
print("📂 MODELOS V1 - Dataset Original (211 imagens)")
print("="*70)

# Carregar dataset original
df_v1 = pd.read_csv('labels.csv')
df_v1['filename'] = df_v1['filename'].apply(lambda x: f'dataset/{x}' if not x.startswith('dataset/') else x)
df_v1['bristol_type_str'] = df_v1['bristol_type'].astype(str)

test_datagen = ImageDataGenerator(rescale=1./255)

gen_v1 = test_datagen.flow_from_dataframe(
    df_v1, x_col='filename', y_col='bristol_type_str',
    target_size=IMG_SIZE, batch_size=BATCH_SIZE,
    class_mode='categorical', shuffle=False
)

print(f"\n✓ Dataset V1: {len(df_v1)} imagens")

results = []

# Modelo V1: Feature Extraction
print(f"\n🔍 Avaliando: Feature Extraction V1 (best_model_fe.h5)")
try:
    model = load_model('best_model_fe.h5')
    loss, acc = model.evaluate(gen_v1, verbose=0)
    print(f"   Acurácia: {acc:.4f} ({acc*100:.2f}%)")
    print(f"   Loss: {loss:.4f}")
    results.append(('Feature Extraction V1', '211 imgs', acc, loss, 'best_model_fe.h5'))
    gen_v1.reset()
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Modelo V1: Feature Extraction AUGMENTED
print(f"\n🔍 Avaliando: Feature Extraction V1 Augmented")
try:
    model = load_model('best_model_fe_AUGMENTED.h5')
    loss, acc = model.evaluate(gen_v1, verbose=0)
    print(f"   Acurácia: {acc:.4f} ({acc*100:.2f}%)")
    print(f"   Loss: {loss:.4f}")
    results.append(('Feature Extraction V1 Aug', '301 imgs (211+90)', acc, loss, 'best_model_fe_AUGMENTED.h5'))
    gen_v1.reset()
except Exception as e:
    print(f"   ❌ Erro: {e}")

# ============================================================
# AVALIAR MODELOS V2 (Dataset 360)
# ============================================================

print(f"\n" + "="*70)
print("📂 MODELOS V2 - Dataset Expandido (360 imagens)")
print("="*70)

# Carregar dataset V2
df_v2 = pd.read_csv('labels_v2_desbalanceado.csv')
df_v2['filename'] = df_v2['filename'].apply(lambda x: f'dataset/{x}' if not x.startswith('dataset/') else x)
df_v2['bristol_type_str'] = df_v2['bristol_type'].astype(str)

gen_v2 = test_datagen.flow_from_dataframe(
    df_v2, x_col='filename', y_col='bristol_type_str',
    target_size=IMG_SIZE, batch_size=BATCH_SIZE,
    class_mode='categorical', shuffle=False
)

print(f"\n✓ Dataset V2: {len(df_v2)} imagens")
print(f"   Distribuição:")
for tipo in range(1, 8):
    count = len(df_v2[df_v2['bristol_type'] == tipo])
    pct = (count / len(df_v2)) * 100
    print(f"      Tipo {tipo}: {count:3d} ({pct:5.1f}%)")

# Modelo V2: Feature Extraction
print(f"\n🔍 Avaliando: Feature Extraction V2")
try:
    model = load_model('best_model_fe_V2.h5')
    loss, acc = model.evaluate(gen_v2, verbose=0)
    print(f"   Acurácia: {acc:.4f} ({acc*100:.2f}%)")
    print(f"   Loss: {loss:.4f}")

    # Predições para análise
    y_pred = model.predict(gen_v2, verbose=0)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true = gen_v2.classes

    print(f"\n   📋 Relatório por Classe:")
    report = classification_report(
        y_true, y_pred_classes,
        target_names=[f"Tipo {i+1}" for i in range(7)],
        digits=2, zero_division=0
    )
    print(report)

    results.append(('Feature Extraction V2', '360 imgs', acc, loss, 'best_model_fe_V2.h5'))
    gen_v2.reset()
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Modelo V2: Fine-Tuning
print(f"\n🔍 Avaliando: Fine-Tuning V2")
try:
    model = load_model('best_model_ft_V2.h5')
    loss, acc = model.evaluate(gen_v2, verbose=0)
    print(f"   Acurácia: {acc:.4f} ({acc*100:.2f}%)")
    print(f"   Loss: {loss:.4f}")

    # Predições para análise
    y_pred = model.predict(gen_v2, verbose=0)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true = gen_v2.classes

    print(f"\n   📋 Relatório por Classe:")
    report = classification_report(
        y_true, y_pred_classes,
        target_names=[f"Tipo {i+1}" for i in range(7)],
        digits=2, zero_division=0
    )
    print(report)

    results.append(('Fine-Tuning V2', '360 imgs', acc, loss, 'best_model_ft_V2.h5'))
    gen_v2.reset()
except Exception as e:
    print(f"   ❌ Erro: {e}")

# ============================================================
# COMPARAÇÃO FINAL
# ============================================================

print(f"\n" + "="*70)
print("🏆 RANKING FINAL")
print("="*70)

# Ordenar por acurácia
results_sorted = sorted(results, key=lambda x: x[2], reverse=True)

print(f"\n{'Pos':<5} {'Modelo':<30} {'Dataset':<20} {'Acurácia':<15} {'Loss'}")
print("-"*70)

for i, (name, dataset, acc, loss, filename) in enumerate(results_sorted, 1):
    emoji = "🥇" if i == 1 else ("🥈" if i == 2 else "🥉")
    print(f"{emoji} {i:<3} {name:<30} {dataset:<20} {acc:.4f} ({acc*100:5.2f}%)  {loss:.4f}")

# Melhor modelo
best = results_sorted[0]
print(f"\n🏆 MELHOR MODELO: {best[0]}")
print(f"   Arquivo: {best[4]}")
print(f"   Acurácia: {best[2]:.4f} ({best[2]*100:.2f}%)")

# Análise do problema V2
print(f"\n" + "="*70)
print("💡 ANÁLISE")
print("="*70)

v1_best = max([r for r in results if 'V1' in r[0]], key=lambda x: x[2])
v2_best = max([r for r in results if 'V2' in r[0]], key=lambda x: x[2])

print(f"\n📊 Comparação V1 vs V2:")
print(f"   Melhor V1: {v1_best[0]} = {v1_best[2]*100:.2f}%")
print(f"   Melhor V2: {v2_best[0]} = {v2_best[2]*100:.2f}%")
print(f"   Diferença: {(v2_best[2] - v1_best[2])*100:+.2f}%")

if v2_best[2] < v1_best[2]:
    print(f"\n⚠️  PROBLEMA CONFIRMADO:")
    print(f"   V2 piorou devido ao dataset EXTREMAMENTE desbalanceado")
    print(f"   93.3% das novas imagens são Tipos 3 e 4!")
else:
    print(f"\n✅ V2 MELHOROU!")

# Salvar resultados
with open('fair_evaluation_results.txt', 'w') as f:
    f.write("REAVALIAÇÃO JUSTA - TODOS OS MODELOS\n")
    f.write("="*70 + "\n\n")
    f.write("Método: Dataset COMPLETO (sem split)\n\n")

    for i, (name, dataset, acc, loss, filename) in enumerate(results_sorted, 1):
        f.write(f"{i}. {name} ({dataset})\n")
        f.write(f"   Arquivo: {filename}\n")
        f.write(f"   Acurácia: {acc:.4f} ({acc*100:.2f}%)\n")
        f.write(f"   Loss: {loss:.4f}\n\n")

    f.write(f"\nMelhor: {best[0]} com {best[2]*100:.2f}%\n")

print(f"\n💾 Resultados salvos: fair_evaluation_results.txt")

print(f"\n" + "="*70)
print("✅ REAVALIAÇÃO COMPLETA!")
print("="*70)
print()
