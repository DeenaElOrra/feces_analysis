# frontend/pages/5_📸_Dashboard_Paciente.py
import streamlit as st
from utils.api_client import get_api_client
import pandas as pd
from datetime import datetime
from PIL import Image
import io

st.set_page_config(
    page_title="Dashboard Paciente",
    page_icon="📸",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .result-box {
        background-color: #e7f3ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .recommendation-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #ffc107;
    }
    .analysis-history {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #ccc;
        margin: 1rem 0;
    }
    @media (max-width: 768px) {
        .upload-section {
            padding: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Check authentication
if 'token' not in st.session_state or st.session_state.get('user_type') != 'paciente':
    st.error("⚠️ Você precisa fazer login como paciente para acessar esta página")
    if st.button("Ir para Login"):
        st.switch_page("pages/3_🧑_Login_Paciente.py")
    st.stop()

api_client = get_api_client()

# Sidebar - Profile and logout
with st.sidebar:
    st.markdown("### 🧑 Perfil do Paciente")

    try:
        perfil = api_client.get_perfil_paciente(st.session_state.token)

        st.markdown(f"""
        **Nome:** {perfil['nome']}
        **Email:** {perfil['email']}
        """)

        if perfil.get('cpf'):
            st.markdown(f"**CPF:** {perfil['cpf']}")
        if perfil.get('data_nascimento'):
            st.markdown(f"**Data de Nascimento:** {perfil['data_nascimento']}")
        if perfil.get('telefone'):
            st.markdown(f"**Telefone:** {perfil['telefone']}")

    except Exception as e:
        st.error(f"Erro ao carregar perfil: {str(e)}")
        if st.button("Fazer login novamente"):
            del st.session_state.token
            st.switch_page("pages/3_🧑_Login_Paciente.py")

    st.markdown("---")
    if st.button("🚪 Sair", use_container_width=True):
        del st.session_state.token
        del st.session_state.user_type
        st.switch_page("1_🏠_Home.py")

# Main content
st.title("📸 Minha Saúde Digestiva")

# Create tabs
tab1, tab2 = st.tabs(["📤 Nova Análise", "📊 Meu Histórico"])

# ========== TAB 1: NEW ANALYSIS ==========
with tab1:
    st.markdown("### 📸 Enviar Foto para Análise")

    st.markdown("""
    <div class="upload-section">
        <h4 style="margin-top: 0;">🏥 Como funciona:</h4>
        <ol>
            <li>Tire uma foto clara das suas fezes</li>
            <li>Faça upload da imagem abaixo</li>
            <li>Nossa IA classificará automaticamente usando a Escala de Bristol</li>
            <li>Você receberá recomendações personalizadas</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        # File uploader with camera support (works on mobile)
        uploaded_file = st.file_uploader(
            "Escolha uma imagem",
            type=['jpg', 'jpeg', 'png'],
            help="Aceita JPG, JPEG ou PNG. Use a câmera do celular para tirar a foto!"
        )

        # Add mobile camera option
        if st.button("📱 Tirar Foto (Mobile)", use_container_width=True):
            st.info("Use o botão 'Browse files' acima e selecione 'Camera' no seu dispositivo móvel")

        observacoes = st.text_area(
            "Observações (opcional)",
            placeholder="Ex: Dor abdominal, mudança na dieta, etc.",
            help="Adicione qualquer informação relevante sobre o momento"
        )

    with col2:
        if uploaded_file:
            # Display preview
            image = Image.open(uploaded_file)
            st.image(image, caption="Pré-visualização", use_container_width=True)

    if uploaded_file:
        if st.button("🔍 Analisar Agora", type="primary", use_container_width=True):
            with st.spinner("Analisando imagem... Por favor aguarde."):
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)

                    # Upload and analyze
                    resultado = api_client.criar_analise(
                        st.session_state.token,
                        uploaded_file,
                        observacoes if observacoes else None
                    )

                    st.success("✅ Análise concluída com sucesso!")
                    st.balloons()

                    # Display results
                    st.markdown("---")
                    st.markdown("### 📋 Resultados da Análise")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"""
                        <div class="result-box">
                            <h2>{resultado['tipo_bristol']}</h2>
                            <p>Tipo Bristol</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"""
                        <div class="result-box">
                            <h2>{resultado['confianca']:.1f}%</h2>
                            <p>Confiança</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with col3:
                        data_analise = datetime.fromisoformat(
                            resultado['analisado_em'].replace('Z', '+00:00')
                        ).strftime('%d/%m/%Y %H:%M')
                        st.markdown(f"""
                        <div class="result-box">
                            <h4>{data_analise}</h4>
                            <p>Data/Hora</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Recommendations
                    if resultado.get('recomendacoes'):
                        st.markdown("### 💡 Recomendações")
                        for rec in resultado['recomendacoes']:
                            st.markdown(f"""
                            <div class="recommendation-box">
                                • {rec}
                            </div>
                            """, unsafe_allow_html=True)

                    st.info("📊 Confira seu histórico completo na aba 'Meu Histórico'")

                except Exception as e:
                    st.error(f"❌ Erro ao analisar imagem: {str(e)}")

                    if "401" in str(e):
                        st.warning("Sua sessão expirou. Faça login novamente.")
                        if st.button("Fazer login"):
                            del st.session_state.token
                            st.switch_page("pages/3_🧑_Login_Paciente.py")

# ========== TAB 2: HISTORY ==========
with tab2:
    st.markdown("### 📊 Histórico de Análises")

    try:
        analises = api_client.get_minhas_analises(st.session_state.token)

        if len(analises) == 0:
            st.info("Você ainda não realizou nenhuma análise. Vá para a aba 'Nova Análise' para começar!")
        else:
            # Metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h2>{len(analises)}</h2>
                    <p>Total de Análises</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # Most common type
                tipos = [a['tipo_bristol'] for a in analises]
                tipo_comum = max(set(tipos), key=tipos.count)
                st.markdown(f"""
                <div class="metric-card">
                    <h2>Tipo {tipo_comum}</h2>
                    <p>Mais Frequente</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                # Latest analysis
                ultima = analises[0]['analisado_em']
                data_ultima = datetime.fromisoformat(ultima.replace('Z', '+00:00')).strftime('%d/%m/%Y')
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{data_ultima}</h4>
                    <p>Última Análise</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Bristol distribution chart
            st.markdown("### 📊 Distribuição por Tipo Bristol")

            bristol_counts = {}
            for a in analises:
                tipo = a['tipo_bristol']
                bristol_counts[tipo] = bristol_counts.get(tipo, 0) + 1

            df_bristol = pd.DataFrame([
                {"Tipo Bristol": f"Tipo {k}", "Quantidade": v}
                for k, v in sorted(bristol_counts.items())
            ])

            st.bar_chart(df_bristol.set_index("Tipo Bristol"))

            # Temporal evolution
            st.markdown("### 📈 Evolução Temporal")

            df_temporal = pd.DataFrame([
                {
                    "Data": datetime.fromisoformat(a['analisado_em'].replace('Z', '+00:00')).strftime('%Y-%m-%d'),
                    "Tipo Bristol": a['tipo_bristol']
                }
                for a in reversed(analises[-30:])  # Last 30 analyses
            ])

            st.line_chart(df_temporal.set_index("Data"))

            st.markdown("---")

            # Detailed history
            st.markdown("### 📋 Histórico Detalhado")

            for analise in analises[:20]:  # Show last 20
                data_analise = datetime.fromisoformat(
                    analise['analisado_em'].replace('Z', '+00:00')
                ).strftime('%d/%m/%Y %H:%M')

                with st.expander(f"📅 {data_analise} - Tipo {analise['tipo_bristol']} ({analise['confianca']:.1f}% confiança)"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"""
                        **Tipo Bristol:** {analise['tipo_bristol']}
                        **Confiança:** {analise['confianca']:.1f}%
                        **Data:** {data_analise}
                        """)

                        if analise.get('observacoes'):
                            st.markdown(f"**Observações:** {analise['observacoes']}")

                    with col2:
                        if analise.get('recomendacoes'):
                            st.markdown("**Recomendações:**")
                            for rec in analise['recomendacoes']:
                                st.markdown(f"• {rec}")

            if len(analises) > 20:
                st.caption(f"Mostrando as 20 análises mais recentes de {len(analises)} no total")

    except Exception as e:
        st.error(f"❌ Erro ao carregar histórico: {str(e)}")

        if "401" in str(e):
            st.warning("Sua sessão expirou. Faça login novamente.")
            if st.button("Fazer login"):
                del st.session_state.token
                st.switch_page("pages/3_🧑_Login_Paciente.py")

# Bristol Scale Reference
with st.expander("📖 Referência: Escala de Bristol"):
    st.markdown("""
    ### Escala de Bristol - Tipos de Fezes

    - **Tipo 1:** Pedaços duros separados (constipação severa)
    - **Tipo 2:** Formato de salsicha, mas irregular (constipação leve)
    - **Tipo 3:** Como salsicha com rachaduras (normal)
    - **Tipo 4:** Como salsicha lisa e macia (ideal)
    - **Tipo 5:** Pedaços macios com bordas bem definidas (tendência a diarreia)
    - **Tipo 6:** Pedaços fofos com bordas irregulares (diarreia leve)
    - **Tipo 7:** Aquoso, sem pedaços sólidos (diarreia severa)

    **Tipos 3-4 são considerados ideais e saudáveis.**
    """)
