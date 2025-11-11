#!/usr/bin/env python3
"""
Script para avaliar a acurácia do modelo treinado
"""

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Configurações
IMG_SIZE = (224, 224)
BATCH_SIZE = 16

# Carregar modelo salvo
print("Carregando modelo...")
model = load_model('best_model_fe.h5')
print("✓ Modelo carregado!\n")

# Carregar dados
df = pd.read_csv('labels.csv')
dataset_path = Path('dataset')
df['filepath'] = df['filename'].apply(lambda x: str(dataset_path / x))
df['bristol_type_str'] = df['bristol_type'].astype(str)

# Criar gerador de teste (todo o dataset para avaliação completa)
test_datagen = ImageDataGenerator(rescale=1./255)
test_generator = test_datagen.flow_from_dataframe(
    df,
    x_col='filepath',
    y_col='bristol_type_str',
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

# Avaliar
print("="*60)
print("AVALIAÇÃO DO MODELO - Dataset Completo")
print("="*60)

test_loss, test_acc = model.evaluate(test_generator, verbose=1)
print(f"\n📊 Loss: {test_loss:.4f}")
print(f"📊 Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)\n")

# Predições detalhadas
print("Gerando predições...")
test_generator.reset()
y_pred_proba = model.predict(test_generator, verbose=1)
y_pred = np.argmax(y_pred_proba, axis=1)
y_true = test_generator.classes

# Classes
class_names = [str(i+1) for i in range(7)]

# Classification Report
print("\n" + "="*60)
print("RELATÓRIO POR CLASSE")
print("="*60)
print(classification_report(y_true, y_pred, target_names=class_names))

# Matriz de Confusão
cm = confusion_matrix(y_true, y_pred)
print("\n" + "="*60)
print("MATRIZ DE CONFUSÃO")
print("="*60)
print(cm)

# Calcular acurácia por classe
print("\n" + "="*60)
print("ACURÁCIA POR TIPO BRISTOL")
print("="*60)
for i in range(7):
    class_mask = (y_true == i)
    if class_mask.sum() > 0:
        class_acc = (y_pred[class_mask] == i).sum() / class_mask.sum()
        total = class_mask.sum()
        correct = (y_pred[class_mask] == i).sum()
        print(f"Tipo {i+1}: {class_acc:.4f} ({class_acc*100:.2f}%) - {correct}/{total} corretos")

# Análise de erros
print("\n" + "="*60)
print("ANÁLISE DE ERROS")
print("="*60)
errors = y_pred != y_true
print(f"Total de erros: {errors.sum()} de {len(y_true)} ({errors.sum()/len(y_true)*100:.2f}%)")

# Mostrar confusões mais comuns
print("\nConfusões mais comuns:")
confusion_pairs = []
for i in range(len(y_true)):
    if y_pred[i] != y_true[i]:
        confusion_pairs.append((y_true[i]+1, y_pred[i]+1))

from collections import Counter
confusion_counts = Counter(confusion_pairs)
for (true_class, pred_class), count in confusion_counts.most_common(5):
    print(f"  Tipo {true_class} confundido com Tipo {pred_class}: {count}x")

print("\n" + "="*60)
print("RESUMO")
print("="*60)
print(f"✓ Modelo salvo: best_model_fe.h5")
print(f"✓ Acurácia geral: {test_acc*100:.2f}%")
print(f"✓ Total de imagens: {len(y_true)}")
print(f"✓ Predições corretas: {(y_pred == y_true).sum()}")
print(f"✓ Predições incorretas: {(y_pred != y_true).sum()}")

# Comparação com baseline
baseline_acc = 1/7  # Chute aleatório para 7 classes
print(f"\n📈 Baseline (chute aleatório): {baseline_acc*100:.2f}%")
print(f"📈 Melhoria sobre baseline: {(test_acc/baseline_acc - 1)*100:.1f}%")
