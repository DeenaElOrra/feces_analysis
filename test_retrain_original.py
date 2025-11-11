#!/usr/bin/env python3
"""
Teste: Retreinar APENAS Feature Extraction com dataset ORIGINAL (211 imgs)
Para confirmar que o código de treino está funcionando
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

print("="*70)
print("🧪 TESTE: Retreinar com Dataset ORIGINAL (211 imagens)")
print("="*70)
print("\nObjetivo: Confirmar que código está OK")
print("Esperado: ~68-70% de acurácia\n")

# Configurações
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 30  # Menos épocas para teste rápido

# Carregar dados ORIGINAIS
df = pd.read_csv('labels.csv')
print(f"✓ Dataset carregado: {len(df)} imagens")

# Ajustar paths
df['filename'] = df['filename'].apply(lambda x: f'dataset/{x}' if not x.startswith('dataset/') else x)
df['bristol_type_str'] = df['bristol_type'].astype(str)

# Distribuição
print(f"\n📈 Distribuição:")
for tipo in range(1, 8):
    count = len(df[df['bristol_type'] == tipo])
    print(f"  Tipo {tipo}: {count} imagens")

# Split
train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    stratify=df['bristol_type'],
    random_state=42
)

print(f"\n✓ Train: {len(train_df)} | Test: {len(test_df)}")

# Geradores
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

test_datagen = ImageDataGenerator(rescale=1./255)

train_gen = train_datagen.flow_from_dataframe(
    train_df, x_col='filename', y_col='bristol_type_str',
    target_size=IMG_SIZE, batch_size=BATCH_SIZE,
    class_mode='categorical', shuffle=True, seed=42, subset='training'
)

val_gen = train_datagen.flow_from_dataframe(
    train_df, x_col='filename', y_col='bristol_type_str',
    target_size=IMG_SIZE, batch_size=BATCH_SIZE,
    class_mode='categorical', shuffle=False, subset='validation'
)

test_gen = test_datagen.flow_from_dataframe(
    test_df, x_col='filename', y_col='bristol_type_str',
    target_size=IMG_SIZE, batch_size=BATCH_SIZE,
    class_mode='categorical', shuffle=False
)

# Class Weights
y_train = train_df['bristol_type'].values
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_train),
    y=y_train
)
class_weight_dict = dict(enumerate(class_weights))

# Modelo
print(f"\n🏗️  Criando modelo Feature Extraction...")
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
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

print(f"✓ Modelo criado!")

# Callbacks
callbacks = [
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5),
    ModelCheckpoint('test_model_original.h5', monitor='val_accuracy', save_best_only=True)
]

# Treinar
print(f"\n🚀 TREINANDO (30 épocas)...\n")

history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS,
    callbacks=callbacks,
    class_weight=class_weight_dict,
    verbose=2
)

# Avaliar
test_loss, test_acc = model.evaluate(test_gen, verbose=0)

print(f"\n" + "="*70)
print(f"✅ TESTE COMPLETO!")
print(f"="*70)
print(f"\n📊 RESULTADO:")
print(f"   Acurácia: {test_acc:.4f} ({test_acc*100:.2f}%)")
print(f"   Loss: {test_loss:.4f}")

print(f"\n📊 COMPARAÇÃO:")
print(f"   Esperado:   ~68-70%")
print(f"   Obtido:      {test_acc*100:.2f}%")

if test_acc >= 0.65:
    print(f"\n✅ CÓDIGO ESTÁ OK!")
    print(f"   O problema foi o dataset desbalanceado!")
else:
    print(f"\n⚠️  Acurácia abaixo do esperado")
    print(f"   Pode ter outro problema no código")

print(f"\n💾 Modelo salvo: test_model_original.h5")
print()
