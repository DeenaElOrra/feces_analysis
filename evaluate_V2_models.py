#!/usr/bin/env python3
"""
Avaliar Modelos V2 treinados com 360 imagens
"""

import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

print("="*70)
print("📊 AVALIAÇÃO DOS MODELOS V2 (360 IMAGENS)")
print("="*70)

# Configurações
IMG_SIZE = (224, 224)
BATCH_SIZE = 16

# Carregar dados
df = pd.read_csv('labels.csv')
df['filename'] = df['filename'].apply(lambda x: f'dataset/{x}' if not x.startswith('dataset/') else x)
df['bristol_type_str'] = df['bristol_type'].astype(str)

# Split (mesmo random_state usado no treino)
train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    stratify=df['bristol_type'],
    random_state=42
)

print(f"\n📊 Dataset V2:")
print(f"   Total: {len(df)} imagens")
print(f"   Test: {len(test_df)} imagens")

# Test generator
test_datagen = ImageDataGenerator(rescale=1./255)

test_generator = test_datagen.flow_from_dataframe(
    test_df,
    x_col='filename',
    y_col='bristol_type_str',
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

# ============================================================
# AVALIAR MODELOS V2
# ============================================================

models_to_evaluate = [
    ('Feature Extraction V2', 'best_model_fe_V2.h5'),
    ('Fine-Tuning V2', 'best_model_ft_V2.h5')
]

results = []

for name, filename in models_to_evaluate:
    print(f"\n" + "="*70)
    print(f"🔍 AVALIANDO: {name}")
    print(f"="*70)

    try:
        # Carregar modelo
        model = load_model(filename)
        print(f"✓ Modelo carregado: {filename}")

        # Avaliar
        loss, acc = model.evaluate(test_generator, verbose=0)

        print(f"\n📊 RESULTADOS:")
        print(f"   Acurácia: {acc:.4f} ({acc*100:.2f}%)")
        print(f"   Loss: {loss:.4f}")

        # Predições
        y_pred = model.predict(test_generator, verbose=0)
        y_pred_classes = np.argmax(y_pred, axis=1)
        y_true = test_generator.classes

        # Relatório por classe
        print(f"\n📋 Relatório por Classe:")
        report = classification_report(
            y_true,
            y_pred_classes,
            target_names=[f"Tipo {i+1}" for i in range(7)],
            digits=3
        )
        print(report)

        # Salvar resultados
        results.append({
            'name': name,
            'filename': filename,
            'accuracy': acc,
            'loss': loss
        })

        # Reset generator
        test_generator.reset()

    except Exception as e:
        print(f"❌ Erro ao avaliar {name}: {e}")

# ============================================================
# COMPARAÇÃO COM MODELOS V1
# ============================================================

print("\n" + "="*70)
print("🏆 COMPARAÇÃO: V1 vs V2")
print("="*70)

# Modelos V1 (valores conhecidos)
v1_results = [
    {'name': 'Feature Extraction V1', 'accuracy': 0.6872, 'dataset': '211 imgs'},
    {'name': 'Feature Extraction Augmented', 'accuracy': 0.7542, 'dataset': '301 imgs (211+90)'},
]

print(f"\n📊 MODELOS V1:")
for r in v1_results:
    print(f"   {r['name']:30s} {r['accuracy']:.4f} ({r['accuracy']*100:.2f}%)  [{r['dataset']}]")

print(f"\n📊 MODELOS V2 (360 imagens REAIS):")
for r in results:
    print(f"   {r['name']:30s} {r['accuracy']:.4f} ({r['accuracy']*100:.2f}%)")

# Melhor modelo
all_models = v1_results + results
best = max(all_models, key=lambda x: x['accuracy'])

print(f"\n🥇 MELHOR MODELO:")
print(f"   {best['name']}")
print(f"   Acurácia: {best['accuracy']:.4f} ({best['accuracy']*100:.2f}%)")

# Ganho do melhor V2 vs melhor V1
best_v1 = max(v1_results, key=lambda x: x['accuracy'])
best_v2 = max(results, key=lambda x: x['accuracy']) if results else None

if best_v2:
    diff = best_v2['accuracy'] - best_v1['accuracy']
    diff_percent = (diff / best_v1['accuracy']) * 100

    print(f"\n📈 GANHO V2:")
    if diff > 0:
        print(f"   +{diff:.4f} ({diff_percent:+.2f}%) 🎉 MELHOROU!")
    elif diff < 0:
        print(f"   {diff:.4f} ({diff_percent:.2f}%) ⚠️ PIOROU")
    else:
        print(f"   0.0000 (sem mudança)")

# Salvar resultados
with open('evaluation_V2_results.txt', 'w') as f:
    f.write("RESULTADOS DA AVALIAÇÃO - MODELOS V2\n")
    f.write("="*70 + "\n\n")
    f.write(f"Dataset: 360 imagens (211 originais + 149 novas)\n\n")

    for r in results:
        f.write(f"{r['name']}:\n")
        f.write(f"  Arquivo: {r['filename']}\n")
        f.write(f"  Acurácia: {r['accuracy']:.4f} ({r['accuracy']*100:.2f}%)\n")
        f.write(f"  Loss: {r['loss']:.4f}\n\n")

    if best_v2:
        f.write(f"\nMelhor Modelo V2: {best_v2['name']}\n")
        f.write(f"Acurácia: {best_v2['accuracy']:.4f} ({best_v2['accuracy']*100:.2f}%)\n")
        f.write(f"Ganho vs V1: {diff:+.4f} ({diff_percent:+.2f}%)\n")

print(f"\n💾 Resultados salvos em: evaluation_V2_results.txt")

print("\n" + "="*70)
print("✅ AVALIAÇÃO COMPLETA!")
print("="*70)
print()
