# frontend/pages/4_📊_Dashboard_Medico.py
import streamlit as st
from utils.api_client import get_api_client
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Dashboard Médico",
    page_icon="📊",
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
    .patient-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
    }
    .analysis-card {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Check authentication
if 'token' not in st.session_state or st.session_state.get('user_type') != 'medico':
    st.error("⚠️ Você precisa fazer login como médico para acessar esta página")
    if st.button("Ir para Login"):
        st.switch_page("pages/2_👨‍⚕️_Login_Medico.py")
    st.stop()

api_client = get_api_client()

# Sidebar - Profile and logout
with st.sidebar:
    st.markdown("### 👨‍⚕️ Perfil Médico")

    try:
        perfil = api_client.get_perfil_medico(st.session_state.token)

        st.markdown(f"""
        **Nome:** {perfil['nome']}
        **CRM:** {perfil['crm']}-{perfil['uf_crm']}
        **Especialidade:** {perfil.get('especialidade', 'N/A')}
        **Email:** {perfil['email']}
        """)

        st.markdown("---")
        st.markdown("### 🔑 Código de Convite")
        st.code(perfil['codigo_convite'], language=None)
        st.caption("Compartilhe com seus pacientes")

    except Exception as e:
        st.error(f"Erro ao carregar perfil: {str(e)}")
        if st.button("Fazer login novamente"):
            del st.session_state.token
            st.switch_page("pages/2_👨‍⚕️_Login_Medico.py")

    st.markdown("---")
    if st.button("🚪 Sair", use_container_width=True):
        del st.session_state.token
        del st.session_state.user_type
        st.switch_page("1_🏠_Home.py")

# Main content
st.title("📊 Dashboard Médico")

# Load patients data
try:
    pacientes = api_client.get_pacientes(st.session_state.token)

    # Metrics
    st.markdown("### 📈 Visão Geral")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(pacientes)}</h2>
            <p>Pacientes Vinculados</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Count total analyses
        total_analises = 0
        for p in pacientes:
            try:
                analises = api_client.get_analises_paciente(st.session_state.token, p['id'])
                total_analises += len(analises)
            except:
                pass

        st.markdown(f"""
        <div class="metric-card">
            <h2>{total_analises}</h2>
            <p>Total de Análises</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{perfil['codigo_convite']}</h2>
            <p>Código de Convite</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Patients list
    st.markdown("### 👥 Meus Pacientes")

    if len(pacientes) == 0:
        st.info("Você ainda não tem pacientes vinculados. Compartilhe seu código de convite para que pacientes possam se cadastrar.")
    else:
        # Create tabs for each patient
        patient_tabs = st.tabs([f"{p['nome']}" for p in pacientes])

        for idx, (tab, paciente) in enumerate(zip(patient_tabs, pacientes)):
            with tab:
                # Patient info
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.markdown(f"""
                    **Email:** {paciente['email']}
                    **Cadastrado em:** {datetime.fromisoformat(paciente['criado_em'].replace('Z', '+00:00')).strftime('%d/%m/%Y')}
                    """)

                    if paciente.get('cpf'):
                        st.markdown(f"**CPF:** {paciente['cpf']}")
                    if paciente.get('data_nascimento'):
                        st.markdown(f"**Data de Nascimento:** {paciente['data_nascimento']}")
                    if paciente.get('telefone'):
                        st.markdown(f"**Telefone:** {paciente['telefone']}")

                with col2:
                    # Load patient analyses
                    try:
                        analises = api_client.get_analises_paciente(st.session_state.token, paciente['id'])

                        if len(analises) == 0:
                            st.info("Este paciente ainda não realizou nenhuma análise")
                        else:
                            st.markdown(f"**Total de análises:** {len(analises)}")

                            # Bristol distribution
                            bristol_counts = {}
                            for a in analises:
                                tipo = a['tipo_bristol']
                                bristol_counts[tipo] = bristol_counts.get(tipo, 0) + 1

                            st.markdown("**Distribuição Bristol:**")
                            df_bristol = pd.DataFrame([
                                {"Tipo": k, "Quantidade": v}
                                for k, v in sorted(bristol_counts.items())
                            ])
                            st.bar_chart(df_bristol.set_index("Tipo"))

                    except Exception as e:
                        st.error(f"Erro ao carregar análises: {str(e)}")

                # Analyses history
                st.markdown("#### 📋 Histórico de Análises")

                try:
                    analises = api_client.get_analises_paciente(st.session_state.token, paciente['id'])

                    if len(analises) > 0:
                        # Sort by date (most recent first)
                        analises_sorted = sorted(
                            analises,
                            key=lambda x: x['analisado_em'],
                            reverse=True
                        )

                        for analise in analises_sorted[:10]:  # Show last 10
                            data_analise = datetime.fromisoformat(
                                analise['analisado_em'].replace('Z', '+00:00')
                            ).strftime('%d/%m/%Y %H:%M')

                            st.markdown(f"""
                            <div class="analysis-card">
                                <strong>📅 {data_analise}</strong> -
                                <strong>Tipo Bristol: {analise['tipo_bristol']}</strong>
                                (Confiança: {analise['confianca']:.1f}%)
                                {f"<br>📝 {analise['observacoes']}" if analise.get('observacoes') else ""}
                            </div>
                            """, unsafe_allow_html=True)

                        if len(analises) > 10:
                            st.caption(f"Mostrando as 10 análises mais recentes de {len(analises)} no total")

                except Exception as e:
                    st.error(f"Erro ao carregar histórico: {str(e)}")

except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {str(e)}")

    if "401" in str(e) or "Token inválido" in str(e):
        st.warning("Sua sessão expirou. Faça login novamente.")
        if st.button("Fazer login"):
            del st.session_state.token
            st.switch_page("pages/2_👨‍⚕️_Login_Medico.py")
