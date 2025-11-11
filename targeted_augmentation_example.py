#!/usr/bin/env python3
"""
Exemplo de Data Augmentation Direcionado para Classes Confusas

Este script mostra como aplicar transformações mais agressivas
nas classes que o modelo está confundindo (Tipo 3 e Tipo 4)
"""

import pandas as pd
from pathlib import Path
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
import numpy as np
from PIL import Image
import os

# Carregar dados
df = pd.read_csv('labels.csv')
dataset_path = Path('dataset')

# ============================================================
# ESTRATÉGIA 1: Augmentation Mais Agressivo para Classes Confusas
# ============================================================

def create_class_specific_generators():
    """
    Cria geradores com augmentation diferente por classe
    """

    # Augmentation NORMAL (para classes que estão indo bem: 1, 7)
    normal_augmentation = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,      # Rotação moderada
        zoom_range=0.15,        # Zoom moderado
        horizontal_flip=True,
        brightness_range=[0.9, 1.1]
    )

    # Augmentation AGRESSIVO (para classes confusas: 3, 4)
    aggressive_augmentation = ImageDataGenerator(
        rescale=1./255,
        rotation_range=40,          # 🔥 Rotação mais forte
        width_shift_range=0.3,      # 🔥 Mais deslocamento
        height_shift_range=0.3,
        shear_range=0.3,            # 🔥 Mais distorção
        zoom_range=0.3,             # 🔥 Mais zoom
        horizontal_flip=True,
        vertical_flip=False,        # Não vira de cabeça pra baixo
        brightness_range=[0.7, 1.3], # 🔥 Mais variação de luz
        fill_mode='nearest'
    )

    # Augmentation para Tipo 2 (precisa de mais dados)
    extreme_augmentation = ImageDataGenerator(
        rescale=1./255,
        rotation_range=50,          # 🔥🔥 Muito agressivo
        width_shift_range=0.4,
        height_shift_range=0.4,
        shear_range=0.4,
        zoom_range=[0.7, 1.3],      # 🔥🔥 Zoom in e out
        horizontal_flip=True,
        brightness_range=[0.6, 1.4],
        channel_shift_range=30.0,   # 🔥🔥 Muda cores
        fill_mode='reflect'
    )

    return normal_augmentation, aggressive_augmentation, extreme_augmentation


# ============================================================
# ESTRATÉGIA 2: Gerar Imagens Sintéticas das Classes Confusas
# ============================================================

def generate_synthetic_images_for_confused_classes(
    confused_types=[3, 4],  # Classes que confundem
    target_count=50,        # Quantas gerar de cada
    output_dir='dataset_augmented'
):
    """
    Gera imagens sintéticas extras para classes confusas
    """

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Augmentation agressivo
    datagen = ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.3,
        height_shift_range=0.3,
        shear_range=0.3,
        zoom_range=0.3,
        horizontal_flip=True,
        brightness_range=[0.7, 1.3],
        fill_mode='nearest'
    )

    augmented_data = []

    for bristol_type in confused_types:
        print(f"\n🔄 Gerando {target_count} imagens sintéticas para Tipo {bristol_type}...")

        # Pegar imagens originais dessa classe
        class_images = df[df['bristol_type'] == bristol_type]

        generated = 0
        for idx, row in class_images.iterrows():
            img_path = dataset_path / row['filename']

            # Carregar imagem
            img = load_img(img_path, target_size=(224, 224))
            img_array = img_to_array(img)
            img_array = img_array.reshape((1,) + img_array.shape)

            # Gerar variações
            variations_per_image = target_count // len(class_images) + 1

            for i, batch in enumerate(datagen.flow(img_array, batch_size=1)):
                if generated >= target_count:
                    break

                # Salvar imagem sintética
                aug_filename = f"aug_type{bristol_type}_{idx}_{i}.png"
                aug_path = output_path / aug_filename

                # Converter de volta para imagem
                aug_img = Image.fromarray((batch[0] * 255).astype('uint8'))
                aug_img.save(aug_path)

                # Adicionar ao dataframe
                augmented_data.append({
                    'filename': aug_filename,
                    'bristol_type': bristol_type,
                    'is_synthetic': True
                })

                generated += 1

                if generated >= target_count:
                    break

        print(f"✓ Geradas {generated} imagens para Tipo {bristol_type}")

    # Criar novo CSV com dados aumentados
    aug_df = pd.DataFrame(augmented_data)
    combined_df = pd.concat([df, aug_df], ignore_index=True)
    combined_df.to_csv('labels_augmented.csv', index=False)

    print(f"\n✓ Total de imagens após augmentation: {len(combined_df)}")
    print(f"✓ Dataset original: {len(df)}")
    print(f"✓ Imagens sintéticas adicionadas: {len(aug_df)}")

    return combined_df


