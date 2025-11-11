#!/usr/bin/env python3
"""
Script para Retreinar TODOS os Modelos com Dataset V2 (360 imagens)

Este script treina sequencialmente:
1. Feature Extraction (VGG16 congelado) → best_model_fe_V2.h5
2. Fine-Tuning (VGG16 treinável) → best_model_ft_V2.h5
"""

import tensorflow as tf
from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from pathlib import Path
import os

print("="*70)
print("🚀 RETREINAMENTO COMPLETO - Dataset V2 (360 imagens)")
print("="*70)

# Configurações
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 50

# ============================================================
# PREPARAR DADOS
# ============================================================

print("\n📊 CARREGANDO DATASET V2...")
df = pd.read_csv('labels.csv')
print(f"✓ Total de imagens: {len(df)}")

# Ajustar paths
df['filename'] = df['filename'].apply(lambda x: f'dataset/{x}' if not x.startswith('dataset/') else x)
df['bristol_type_str'] = df['bristol_type'].astype(str)

# Distribuição
print(f"\n📈 Distribuição:")
for tipo in range(1, 8):
    count = len(df[df['bristol_type'] == tipo])
    print(f"  Tipo {tipo}: {count} imagens")

# Split estratificado
train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    stratify=df['bristol_type'],
    random_state=42
)

print(f"\n✓ Train: {len(train_df)} imagens (80%)")
print(f"✓ Test: {len(test_df)} imagens (20%)")

# Data Generators
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    brightness_range=[0.8, 1.2],
    fill_mode='nearest'
)

test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_dataframe(
    train_df,
    x_col='filename',
    y_col='bristol_type_str',
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True,
    seed=42,
    subset='training'
)

val_generator = train_datagen.flow_from_dataframe(
    train_df,
    x_col='filename',
    y_col='bristol_type_str',
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False,
    subset='validation'
)

test_generator = test_datagen.flow_from_dataframe(
    test_df,
    x_col='filename',
    y_col='bristol_type_str',
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

# Class Weights
y_train = train_df['bristol_type'].values
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_train),
    y=y_train
)
class_weight_dict = dict(enumerate(class_weights))

print(f"\n⚖️  Class Weights:")
for i, weight in class_weight_dict.items():
    print(f"  Tipo {i+1}: {weight:.2f}")

# ============================================================
# MODELO 1: FEATURE EXTRACTION
# ============================================================

print("\n" + "="*70)
print("🏗️  MODELO 1: FEATURE EXTRACTION (VGG16 Congelado)")
print("="*70)

def create_feature_extraction_model():
    base_model = VGG16(
        weights='imagenet',
        include_top=False,
        input_shape=(224, 224, 3)
    )
    base_model.trainable = False

    model = Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dense(512, activation='relu'),
        BatchNormalization(),
        Dropout(0.5),
        Dense(256, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        Dense(7, activation='softmax')
    ])

    return model

print("\n🏗️  Criando modelo Feature Extraction...")
model_fe = create_feature_extraction_model()

model_fe.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print(f"✓ Modelo criado: {model_fe.count_params():,} parâmetros")

# Callbacks
callbacks_fe = [
    EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    ),
    ModelCheckpoint(
        'best_model_fe_V2.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
]

print(f"\n🚀 TREINANDO Feature Extraction...")
print(f"⏱️  Tempo estimado: 15-25 minutos\n")

history_fe = model_fe.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    callbacks=callbacks_fe,
    class_weight=class_weight_dict,
    verbose=1
)

# Avaliar
test_loss_fe, test_acc_fe = model_fe.evaluate(test_generator, verbose=0)

print(f"\n" + "="*70)
print(f"✅ FEATURE EXTRACTION COMPLETO!")
print(f"="*70)
print(f"📊 Acurácia no teste: {test_acc_fe:.4f} ({test_acc_fe*100:.2f}%)")
print(f"📊 Loss no teste: {test_loss_fe:.4f}")
print(f"💾 Modelo salvo: best_model_fe_V2.h5")

# ============================================================
# MODELO 2: FINE-TUNING
# ============================================================

print("\n" + "="*70)
print("🏗️  MODELO 2: FINE-TUNING (VGG16 Treinável)")
print("="*70)

# RECRIAR GERADORES para o segundo modelo
print("\n📊 Recriando geradores de dados...")

train_datagen_ft = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    brightness_range=[0.8, 1.2],
    fill_mode='nearest'
)

