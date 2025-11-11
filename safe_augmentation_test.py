#!/usr/bin/env python3
"""
TESTE SEGURO de Data Augmentation Direcionado

Este script:
1. NÃO modifica o dataset original
2. NÃO substitui o modelo atual
3. Cria arquivos NOVOS com sufixo '_test'
4. Você pode deletar tudo depois se não gostar
"""

import pandas as pd
from pathlib import Path
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
import numpy as np
from PIL import Image

# Configurações
ORIGINAL_CSV = 'labels.csv'
NEW_CSV = 'labels_augmented_TEST.csv'  # Nome diferente!
NEW_FOLDER = 'dataset_augmented_TEST'  # Pasta diferente!

print("="*60)
print("🛡️  MODO SEGURO - TESTE DE AUGMENTATION")
print("="*60)
print()
print("✅ Arquivos ORIGINAIS serão preservados:")
print(f"   - {ORIGINAL_CSV}")
print(f"   - dataset/")
print(f"   - best_model_fe.h5")
print()
print("📁 Arquivos NOVOS serão criados:")
print(f"   - {NEW_CSV}")
print(f"   - {NEW_FOLDER}/")
print()
print("❌ SE NÃO GOSTAR, é só deletar:")
print(f"   rm -rf {NEW_FOLDER}")
print(f"   rm {NEW_CSV}")
print()
print("="*60)

# Carregar dados originais
df = pd.read_csv(ORIGINAL_CSV)
dataset_path = Path('dataset')

print(f"\n📊 Dataset original: {len(df)} imagens")
print(f"Distribuição:")
print(df['bristol_type'].value_counts().sort_index())

# Criar pasta para imagens aumentadas
output_path = Path(NEW_FOLDER)
output_path.mkdir(exist_ok=True)

# Configurar augmentation agressivo para classes problemáticas
aggressive_datagen = ImageDataGenerator(
    rotation_range=40,
    width_shift_range=0.3,
    height_shift_range=0.3,
    shear_range=0.3,
    zoom_range=0.3,
    horizontal_flip=True,
    brightness_range=[0.7, 1.3],
    fill_mode='nearest'
)

# Classes problemáticas que precisam de mais dados
CONFUSED_CLASSES = [2, 3, 4]  # Tipo 2 (poucos dados), Tipos 3 e 4 (confundem)
TARGET_COUNT = 30  # Gerar 30 imagens sintéticas de cada

print(f"\n🎯 Gerando imagens sintéticas para tipos: {CONFUSED_CLASSES}")
print(f"   {TARGET_COUNT} imagens por tipo")

augmented_data = []

for bristol_type in CONFUSED_CLASSES:
    class_images = df[df['bristol_type'] == bristol_type]
    original_count = len(class_images)

    print(f"\n📸 Tipo {bristol_type}:")
    print(f"   Original: {original_count} imagens")

    generated = 0

    for idx, row in class_images.iterrows():
        img_path = dataset_path / row['filename']

        # Carregar imagem
        img = load_img(img_path, target_size=(224, 224))
        img_array = img_to_array(img)
        img_array = img_array.reshape((1,) + img_array.shape)

        # Quantas gerar desta imagem
        per_image = (TARGET_COUNT // original_count) + 1

        # Gerar variações
        for i, batch in enumerate(aggressive_datagen.flow(img_array, batch_size=1)):
            if generated >= TARGET_COUNT:
                break

            # Salvar imagem sintética
            aug_filename = f"aug_type{bristol_type}_orig{idx}_var{i}.png"
            aug_path = output_path / aug_filename

            # Converter e salvar
            aug_img = Image.fromarray((batch[0] * 255).astype('uint8'))
            aug_img.save(aug_path)

            # Adicionar ao novo dataframe
            augmented_data.append({
                'filename': str(Path(NEW_FOLDER) / aug_filename),
                'bristol_type': bristol_type
            })

            generated += 1

            if generated >= TARGET_COUNT:
                break

        if generated >= TARGET_COUNT:
            break

    print(f"   Geradas: {generated} imagens sintéticas")
    print(f"   Total agora: {original_count + generated} imagens")

# Combinar dados originais com sintéticos
print(f"\n📊 Criando novo CSV combinado...")
aug_df = pd.DataFrame(augmented_data)

# Ajustar paths do dataset original para incluir pasta
df_copy = df.copy()
df_copy['filename'] = df_copy['filename'].apply(lambda x: str(Path('dataset') / x))

# Combinar
combined_df = pd.concat([df_copy, aug_df], ignore_index=True)
combined_df.to_csv(NEW_CSV, index=False)

print(f"\n✅ TESTE COMPLETO!")
print("="*60)
print(f"📂 Dataset original (intocado): {len(df)} imagens")
print(f"📂 Dataset aumentado (novo): {len(combined_df)} imagens")
print(f"   +{len(aug_df)} imagens sintéticas adicionadas")
print()
print("Distribuição final:")
print(combined_df['bristol_type'].value_counts().sort_index())
print()
print("="*60)
print("🔄 PRÓXIMOS PASSOS:")
print("="*60)
print()
print("1️⃣  TESTAR o novo dataset:")
print(f"   Edite o notebook para usar '{NEW_CSV}'")
print(f"   Treine um NOVO modelo (não sobrescreve o atual)")
print()
print("2️⃣  COMPARAR resultados:")
print(f"   Modelo atual: 70.14% acurácia")
print(f"   Modelo novo: ??? (espera-se 75-80%)")
print()
print("3️⃣  SE MELHORAR:")
print(f"   mv {NEW_CSV} labels.csv")
print(f"   mv {NEW_FOLDER} dataset_augmented")
print()
print("4️⃣  SE PIORAR:")
print(f"   rm -rf {NEW_FOLDER}")
print(f"   rm {NEW_CSV}")
print(f"   # Seu modelo original está 100% intacto!")
print()
print("="*60)