# ============================================================
# ESTRATÉGIA 3: Augmentation Focado na Diferença Entre Classes
# ============================================================

def create_discriminative_augmentation():
    """
    Cria augmentation que enfatiza as DIFERENÇAS entre Tipo 3 e Tipo 4

    Ideia: Se Tipo 3 e 4 diferem por textura/cor, varie essas características
    """

    # Para Tipo 3: Enfatizar características únicas
    type3_augmentation = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        zoom_range=0.25,
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],
        # 🔍 Foco em variações de textura
        shear_range=0.2,
        fill_mode='nearest'
    )

    # Para Tipo 4: Enfatizar características únicas
    type4_augmentation = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        zoom_range=0.25,
        horizontal_flip=True,
        # 🔍 Foco em variações de cor/brilho
        brightness_range=[0.7, 1.3],
        channel_shift_range=20.0,
        fill_mode='nearest'
    )

    return type3_augmentation, type4_augmentation


# ============================================================
# ESTRATÉGIA 4: Mixup Entre Classes Próximas (Avançado)
# ============================================================

def apply_mixup_for_boundary_learning(alpha=0.2):
    """
    Mixup: Mistura duas imagens de classes diferentes

    Ajuda o modelo a aprender as FRONTEIRAS entre classes confusas
    Exemplo: 80% Tipo 3 + 20% Tipo 4 = imagem híbrida

    Isso força o modelo a focar nas diferenças sutis!
    """

    print("🎨 Mixup ajuda a aprender fronteiras entre classes!")
    print("Exemplo: misturar Tipo 3 e Tipo 4 com pesos variados")
    print("Isso treina o modelo a distinguir melhor as classes vizinhas")

    # Implementação simplificada
    # (Na prática, você faria isso durante o treinamento)

    return f"Use mixup com alpha={alpha} durante o treino"


# ============================================================
# EXEMPLO DE USO
# ============================================================

if __name__ == "__main__":
    print("="*60)
    print("DATA AUGMENTATION DIRECIONADO PARA CLASSES CONFUSAS")
    print("="*60)

    print("\n📊 Análise do problema:")
    print("- Tipo 4 confunde com Tipo 3 (9 casos)")
    print("- Tipo 3 tem precision baixa (49%)")
    print("- Tipo 2 tem poucos dados (12 imagens)")

    print("\n🎯 Estratégias disponíveis:")
    print("1. Augmentation mais agressivo para Tipos 3 e 4")
    print("2. Gerar imagens sintéticas extras dessas classes")
    print("3. Augmentation focado nas diferenças entre classes")
    print("4. Mixup para aprender fronteiras entre classes")

    print("\n" + "="*60)
    print("GERANDO IMAGENS SINTÉTICAS...")
    print("="*60)

    # Gerar imagens para classes confusas
    augmented_df = generate_synthetic_images_for_confused_classes(
        confused_types=[2, 3, 4],  # Classes problemáticas
        target_count=30,           # 30 imagens sintéticas de cada
        output_dir='dataset_augmented'
    )

    print("\n✓ Dataset aumentado salvo em 'labels_augmented.csv'")
    print("✓ Imagens sintéticas salvas em 'dataset_augmented/'")

    print("\n" + "="*60)
    print("PRÓXIMO PASSO:")
    print("="*60)
    print("1. Use 'labels_augmented.csv' no treino")
    print("2. Treine novamente o modelo")
    print("3. A acurácia deve subir para ~75-80%!")
