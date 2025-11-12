"""
AWS Lambda Function - Classificador de Fezes
Handler para API Gateway
"""

import json
import base64
import numpy as np
from PIL import Image
from io import BytesIO
import tensorflow as tf
from tensorflow.keras.models import load_model

# Carregar modelo uma vez (fora do handler)
MODEL = None

def load_classification_model():
    """Carrega modelo (cache global)"""
    global MODEL
    if MODEL is None:
        MODEL = load_model('best_model_fe.h5')
    return MODEL

def preprocess_image(image_data):
    """Preprocessa imagem base64 para o modelo"""
    # Decodificar base64
    img_bytes = base64.b64decode(image_data)
    img = Image.open(BytesIO(img_bytes))

    # Redimensionar
    img = img.resize((224, 224))

    # Converter para RGB se necessário
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Converter para array e normalizar
    img_array = np.array(img) / 255.0

    # Adicionar dimensão de batch
    img_array = np.expand_dims(img_array, axis=0)

    return img_array

def lambda_handler(event, context):
    """
    Handler principal da Lambda

    Espera um evento com:
    {
        "body": {
            "image": "base64_encoded_image"
        }
    }
    """

    try:
        # Parse do body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        # Validar input
        if 'image' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing image field in request body'
                })
            }

        # Carregar modelo
        model = load_classification_model()

        # Preprocessar imagem
        img_array = preprocess_image(body['image'])

        # Fazer predição
        predictions = model.predict(img_array, verbose=0)

        # Processar resultado
        predicted_class = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][predicted_class] * 100)

        # Top 3
        top_3_indices = np.argsort(predictions[0])[-3:][::-1]
        top_3 = [
            {
                'type': int(idx) + 1,  # Bristol types são 1-7, não 0-6
                'confidence': float(predictions[0][idx] * 100)
            }
            for idx in top_3_indices
        ]

        # Mapeamento de tipos
        bristol_names = {
            0: "Tipo 1 - Constipação Severa",
            1: "Tipo 2 - Constipação Leve",
            2: "Tipo 3 - Normal",
            3: "Tipo 4 - Ideal",
            4: "Tipo 5 - Falta de Fibra",
            5: "Tipo 6 - Leve Diarreia",
            6: "Tipo 7 - Diarreia"
        }

        # Resposta
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'prediction': {
                    'type': predicted_class + 1,
                    'name': bristol_names[predicted_class],
                    'confidence': confidence
                },
                'top_3': top_3
            })
        }

        return response

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
