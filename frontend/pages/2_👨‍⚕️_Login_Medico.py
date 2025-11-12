# frontend/pages/2_👨‍⚕️_Login_Medico.py
import streamlit as st
from utils.api_client import get_api_client

st.set_page_config(
    page_title="Login Médico",
    page_icon="👨‍⚕️",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .login-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Check if already logged in
if 'token' in st.session_state and st.session_state.get('user_type') == 'medico':
    st.switch_page("pages/4_📊_Dashboard_Medico.py")

# Header
st.markdown('<h1 class="login-header">👨‍⚕️ Acesso Médico</h1>', unsafe_allow_html=True)

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

                        if response.get("tipo_usuario") == "medico":
                            # Store session data
                            st.session_state.token = response["access_token"]
                            st.session_state.refresh_token = response["refresh_token"]
                            st.session_state.user_type = "medico"

                            st.success("✅ Login realizado com sucesso!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Esta conta não é de médico. Use o login de paciente.")

                except Exception as e:
                    st.error(f"❌ Erro ao fazer login: {str(e)}")

# ========== REGISTRATION TAB ==========
with tab2:
    st.markdown("### Crie sua conta profissional")

    st.markdown("""
    <div class="info-box">
        💡 <b>Após o cadastro, você receberá um código de convite único</b> para compartilhar com seus pacientes.
    </div>
    """, unsafe_allow_html=True)

    with st.form("registro_form"):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome Completo*", placeholder="Dr. João Silva")
            crm = st.text_input("CRM*", placeholder="123456")
            email_reg = st.text_input("Email*", placeholder="seu.email@exemplo.com")

        with col2:
            uf_crm = st.text_input("UF do CRM*", placeholder="SP", max_chars=2)
            especialidade = st.text_input("Especialidade", placeholder="Gastroenterologia")
            telefone = st.text_input("Telefone", placeholder="(11) 99999-9999")

        senha_reg = st.text_input("Senha*", type="password", placeholder="Mínimo 6 caracteres")
        senha_confirm = st.text_input("Confirmar Senha*", type="password", placeholder="Digite a senha novamente")

        st.markdown("<small>* Campos obrigatórios</small>", unsafe_allow_html=True)

        submitted_reg = st.form_submit_button("Criar Conta", use_container_width=True, type="primary")

        if submitted_reg:
            # Validations
            if not all([nome, crm, uf_crm, email_reg, senha_reg, senha_confirm]):
                st.error("Por favor, preencha todos os campos obrigatórios (*)")
            elif len(senha_reg) < 6:
                st.error("A senha deve ter no mínimo 6 caracteres")
            elif senha_reg != senha_confirm:
                st.error("As senhas não conferem")
            elif len(uf_crm) != 2:
                st.error("UF do CRM deve ter 2 caracteres (ex: SP, RJ)")
            else:
                try:
                    with st.spinner("Criando conta..."):
                        data = {
                            "nome": nome,
                            "crm": crm,
                            "uf_crm": uf_crm.upper(),
                            "email": email_reg,
                            "senha": senha_reg
                        }

                        # Add optional fields only if provided
                        if especialidade:
                            data["especialidade"] = especialidade
                        if telefone:
                            data["telefone"] = telefone

                        response = api_client.registro_medico(data)

                        st.success("✅ Conta criada com sucesso!")
                        st.balloons()

                        # Show invite code
                        st.markdown(f"""
                        <div class="info-box">
                            <h3 style="margin-top: 0;">🎉 Seu código de convite:</h3>
                            <h2 style="text-align: center; color: #1f77b4; font-family: monospace;">
                                {response['codigo_convite']}
                            </h2>
                            <p><b>Compartilhe este código com seus pacientes</b> para que eles possam se cadastrar e vincular à sua conta.</p>
                        </div>
                        """, unsafe_allow_html=True)

                        st.info("👈 Faça login na aba 'Login' para acessar seu dashboard")

                except Exception as e:
                    error_msg = str(e)
                    if "Email já cadastrado" in error_msg:
                        st.error("❌ Este email já está cadastrado")
                    elif "CRM já cadastrado" in error_msg:
                        st.error("❌ Este CRM já está cadastrado")
                    else:
                        st.error(f"❌ Erro ao criar conta: {error_msg}")

# Back to home
st.markdown("---")
if st.button("⬅️ Voltar para página inicial"):
    st.switch_page("1_🏠_Home.py")
