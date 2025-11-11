#!/usr/bin/env python3
"""
Análise Comparativa: Modelo Original vs Modelo Aumentado
"""

import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

print("="*70)
print("📊 ANÁLISE COMPARATIVA DE MODELOS")
print("="*70)

# Configurações
IMG_SIZE = (224, 224)
BATCH_SIZE = 16

# ============================================================
# 1. AVALIAR MODELO ORIGINAL
# ============================================================

print("\n🔵 AVALIANDO MODELO ORIGINAL...")
print("-"*70)

# Carregar dados originais
df_original = pd.read_csv('labels.csv')
df_original['bristol_type_str'] = df_original['bristol_type'].astype(str)

# Ajustar paths
df_original['filename'] = df_original['filename'].apply(lambda x: f'dataset/{x}')

# Data generator
test_datagen = ImageDataGenerator(rescale=1./255)

test_generator_orig = test_datagen.flow_from_dataframe(
    df_original,
    x_col='filename',
    y_col='bristol_type_str',
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

# Carregar e avaliar modelo original
model_orig = load_model('best_model_fe.h5')
loss_orig, acc_orig = model_orig.evaluate(test_generator_orig, verbose=0)

# Predições
y_pred_orig = model_orig.predict(test_generator_orig, verbose=0)
y_pred_classes_orig = np.argmax(y_pred_orig, axis=1)
y_true_orig = test_generator_orig.classes

print(f"✓ Dataset: {len(df_original)} imagens")
print(f"✓ Loss: {loss_orig:.4f}")
print(f"✓ Acurácia: {acc_orig:.4f} ({acc_orig*100:.2f}%)")

# ============================================================
# 2. AVALIAR MODELO AUMENTADO
# ============================================================

print("\n🟢 AVALIANDO MODELO AUMENTADO...")
print("-"*70)

# Carregar dados aumentados
df_augmented = pd.read_csv('labels_augmented_TEST.csv')
df_augmented['bristol_type_str'] = df_augmented['bristol_type'].astype(str)

test_generator_aug = test_datagen.flow_from_dataframe(
    df_augmented,
    x_col='filename',
    y_col='bristol_type_str',
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

# Carregar e avaliar modelo aumentado
model_aug = load_model('best_model_fe_AUGMENTED.h5')
loss_aug, acc_aug = model_aug.evaluate(test_generator_aug, verbose=0)

# Predições
y_pred_aug = model_aug.predict(test_generator_aug, verbose=0)
y_pred_classes_aug = np.argmax(y_pred_aug, axis=1)
y_true_aug = test_generator_aug.classes

print(f"✓ Dataset: {len(df_augmented)} imagens")
print(f"✓ Loss: {loss_aug:.4f}")
print(f"✓ Acurácia: {acc_aug:.4f} ({acc_aug*100:.2f}%)")

# ============================================================
# 3. COMPARAÇÃO DETALHADA
# ============================================================

print("\n" + "="*70)
print("📈 COMPARAÇÃO DETALHADA")
print("="*70)

# Diferença absoluta
diff = acc_aug - acc_orig
diff_percent = (diff / acc_orig) * 100

print(f"\n🔵 MODELO ORIGINAL:")
print(f"   Dataset: {len(df_original)} imagens (original)")
print(f"   Acurácia: {acc_orig:.4f} ({acc_orig*100:.2f}%)")
print(f"   Loss: {loss_orig:.4f}")

print(f"\n🟢 MODELO AUMENTADO:")
print(f"   Dataset: {len(df_augmented)} imagens (+{len(df_augmented)-len(df_original)} sintéticas)")
print(f"   Acurácia: {acc_aug:.4f} ({acc_aug*100:.2f}%)")
print(f"   Loss: {loss_aug:.4f}")

print(f"\n📊 DIFERENÇA:")
if diff > 0:
    print(f"   ✅ +{diff:.4f} ({diff_percent:+.2f}%)")
    print(f"   O modelo aumentado É MELHOR!")
elif diff < 0:
    print(f"   ⚠️  {diff:.4f} ({diff_percent:.2f}%)")
    print(f"   O modelo aumentado piorou")
else:
    print(f"   ➖ 0.0000 (sem diferença)")

# ============================================================
# 4. RELATÓRIOS POR CLASSE
# ============================================================

print("\n" + "="*70)
print("📋 DESEMPENHO POR CLASSE - MODELO ORIGINAL")
print("="*70)

report_orig = classification_report(
    y_true_orig,
    y_pred_classes_orig,
    target_names=[f"Tipo {i+1}" for i in range(7)],
    digits=3
)
print(report_orig)

print("\n" + "="*70)
print("📋 DESEMPENHO POR CLASSE - MODELO AUMENTADO")
print("="*70)

report_aug = classification_report(
    y_true_aug,
    y_pred_classes_aug,
    target_names=[f"Tipo {i+1}" for i in range(7)],
    digits=3
)
print(report_aug)

# ============================================================
# 5. MATRIZES DE CONFUSÃO
# ============================================================

# Calcular matrizes
cm_orig = confusion_matrix(y_true_orig, y_pred_classes_orig)
cm_aug = confusion_matrix(y_true_aug, y_pred_classes_aug)

# Criar figura
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Matriz Original
sns.heatmap(
    cm_orig,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=[f'T{i+1}' for i in range(7)],
    yticklabels=[f'T{i+1}' for i in range(7)],
    ax=axes[0]
)
axes[0].set_title(f'Modelo Original - {acc_orig*100:.2f}%', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Predito')
axes[0].set_ylabel('Real')

# Matriz Aumentado
sns.heatmap(
    cm_aug,
    annot=True,
    fmt='d',
    cmap='Greens',
    xticklabels=[f'T{i+1}' for i in range(7)],
    yticklabels=[f'T{i+1}' for i in range(7)],
    ax=axes[1]
)
axes[1].set_title(f'Modelo Aumentado - {acc_aug*100:.2f}%', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Predito')
axes[1].set_ylabel('Real')

plt.tight_layout()
plt.savefig('comparison_confusion_matrices.png', dpi=150, bbox_inches='tight')
print(f"\n✓ Matrizes de confusão salvas: comparison_confusion_matrices.png")

# ============================================================
# 6. COMPARAÇÃO POR CLASSE
# ============================================================

# Extrair precision, recall, f1 por classe
from sklearn.metrics import precision_recall_fscore_support

precision_orig, recall_orig, f1_orig, _ = precision_recall_fscore_support(
    y_true_orig, y_pred_classes_orig, average=None
)

precision_aug, recall_aug, f1_aug, _ = precision_recall_fscore_support(
    y_true_aug, y_pred_classes_aug, average=None
)

# Criar gráfico comparativo
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

classes = [f'Tipo {i+1}' for i in range(7)]
x = np.arange(len(classes))
width = 0.35

# Precision
axes[0].bar(x - width/2, precision_orig, width, label='Original', color='#3498db', alpha=0.8)
axes[0].bar(x + width/2, precision_aug, width, label='Aumentado', color='#2ecc71', alpha=0.8)
axes[0].set_title('Precision por Classe', fontweight='bold')
axes[0].set_ylabel('Precision')
axes[0].set_xticks(x)
axes[0].set_xticklabels(classes)
axes[0].legend()
axes[0].grid(axis='y', alpha=0.3)

# Recall
axes[1].bar(x - width/2, recall_orig, width, label='Original', color='#3498db', alpha=0.8)
axes[1].bar(x + width/2, recall_aug, width, label='Aumentado', color='#2ecc71', alpha=0.8)
axes[1].set_title('Recall por Classe', fontweight='bold')
axes[1].set_ylabel('Recall')
axes[1].set_xticks(x)
axes[1].set_xticklabels(classes)
axes[1].legend()
axes[1].grid(axis='y', alpha=0.3)

# F1-Score
axes[2].bar(x - width/2, f1_orig, width, label='Original', color='#3498db', alpha=0.8)
axes[2].bar(x + width/2, f1_aug, width, label='Aumentado', color='#2ecc71', alpha=0.8)
axes[2].set_title('F1-Score por Classe', fontweight='bold')
axes[2].set_ylabel('F1-Score')
axes[2].set_xticks(x)
axes[2].set_xticklabels(classes)
axes[2].legend()
axes[2].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('comparison_metrics_by_class.png', dpi=150, bbox_inches='tight')
print(f"✓ Métricas por classe salvas: comparison_metrics_by_class.png")

# ============================================================
# 7. ANÁLISE DE GANHOS POR CLASSE
# ============================================================

print("\n" + "="*70)
print("🎯 GANHOS POR CLASSE")
print("="*70)

print(f"\n{'Classe':<10} {'F1 Original':<12} {'F1 Aumentado':<15} {'Diferença':<12} {'Status'}")
print("-"*70)

for i in range(7):
    diff_f1 = f1_aug[i] - f1_orig[i]
    status = "✅ MELHOROU" if diff_f1 > 0.05 else ("⚠️  PIOROU" if diff_f1 < -0.05 else "➖ IGUAL")

    print(f"Tipo {i+1:<5} {f1_orig[i]:.3f} ({f1_orig[i]*100:5.1f}%)  {f1_aug[i]:.3f} ({f1_aug[i]*100:5.1f}%)  {diff_f1:+.3f} ({diff_f1*100:+5.1f}%)  {status}")

# ============================================================
# 8. RECOMENDAÇÃO FINAL
# ============================================================

print("\n" + "="*70)
print("💡 RECOMENDAÇÃO FINAL")
print("="*70)

if diff > 0.05:
    print("\n✅ USAR MODELO AUMENTADO!")
    print(f"   O modelo aumentado teve ganho significativo: +{diff*100:.2f}%")
    print(f"\n📁 Arquivos:")
    print(f"   Modelo: best_model_fe_AUGMENTED.h5")
    print(f"   Dataset: labels_augmented_TEST.csv")
    print(f"\n🎯 Próximos passos:")
    print(f"   1. Renomear arquivos para produção:")
    print(f"      mv best_model_fe_AUGMENTED.h5 best_model_fe_PROD.h5")
    print(f"   2. Fazer backup do modelo original (já feito)")
    print(f"   3. Considerar aumentar ainda mais o dataset")

elif diff > 0:
    print("\n✅ Modelo aumentado melhorou levemente")
    print(f"   Ganho: +{diff*100:.2f}%")
    print("\n💭 Recomendação:")
    print("   - Teste em cenários reais para decidir")
    print("   - Considere treinar com mais épocas")
    print("   - Tente ajustar hiperparâmetros")

else:
    print("\n⚠️  MANTER MODELO ORIGINAL")
    print(f"   O modelo aumentado não trouxe melhorias ({diff*100:.2f}%)")
    print("\n🔧 Sugestões:")
    print("   1. Coletar mais dados REAIS (melhor que sintéticos)")
    print("   2. Ajustar parâmetros de augmentation")
    print("   3. Tentar outras arquiteturas (ResNet, EfficientNet)")
    print("   4. Aplicar técnicas como focal loss para classes difíceis")

print("\n" + "="*70)
print("✅ ANÁLISE COMPLETA!")
print("="*70)
print("\n📊 Gráficos salvos:")
print("   - comparison_confusion_matrices.png")
print("   - comparison_metrics_by_class.png")
print("\n")
