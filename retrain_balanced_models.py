#!/usr/bin/env python3
"""
Retreinar Modelos V2 com Dataset BALANCEADO
Dataset: 222 imagens balanceadas (labels_v2_balanced.csv)
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
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from collections import Counter

print("="*70)
print("🚀 RETREINAMENTO COM DATASET BALANCEADO")
print("="*70)
print("\n📊 Dataset: labels_v2_balanced.csv (222 imagens)")
print("⚖️  Distribuição balanceada entre os tipos\n")

# Configurações
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 50

# Carregar dataset BALANCEADO
df = pd.read_csv('labels_v2_balanced.csv')
print(f"✓ Dataset carregado: {len(df)} imagens")

# Ajustar paths
df['filename'] = df['filename'].apply(lambda x: f'dataset/{x}' if not x.startswith('dataset/') else x)
df['bristol_type_str'] = df['bristol_type'].astype(str)

# Mostrar distribuição
print(f"\n📈 Distribuição:")
counter = Counter(df['bristol_type'])
for tipo in range(1, 8):
    count = counter.get(tipo, 0)
    pct = (count / len(df)) * 100
    print(f"  Tipo {tipo}: {count:3d} ({pct:5.1f}%)")

# Split stratificado
train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    stratify=df['bristol_type'],
    random_state=42
)

print(f"\n✓ Train: {len(train_df)} imagens")
print(f"✓ Test:  {len(test_df)} imagens")

# Geradores de dados
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

# Class weights
y_train = train_df['bristol_type'].values
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_train),
    y=y_train
)
class_weight_dict = dict(enumerate(class_weights))

print(f"\n⚖️  Class weights:")
for tipo, weight in class_weight_dict.items():
    print(f"  Tipo {tipo+1}: {weight:.2f}")

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

    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

model_fe = create_feature_extraction_model()

print(f"\n✓ Modelo criado!")
print(f"   Parâmetros treináveis: {model_fe.count_params():,}")

# Callbacks
callbacks_fe = [
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5),
    ModelCheckpoint('best_model_fe_balanced.h5', monitor='val_accuracy', save_best_only=True)
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
print(f"\n📊 RESULTADOS:")
print(f"   Acurácia: {test_acc_fe:.4f} ({test_acc_fe*100:.2f}%)")
print(f"   Loss: {test_loss_fe:.4f}")

# ============================================================
# MODELO 2: FINE-TUNING
# ============================================================

print("\n" + "="*70)
print("🏗️  MODELO 2: FINE-TUNING (VGG16 Parcialmente Treinável)")
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
    base_model.trainable = True
    for layer in base_model.layers[:-4]:
        layer.trainable = False

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

    model.compile(
        optimizer=Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

model_ft = create_fine_tuning_model()

print(f"\n✓ Modelo criado!")
print(f"   Parâmetros treináveis: {model_ft.count_params():,}")

# Callbacks
callbacks_ft = [
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5),
    ModelCheckpoint('best_model_ft_balanced.h5', monitor='val_accuracy', save_best_only=True)
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
print(f"\n📊 RESULTADOS:")
print(f"   Acurácia: {test_acc_ft:.4f} ({test_acc_ft*100:.2f}%)")
print(f"   Loss: {test_loss_ft:.4f}")

# ============================================================
# COMPARAÇÃO FINAL
# ============================================================

print("\n" + "="*70)
print("🏆 COMPARAÇÃO: BALANCEADO vs DESBALANCEADO")
print("="*70)

print(f"\n📊 MODELOS V2 DESBALANCEADOS (360 imgs):")
print(f"   Feature Extraction: 37.22%")
print(f"   Fine-Tuning:        20.00%")

print(f"\n📊 MODELOS V2 BALANCEADOS (222 imgs):")
print(f"   Feature Extraction: {test_acc_fe*100:.2f}%  [{(test_acc_fe - 0.3722)*100:+.2f}%]")
print(f"   Fine-Tuning:        {test_acc_ft*100:.2f}%  [{(test_acc_ft - 0.2000)*100:+.2f}%]")

print(f"\n📊 MODELO V1 ORIGINAL (211 imgs):")
print(f"   Feature Extraction: 68.72%")

# Determinar melhor modelo
all_results = [
    ('V1 Feature Extraction', 0.6872),
    ('V2 Balanced Feature Extraction', test_acc_fe),
    ('V2 Balanced Fine-Tuning', test_acc_ft)
]

best = max(all_results, key=lambda x: x[1])

print(f"\n🥇 MELHOR MODELO: {best[0]}")
print(f"   Acurácia: {best[1]*100:.2f}%")

# Salvar resultados
with open('balanced_training_results.txt', 'w') as f:
    f.write("RESULTADOS - MODELOS BALANCEADOS\n")
    f.write("="*70 + "\n\n")
    f.write(f"Dataset: labels_v2_balanced.csv (222 imagens)\n\n")
    f.write(f"Feature Extraction: {test_acc_fe:.4f} ({test_acc_fe*100:.2f}%)\n")
    f.write(f"Fine-Tuning:        {test_acc_ft:.4f} ({test_acc_ft*100:.2f}%)\n\n")
    f.write(f"Melhoria vs V2 Desbalanceado:\n")
    f.write(f"  Feature Extraction: {(test_acc_fe - 0.3722)*100:+.2f}%\n")
    f.write(f"  Fine-Tuning:        {(test_acc_ft - 0.2000)*100:+.2f}%\n")

print(f"\n💾 Modelos salvos:")
print(f"   - best_model_fe_balanced.h5")
print(f"   - best_model_ft_balanced.h5")
print(f"\n💾 Resultados salvos: balanced_training_results.txt")

print("\n" + "="*70)
print("✅ RETREINAMENTO COMPLETO!")
print("="*70)
print()
