#!/usr/bin/env python3
"""
Script de Predição RÁPIDO - Mantém modelo em memória
Modo interativo: Carrega modelo uma vez, analisa múltiplas imagens
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
    """Carrega e preprocessa uma imagem para predição"""
    img = image.load_img(img_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict(img_path, model):
    """Faz predição para uma imagem"""
    img_array = load_and_preprocess_image(img_path)
    predictions = model.predict(img_array, verbose=0)

    predicted_class = np.argmax(predictions[0])
    confidence = predictions[0][predicted_class] * 100

    top_3_indices = np.argsort(predictions[0])[-3:][::-1]
    top_3_predictions = [
        (idx, BRISTOL_TYPES[idx], predictions[0][idx] * 100)
        for idx in top_3_indices
    ]

    return predicted_class, confidence, top_3_predictions

def print_result(img_path, predicted_class, confidence, top_3):
    """Imprime resultado formatado"""
    print("\n" + "="*70)
    print(f"🖼️  {Path(img_path).name}")
    print("="*70)
    print(f"\n🎯 {BRISTOL_TYPES[predicted_class]}")
    print(f"   Confiança: {confidence:.1f}%")

    if len(top_3) > 1 and top_3[1][2] > 15:  # Se 2ª opção tem >15%
        print(f"\n   Também pode ser:")
        print(f"   • {BRISTOL_TYPES[top_3[1][0]]} ({top_3[1][2]:.1f}%)")

def main():
    """Função principal"""

    print("="*70)
    print("🔬 CLASSIFICADOR DE ESCALA DE BRISTOL - MODO RÁPIDO")
    print("="*70)

    # Carregar modelo UMA VEZ
    print(f"\n⏳ Carregando modelo... (só acontece uma vez)")
    try:
        model = load_model(MODEL_PATH)
        print(f"✅ Modelo carregado!\n")
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        sys.exit(1)

    # Modo 1: Um arquivo passado como argumento
    if len(sys.argv) > 1:
        img_path = sys.argv[1]

        if not Path(img_path).exists():
            print(f"❌ Arquivo não encontrado: {img_path}")
            sys.exit(1)

        try:
            predicted_class, confidence, top_3 = predict(img_path, model)
            print_result(img_path, predicted_class, confidence, top_3)
        except Exception as e:
            print(f"❌ Erro ao processar imagem: {e}")
            sys.exit(1)

    # Modo 2: Interativo - analisa múltiplas imagens
    else:
        print("💡 Modo interativo ativado!")
        print("   Digite o caminho da imagem (ou 'sair' para terminar)\n")

        while True:
            try:
                img_path = input("📂 Imagem: ").strip()

                if img_path.lower() in ['sair', 'exit', 'quit', 'q']:
                    print("\n👋 Até logo!")
                    break

                if not img_path:
                    continue

                # Remover aspas se usuário copiou/colou com aspas
                img_path = img_path.strip('"').strip("'")

                if not Path(img_path).exists():
                    print(f"❌ Arquivo não encontrado: {img_path}\n")
                    continue

                predicted_class, confidence, top_3 = predict(img_path, model)
                print_result(img_path, predicted_class, confidence, top_3)
                print()

            except KeyboardInterrupt:
                print("\n\n👋 Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro: {e}\n")

if __name__ == "__main__":
    main()
