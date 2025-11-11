#!/usr/bin/env python3
"""
Script de Predição - Modelo Bristol Stool Scale
Usa o melhor modelo: best_model_fe.h5(68.72% acurácia)
"""

import sys
from pathlib import Path
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Configurações
MODEL_PATH = 'best_model_fe.h5'
IMG_SIZE = (224, 224)

# Mapeamento de classes
BRISTOL_TYPES = {
    0: "Tipo 1 - Pedaços duros separados (constipação severa)",
    1: "Tipo 2 - Forma de salsicha, mas irregular",
    2: "Tipo 3 - Forma de salsicha com rachaduras",
    3: "Tipo 4 - Forma de salsicha ou cobra, lisa e macia (IDEAL)",
    4: "Tipo 5 - Pedaços macios com bordas bem definidas",
    5: "Tipo 6 - Pedaços fofos com bordas irregulares",
    6: "Tipo 7 - Aquoso, sem pedaços sólidos (diarreia)"
}

def load_and_preprocess_image(img_path):
    """
    Carrega e preprocessa uma imagem para predição
    """
    # Carregar imagem
    img = image.load_img(img_path, target_size=IMG_SIZE)

    # Converter para array e normalizar
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0

    # Adicionar dimensão de batch
    img_array = np.expand_dims(img_array, axis=0)

    return img_array

def predict(img_path, model):
    """
    Faz predição para uma imagem
    """
    # Preprocessar imagem
    img_array = load_and_preprocess_image(img_path)

    # Fazer predição
    predictions = model.predict(img_array, verbose=0)

    # Obter classe predita e confiança
    predicted_class = np.argmax(predictions[0])
    confidence = predictions[0][predicted_class] * 100

    # Obter top 3 predições
    top_3_indices = np.argsort(predictions[0])[-3:][::-1]
    top_3_predictions = [
        (idx, BRISTOL_TYPES[idx], predictions[0][idx] * 100)
        for idx in top_3_indices
    ]

    return predicted_class, confidence, top_3_predictions

def main():
    """
    Função principal
    """
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("Uso: python predict.py <caminho_da_imagem>")
        print("\nExemplo:")
        print("  python predict.py dataset/exemplo.jpg")
        sys.exit(1)

    img_path = sys.argv[1]

    # Verificar se arquivo existe
    if not Path(img_path).exists():
        print(f"❌ Erro: Arquivo não encontrado: {img_path}")
        sys.exit(1)

    # Carregar modelo
    print("="*70)
    print("🔬 CLASSIFICADOR DE ESCALA DE BRISTOL")
    print("="*70)
    print(f"\n📂 Carregando modelo: {MODEL_PATH}")

    try:
        model = load_model(MODEL_PATH)
        print(f"✓ Modelo carregado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        sys.exit(1)

    # Fazer predição
    print(f"\n🖼️  Analisando imagem: {img_path}")

    try:
        predicted_class, confidence, top_3 = predict(img_path, model)
    except Exception as e:
        print(f"❌ Erro ao processar imagem: {e}")
        sys.exit(1)

    # Mostrar resultado
    print("\n" + "="*70)
    print("📊 RESULTADO DA ANÁLISE")
    print("="*70)

    print(f"\n🎯 PREDIÇÃO PRINCIPAL:")
    print(f"   {BRISTOL_TYPES[predicted_class]}")
    print(f"   Confiança: {confidence:.2f}%")

    print(f"\n📋 TOP 3 PREDIÇÕES:")
    for i, (idx, desc, conf) in enumerate(top_3, 1):
        emoji = "🥇" if i == 1 else ("🥈" if i == 2 else "🥉")
        print(f"   {emoji} {desc}")
        print(f"      Confiança: {conf:.2f}%")

    # Interpretação clínica
    print(f"\n💡 INTERPRETAÇÃO CLÍNICA:")
    if predicted_class in [0, 1]:
        print("   ⚠️  Possível constipação - Considere aumentar fibras e hidratação")
    elif predicted_class in [2, 3]:
        print("   ✅ Normal - Fezes saudáveis")
    elif predicted_class == 4:
        print("   ⚡ Tendência a fezes mais soltas - Monitorar")
    else:
        print("   ⚠️  Diarreia ou fezes muito soltas - Atenção necessária")

    print("\n" + "="*70)
    print("✅ ANÁLISE COMPLETA!")
    print("="*70)
    print()

if __name__ == "__main__":
    main()
