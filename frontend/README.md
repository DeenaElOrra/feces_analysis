# Frontend Streamlit - Bristol Stool Scale App

## Interface Web Completa para Médicos e Pacientes

Este frontend Streamlit foi desenvolvido para trabalhar em conjunto com o backend FastAPI, oferecendo uma interface mobile-friendly e intuitiva.

## Estrutura do Projeto

```
frontend/
├── 1_🏠_Home.py                    # Página inicial
├── pages/
│   ├── 2_👨‍⚕️_Login_Medico.py      # Login/Registro médico
│   ├── 3_🧑_Login_Paciente.py      # Login/Registro paciente
│   ├── 4_📊_Dashboard_Medico.py    # Dashboard do médico
│   └── 5_📸_Dashboard_Paciente.py  # Dashboard do paciente
├── utils/
│   └── api_client.py              # Cliente HTTP para API
└── requirements.txt               # Dependências
```

## Funcionalidades

### Para Médicos
- Registro profissional com CRM
- Geração de código de convite único
- Visualização de todos os pacientes vinculados
- Acesso ao histórico completo de análises de cada paciente
- Dashboard com métricas e distribuição Bristol
- Interface responsiva para desktop e mobile

### Para Pacientes
- Registro com código do médico
- Upload de fotos direto da câmera do celular
- Classificação automática usando IA (Escala de Bristol)
- Recomendações personalizadas
- Histórico completo de análises
- Gráficos de evolução temporal
- Interface mobile-first

## Como Rodar

### 1. Certifique-se de que o backend está rodando

Primeiro, inicie o backend FastAPI:

```bash
cd backend
source venv/bin/activate  # Mac/Linux
# ou venv\Scripts\activate (Windows)

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

O backend deve estar disponível em `http://localhost:8000`

### 2. Instalar dependências do frontend

```bash
cd frontend
pip install -r requirements.txt
```

### 3. Rodar Streamlit

```bash
streamlit run 1_🏠_Home.py
```

Por padrão, abre em `http://localhost:8501`

### 4. Configurar URL do Backend (Opcional)

Se o backend não estiver em `localhost:8000`, edite em [utils/api_client.py](utils/api_client.py:115):

```python
backend_url = "http://SEU_IP:8000"
```

## Fluxo de Uso

### Fluxo do Médico

1. Acesse a página inicial
2. Clique em "Login Médico"
3. Na aba "Cadastro", crie sua conta com:
   - Nome, CRM, UF do CRM
   - Email, senha, especialidade
4. Você receberá um **código de convite** (ex: DR-ABC123)
5. Compartilhe este código com seus pacientes
6. Faça login na aba "Login"
7. No dashboard, você verá:
   - Todos os pacientes vinculados
   - Histórico de análises de cada paciente
   - Distribuição dos tipos Bristol
   - Métricas gerais

### Fluxo do Paciente

1. Solicite o código de convite do seu médico
2. Acesse a página inicial
3. Clique em "Login Paciente"
4. Na aba "Cadastro", crie sua conta com:
   - Nome, email, senha
   - **Código do médico** (obrigatório)
   - Dados opcionais (CPF, data nascimento, telefone)
5. Faça login na aba "Login"
6. No dashboard:
   - **Aba "Nova Análise":**
     - Tire foto direto do celular ou faça upload
     - Adicione observações (opcional)
     - Clique em "Analisar Agora"
     - Veja resultado instantâneo com recomendações
   - **Aba "Meu Histórico":**
     - Visualize todas as suas análises
     - Gráficos de distribuição Bristol
     - Evolução temporal

## Mobile-Friendly

O frontend foi desenvolvido com foco em dispositivos móveis:

- Layout responsivo que se adapta ao tamanho da tela
- Upload de imagens direto da câmera do celular
- Interface touch-friendly
- CSS otimizado para mobile

### Como usar no celular

1. Acesse `http://[IP_DO_SERVIDOR]:8501` no navegador do celular
2. Faça login como paciente
3. Na página "Nova Análise", clique em "Escolha uma imagem"
4. Seu celular abrirá opção para usar a câmera
5. Tire a foto e faça upload automaticamente

## Segurança

- JWT tokens para autenticação
- Sessões seguras com Streamlit
- Validação de dados no frontend e backend
- Apenas médico vê dados de seus pacientes
- Paciente vê apenas seus próprios dados

## Deploy em Produção

### Opção 1: Mesma EC2 do Backend

```bash
# No servidor EC2
cd frontend
nohup streamlit run 1_🏠_Home.py --server.port 8501 --server.address 0.0.0.0 &
```

### Opção 2: Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "1_🏠_Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t feces-frontend .
docker run -p 8501:8501 feces-frontend
```

### Opção 3: Streamlit Cloud

1. Faça push para GitHub
2. Acesse https://streamlit.io/cloud
3. Conecte seu repositório
4. Configure variáveis de ambiente (backend URL)
5. Deploy automático

## Configurações Adicionais

### Personalizar Tema

Crie `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
enableCORS = false
enableXsrfProtection = true
```

### Adicionar Logo

Coloque uma imagem em `.streamlit/` e adicione no código:

```python
st.image(".streamlit/logo.png", width=200)
```

## Troubleshooting

### Erro: "Erro ao conectar com servidor"

- Verifique se o backend está rodando em `localhost:8000`
- Teste: `curl http://localhost:8000/health`

### Token expirado

- Faça logout e login novamente
- Tokens JWT expiram após 30 minutos por padrão

### Upload de imagem falha

- Verifique formato (JPG, JPEG, PNG)
- Tamanho máximo suportado pelo backend
- Permissões de escrita no diretório `uploads/`

### Página não carrega no mobile

- Verifique firewall/security groups na EC2
- Porta 8501 deve estar aberta
- Use HTTPS em produção

## Próximos Passos

1. ✅ Frontend completo e funcional
2. ✅ Integração com backend FastAPI
3. ⏭️ Testes end-to-end
4. ⏭️ Deploy em produção (EC2)
5. ⏭️ HTTPS com certificado SSL
6. ⏭️ Melhorias de UX baseadas em feedback

## Suporte

Para questões técnicas ou bugs, consulte a documentação do backend em [../backend/README.md](../backend/README.md)
