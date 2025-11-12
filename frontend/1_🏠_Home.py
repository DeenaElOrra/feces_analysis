# frontend/1_🏠_Home.py
import streamlit as st
from utils.api_client import get_api_client

# Page config
st.set_page_config(
    page_title="Bristol Stool Scale App",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile-friendly design
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .cta-button {
        text-align: center;
        margin: 2rem 0;
    }
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.8rem;
        }
        .subtitle {
            font-size: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Check if user is already logged in
if 'token' in st.session_state and 'user_type' in st.session_state:
    if st.session_state.user_type == 'medico':
        st.switch_page("pages/4_📊_Dashboard_Medico.py")
    else:
        st.switch_page("pages/5_📸_Dashboard_Paciente.py")

# Header
st.markdown('<h1 class="main-title">🏥 Bristol Stool Scale App</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plataforma profissional para monitoramento digestivo</p>', unsafe_allow_html=True)

# Check backend connection
api_client = get_api_client()
try:
    health = api_client.health_check()
    st.success("✅ Conectado ao servidor")
except Exception as e:
    st.error("❌ Erro ao conectar com o servidor. Verifique se o backend está rodando.")
    st.info("Execute: `cd backend && uvicorn backend.main:app --reload`")

# Introduction
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>👨‍⚕️ Para Médicos</h3>
        <ul>
            <li>Cadastro profissional com CRM</li>
            <li>Gerencie seus pacientes</li>
            <li>Acompanhe histórico completo</li>
            <li>Dashboard com analytics</li>
            <li>Código de convite único</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>🧑 Para Pacientes</h3>
        <ul>
            <li>Upload de fotos via mobile</li>
            <li>Classificação automática Bristol</li>
            <li>Recomendações personalizadas</li>
            <li>Histórico e evolução temporal</li>
            <li>Interface mobile-friendly</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Call to action
st.markdown("---")
st.markdown('<div class="cta-button">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### Acesse sua conta")

    tab1, tab2 = st.tabs(["👨‍⚕️ Sou Médico", "🧑 Sou Paciente"])

    with tab1:
        st.info("Gerencie seus pacientes e acompanhe o progresso deles")
        if st.button("Login Médico", use_container_width=True, type="primary"):
            st.switch_page("pages/2_👨‍⚕️_Login_Medico.py")

    with tab2:
        st.info("Faça upload de fotos e acompanhe sua saúde digestiva")
        if st.button("Login Paciente", use_container_width=True, type="primary"):
            st.switch_page("pages/3_🧑_Login_Paciente.py")

st.markdown('</div>', unsafe_allow_html=True)

# About Bristol Scale
st.markdown("---")
st.markdown("### 📊 Sobre a Escala de Bristol")

with st.expander("O que é a Escala de Bristol?"):
    st.markdown("""
    A Escala de Bristol é uma ferramenta médica que classifica as fezes em 7 tipos diferentes,
    desenvolvida na Universidade de Bristol, Reino Unido.

    **Tipos:**
    - **Tipo 1-2:** Constipação (fezes muito duras)
    - **Tipo 3-4:** Ideal (formato normal e saudável)
    - **Tipo 5-6:** Tendência a diarreia (fezes amolecidas)
    - **Tipo 7:** Diarreia severa (líquida)

    Esta classificação ajuda médicos e pacientes a monitorar a saúde digestiva de forma objetiva.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>💡 Desenvolvido para profissionais de saúde e seus pacientes</p>
    <p><small>Nutricionistas • Gastroenterologistas • Infectologistas</small></p>
</div>
""", unsafe_allow_html=True)