train_generator_ft = train_datagen_ft.flow_from_dataframe(
    train_df,
    x_col='filename',
    y_col='bristol_type_str',
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True,
    seed=42,
    subset='training'
)

val_generator_ft = train_datagen_ft.flow_from_dataframe(
    train_df,
    x_col='filename',
    y_col='bristol_type_str',
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False,
    subset='validation'
)

print("✓ Geradores recriados!")

def create_fine_tuning_model():
    base_model = VGG16(
        weights='imagenet',
        include_top=False,
        input_shape=(224, 224, 3)
    )

    # Descongelar últimas 4 camadas
    for layer in base_model.layers[:-4]:
        layer.trainable = False
    for layer in base_model.layers[-4:]:
        layer.trainable = True

    model = Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dense(512, activation='relu'),
        BatchNormalization(),
        Dropout(0.5),
        Dense(256, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        Dense(7, activation='softmax')
    ])

    return model

print("\n🏗️  Criando modelo Fine-Tuning...")
model_ft = create_fine_tuning_model()

model_ft.compile(
    optimizer=Adam(learning_rate=0.0001),  # Learning rate menor para fine-tuning
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

trainable = sum([1 for layer in model_ft.layers if layer.trainable])
print(f"✓ Modelo criado: {model_ft.count_params():,} parâmetros")
print(f"✓ Camadas treináveis: {trainable}")

# Callbacks
callbacks_ft = [
    EarlyStopping(
        monitor='val_loss',
        patience=15,  # Mais paciência para fine-tuning
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=7,
        min_lr=1e-8,
        verbose=1
    ),
    ModelCheckpoint(
        'best_model_ft_V2.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
]

print(f"\n🚀 TREINANDO Fine-Tuning...")
print(f"⏱️  Tempo estimado: 25-40 minutos\n")

history_ft = model_ft.fit(
    train_generator_ft,
    validation_data=val_generator_ft,
    epochs=EPOCHS,
    callbacks=callbacks_ft,
    class_weight=class_weight_dict,
    verbose=1
)

# Avaliar
test_loss_ft, test_acc_ft = model_ft.evaluate(test_generator, verbose=0)

print(f"\n" + "="*70)
print(f"✅ FINE-TUNING COMPLETO!")
print(f"="*70)
print(f"📊 Acurácia no teste: {test_acc_ft:.4f} ({test_acc_ft*100:.2f}%)")
print(f"📊 Loss no teste: {test_loss_ft:.4f}")
print(f"💾 Modelo salvo: best_model_ft_V2.h5")

# ============================================================
# COMPARAÇÃO FINAL
# ============================================================

print("\n" + "="*70)
print("🏆 COMPARAÇÃO FINAL - DATASET V2")
print("="*70)

results = [
    ("Feature Extraction V2", test_acc_fe, test_loss_fe, "best_model_fe_V2.h5"),
    ("Fine-Tuning V2", test_acc_ft, test_loss_ft, "best_model_ft_V2.h5")
]

results_sorted = sorted(results, key=lambda x: x[1], reverse=True)

print(f"\n🥇 RANKING:")
for i, (name, acc, loss, filename) in enumerate(results_sorted, 1):
    emoji = "🥇" if i == 1 else "🥈"
    print(f"\n{emoji} {i}. {name}")
    print(f"   Acurácia: {acc:.4f} ({acc*100:.2f}%)")
    print(f"   Loss: {loss:.4f}")
    print(f"   Arquivo: {filename}")

# Salvar resultados
with open('training_results_V2.txt', 'w') as f:
    f.write("RESULTADOS DO TREINAMENTO - DATASET V2 (360 imagens)\n")
    f.write("="*70 + "\n\n")
    for name, acc, loss, filename in results:
        f.write(f"{name}:\n")
        f.write(f"  Acurácia: {acc:.4f} ({acc*100:.2f}%)\n")
        f.write(f"  Loss: {loss:.4f}\n")
        f.write(f"  Arquivo: {filename}\n\n")

print(f"\n💾 Resultados salvos em: training_results_V2.txt")

print("\n" + "="*70)
print("✅ RETREINAMENTO COMPLETO!")
print("="*70)
print(f"\n📁 Modelos V2 criados:")
print(f"   - best_model_fe_V2.h5 (Feature Extraction)")
print(f"   - best_model_ft_V2.h5 (Fine-Tuning)")
print(f"\n📁 Modelos V1 backupeados em:")
print(f"   - models_backup_v1/")
print(f"\n🎯 Próximo passo:")
print(f"   python compare_all_models.py")
print("\n")
