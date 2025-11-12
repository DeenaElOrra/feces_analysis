# frontend/pages/3_🧑_Login_Paciente.py
import streamlit as st
from utils.api_client import get_api_client
from datetime import date

st.set_page_config(
    page_title="Login Paciente",
    page_icon="🧑",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .login-header {
        text-align: center;
        color: #2ca02c;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #e7ffe7;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2ca02c;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Check if already logged in
if 'token' in st.session_state and st.session_state.get('user_type') == 'paciente':
    st.switch_page("pages/5_📸_Dashboard_Paciente.py")

# Header
st.markdown('<h1 class="login-header">🧑 Acesso Paciente</h1>', unsafe_allow_html=True)

# Tabs for login and registration
tab1, tab2 = st.tabs(["🔐 Login", "📝 Cadastro"])

api_client = get_api_client()

# ========== LOGIN TAB ==========
with tab1:
    st.markdown("### Entre com suas credenciais")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="seu.email@exemplo.com")
        senha = st.text_input("Senha", type="password", placeholder="Sua senha")

        submitted = st.form_submit_button("Entrar", use_container_width=True, type="primary")

        if submitted:
            if not email or not senha:
                st.error("Por favor, preencha todos os campos")
            else:
                try:
                    with st.spinner("Autenticando..."):
                        response = api_client.login(email, senha)

                        if response.get("tipo_usuario") == "paciente":
                            # Store session data
                            st.session_state.token = response["access_token"]
                            st.session_state.refresh_token = response["refresh_token"]
                            st.session_state.user_type = "paciente"

                            st.success("✅ Login realizado com sucesso!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Esta conta não é de paciente. Use o login de médico.")

                except Exception as e:
                    st.error(f"❌ Erro ao fazer login: {str(e)}")

# ========== REGISTRATION TAB ==========
with tab2:
    st.markdown("### Crie sua conta de paciente")

    st.markdown("""
    <div class="info-box">
        💡 <b>Você precisa do código de convite do seu médico</b> para criar sua conta e vincular-se a ele.
    </div>
    """, unsafe_allow_html=True)

    with st.form("registro_form"):
        nome = st.text_input("Nome Completo*", placeholder="Maria Santos")
        email_reg = st.text_input("Email*", placeholder="seu.email@exemplo.com")

        col1, col2 = st.columns(2)
        with col1:
            cpf = st.text_input("CPF", placeholder="000.000.000-00")
            telefone = st.text_input("Telefone", placeholder="(11) 99999-9999")

        with col2:
            data_nascimento = st.date_input(
                "Data de Nascimento",
                value=None,
                max_value=date.today(),
                format="DD/MM/YYYY"
            )

        st.markdown("---")

        codigo_medico = st.text_input(
            "Código do Médico*",
            placeholder="DR-ABC123",
            help="Solicite este código ao seu médico"
        )

        senha_reg = st.text_input("Senha*", type="password", placeholder="Mínimo 6 caracteres")
        senha_confirm = st.text_input("Confirmar Senha*", type="password", placeholder="Digite a senha novamente")

        st.markdown("<small>* Campos obrigatórios</small>", unsafe_allow_html=True)

        submitted_reg = st.form_submit_button("Criar Conta", use_container_width=True, type="primary")

        if submitted_reg:
            # Validations
            if not all([nome, email_reg, codigo_medico, senha_reg, senha_confirm]):
                st.error("Por favor, preencha todos os campos obrigatórios (*)")
            elif len(senha_reg) < 6:
                st.error("A senha deve ter no mínimo 6 caracteres")
            elif senha_reg != senha_confirm:
                st.error("As senhas não conferem")
            else:
                try:
                    with st.spinner("Criando conta e vinculando ao médico..."):
                        data = {
                            "nome": nome,
                            "email": email_reg,
                            "senha": senha_reg,
                            "codigo_medico": codigo_medico.upper()
                        }

                        # Add optional fields only if provided
                        if cpf:
                            data["cpf"] = cpf
                        if data_nascimento:
                            data["data_nascimento"] = str(data_nascimento)
                        if telefone:
                            data["telefone"] = telefone

                        response = api_client.registro_paciente(data)

                        st.success("✅ Conta criada e vinculada ao médico com sucesso!")
                        st.balloons()

                        st.markdown("""
                        <div class="info-box">
                            <h3 style="margin-top: 0;">🎉 Bem-vindo(a)!</h3>
                            <p>Sua conta foi criada e você já está vinculado ao seu médico.</p>
                            <p>Agora você pode fazer login e começar a usar a plataforma!</p>
                        </div>
                        """, unsafe_allow_html=True)

                        st.info("👈 Faça login na aba 'Login' para acessar seu dashboard")

                except Exception as e:
                    error_msg = str(e)
                    if "Email já cadastrado" in error_msg:
                        st.error("❌ Este email já está cadastrado")
                    elif "Código do médico inválido" in error_msg or "404" in error_msg:
                        st.error("❌ Código do médico inválido. Verifique com seu médico.")
                    else:
                        st.error(f"❌ Erro ao criar conta: {error_msg}")

# Back to home
st.markdown("---")
if st.button("⬅️ Voltar para página inicial"):
    st.switch_page("1_🏠_Home.py")
