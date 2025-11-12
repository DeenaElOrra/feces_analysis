# backend/services/ml_service.py
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image


class MLService:
    def __init__(self, model_path: str):
        print(f"Carregando modelo de: {model_path}")
        self.model = load_model(model_path)
        print("Modelo carregado com sucesso!")

        # Recomendações por tipo Bristol
        self.recomendacoes = {
            1: [
                "Constipação severa - Hidratação inadequada",
                "Aumentar consumo de fibras (frutas, vegetais, grãos integrais)",
                "Beber pelo menos 2 litros de água por dia",
                "Consulte um médico se persistir por mais de 3 dias"
            ],
            2: [
                "Constipação leve",
                "Aumentar consumo de fibras",
                "Melhorar hidratação (1.5-2L de água/dia)",
                "Praticar atividade física regular"
            ],
            3: [
                "Normal - Formato ideal",
                "Parabéns! Suas fezes estão saudáveis",
                "Mantenha a alimentação equilibrada",
                "Continue bebendo bastante água"
            ],
            4: [
                "Normal - Textura ideal",
                "Excelente! Trato digestivo funcionando bem",
                "Mantenha seus hábitos alimentares",
                "Continue a rotina de hidratação"
            ],
            5: [
                "Fezes amolecidas - Leve diarreia",
                "Pode indicar falta de fibras ou excesso de líquidos",
                "Reduzir alimentos muito gordurosos",
                "Se persistir, consulte um médico"
            ],
            6: [
                "Diarreia leve",
                "Aumentar consumo de probióticos",
                "Evitar alimentos irritantes",
                "Consulte um médico se durar mais de 2 dias"
            ],
            7: [
                "Diarreia severa",
                "CONSULTE UM MÉDICO IMEDIATAMENTE",
                "Manter hidratação com soro caseiro",
                "Pode indicar infecção ou intolerância alimentar"
            ]
        }

    def preprocess_image(self, image_path: str):
        """
        Preprocessa imagem para o modelo
        """
        img = Image.open(image_path)
        img = img.resize((224, 224))  # VGG16 input size
        img_array = np.array(img)

        # Se imagem for grayscale, converter para RGB
        if len(img_array.shape) == 2:
            img_array = np.stack([img_array] * 3, axis=-1)

        # Normalizar
        img_array = img_array.astype('float32') / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def classify(self, image_path: str) -> dict:
        """
        Classifica imagem e retorna resultado
        """
        # Preprocessar
        img_array = self.preprocess_image(image_path)

        # Predição
        predictions = self.model.predict(img_array, verbose=0)

        # Tipo Bristol (1-7)
        tipo_bristol = int(np.argmax(predictions[0])) + 1  # +1 porque modelo retorna 0-6

        # Confiança (%)
        confianca = float(predictions[0].max() * 100)

        # Recomendações
        recomendacoes = self.recomendacoes.get(tipo_bristol, [])

        return {
            "tipo_bristol": tipo_bristol,
            "confianca": round(confianca, 2),
            "recomendacoes": recomendacoes,
            "probabilidades": {i+1: float(predictions[0][i]*100) for i in range(7)}
        }
