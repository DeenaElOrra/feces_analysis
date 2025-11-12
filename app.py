#!/usr/bin/env python3
"""
Web App - Classificador de Fezes (Escala de Bristol)
Deploy com Streamlit Cloud
"""

import streamlit as st
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image
import os

# Configuração da página
st.set_page_config(
    page_title="Classificador Bristol",
    page_icon="💩",
    layout="centered"
)

# Cache do modelo (carrega só uma vez)
@st.cache_resource
def load_classification_model():
    """Carrega o modelo treinado"""
    return load_model('best_model_fe.h5')

# Mapeamento de classes
BRISTOL_TYPES = {
    0: {
        "nome": "Tipo 1 - Constipação Severa",
        "desc": "Pedaços duros separados, como nozes",
        "status": "⚠️ Anormal",
        "cor": "red"
    },
    1: {
        "nome": "Tipo 2 - Constipação Leve",
        "desc": "Forma de salsicha, mas irregular e com rachaduras",
        "status": "⚠️ Levemente anormal",
        "cor": "orange"
    },
    2: {
        "nome": "Tipo 3 - Normal",
        "desc": "Forma de salsicha com rachaduras na superfície",
        "status": "✅ Normal",
        "cor": "green"
    },
    3: {
        "nome": "Tipo 4 - Ideal",
        "desc": "Forma de salsicha ou cobra, lisa e macia",
        "status": "✅ Ideal",
        "cor": "green"
    },
    4: {
        "nome": "Tipo 5 - Falta de Fibra",
        "desc": "Pedaços macios com bordas bem definidas",
        "status": "⚠️ Tendendo a solto",
        "cor": "orange"
    },
    5: {
        "nome": "Tipo 6 - Leve Diarreia",
        "desc": "Pedaços fofos com bordas irregulares",
        "status": "⚠️ Anormal",
        "cor": "orange"
    },
    6: {
        "nome": "Tipo 7 - Diarreia",
        "desc": "Aquoso, sem pedaços sólidos",
        "status": "🚨 Anormal - Busque atendimento",
        "cor": "red"
    }
}

def preprocess_image(img):
    """Preprocessa imagem para o modelo"""
    # Redimensionar
    img = img.resize((224, 224))

    # Converter para array
    img_array = keras_image.img_to_array(img)

    # Normalizar
    img_array = img_array / 255.0

    # Adicionar dimensão de batch
    img_array = np.expand_dims(img_array, axis=0)

    return img_array

def predict(img, model):
    """Faz predição"""
    img_array = preprocess_image(img)
    predictions = model.predict(img_array, verbose=0)

    predicted_class = np.argmax(predictions[0])
    confidence = predictions[0][predicted_class] * 100

    # Top 3
    top_3_indices = np.argsort(predictions[0])[-3:][::-1]
    top_3 = [
        (idx, predictions[0][idx] * 100)
        for idx in top_3_indices
    ]

    return predicted_class, confidence, top_3

# Interface principal
def main():
    st.title("🔬 Classificador de Fezes - Escala de Bristol")
    st.markdown("---")

    # Sidebar com informações
    with st.sidebar:
        st.header("ℹ️ Sobre")
        st.write("""
        Este aplicativo classifica fezes de acordo com a
        **Escala de Bristol**, usando inteligência artificial.

        **Acurácia:** 68.72%

        **Modelo:** VGG16 Transfer Learning
        """)

        st.markdown("---")
        st.subheader("📋 Escala de Bristol")
        st.write("""
        - **Tipo 1-2:** Constipação
        - **Tipo 3-4:** Normal/Ideal
        - **Tipo 5-7:** Tendendo a diarreia
        """)

    # Upload de imagem
    st.subheader("📤 Faça Upload da Imagem")
    uploaded_file = st.file_uploader(
        "Escolha uma imagem (JPG, PNG)",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        # Mostrar imagem
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("🖼️ Imagem")
            img = Image.open(uploaded_file)
            st.image(img, use_column_width=True)

        with col2:
            st.subheader("🔍 Análise")

            # Carregar modelo
            with st.spinner("Carregando modelo..."):
                model = load_classification_model()

            # Fazer predição
            with st.spinner("Analisando..."):
                predicted_class, confidence, top_3 = predict(img, model)

            # Mostrar resultado
            result = BRISTOL_TYPES[predicted_class]

            st.markdown(f"### {result['nome']}")
            st.markdown(f"**{result['desc']}**")

            # Status com cor
            if result['cor'] == 'green':
                st.success(result['status'])
            elif result['cor'] == 'orange':
                st.warning(result['status'])
            else:
                st.error(result['status'])

            # Confiança
            st.metric("Confiança", f"{confidence:.1f}%")

            # Barra de progresso
            st.progress(confidence / 100)

        # Top 3 predições
        st.markdown("---")
        st.subheader("📊 Top 3 Predições")

        for i, (idx, conf) in enumerate(top_3, 1):
            emoji = "🥇" if i == 1 else ("🥈" if i == 2 else "🥉")
            tipo = BRISTOL_TYPES[idx]
            st.write(f"{emoji} **{tipo['nome']}** - {conf:.1f}%")
            st.progress(conf / 100)

    else:
        st.info("👆 Faça upload de uma imagem para começar a análise")

        # Exemplo visual
        st.markdown("---")
        st.subheader("📖 Como usar:")
        st.write("""
        1. Clique em "Browse files" acima
        2. Selecione uma foto
        3. Aguarde a análise
        4. Veja o resultado e interpretação
        """)

    # Footer
    st.markdown("---")
    st.caption("⚠️ Este é um modelo experimental. Consulte um médico para diagnósticos.")

if __name__ == "__main__":
    main()
