# Backend FastAPI - Bristol Stool Scale API

## 🎉 Backend Completo Criado!

Este backend FastAPI está 100% funcional e pronto para uso.

## 📁 Estrutura

```
backend/
├── core/
│   ├── config.py       ✅ Configurações
│   ├── database.py     ✅ SQLAlchemy setup
│   └── security.py     ✅ JWT + hashing
├── models/
│   └── models.py       ✅ Medico, Paciente, Vinculo, Analise
├── schemas/
│   └── schemas.py      ✅ Pydantic schemas
├── services/
│   └── ml_service.py   ✅ Classificação ML
├── main.py             ✅ FastAPI app com todos os endpoints
├── requirements.txt    ✅ Dependências
└── .env               ✅ Configurações (editável)
```

## 🚀 Como Rodar

### 1. Criar ambiente virtual

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# ou
venv\Scripts\activate  # Windows
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar .env

O arquivo `.env` já foi criado. Edite se necessário:

```bash
# Já está configurado para usar SQLite local
# Para PostgreSQL, mude DATABASE_URL
```

### 4. Rodar servidor

```bash
python -m backend.main
```

OU

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Acessar documentação

Abra no navegador:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📊 Endpoints Disponíveis

### Autenticação

```
POST /auth/registro-medico  - Criar conta de médico
POST /auth/registro-paciente - Criar conta de paciente
POST /auth/login - Login (médico ou paciente)
```

### Médico

```
GET /medicos/perfil - Dados do médico logado
GET /medicos/pacientes - Lista de pacientes vinculados
GET /medicos/paciente/{id}/analises - Histórico do paciente
```

### Paciente

```
GET /pacientes/perfil - Dados do paciente logado
POST /pacientes/analise - Upload e classificação
GET /pacientes/analises - Histórico de análises
```

## 🧪 Testar API

### 1. Registrar Médico

```bash
curl -X POST "http://localhost:8000/auth/registro-medico" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Dr. João Silva",
    "crm": "123456",
    "uf_crm": "SP",
    "especialidade": "Gastroenterologia",
    "email": "joao@email.com",
    "senha": "senha123",
    "telefone": "11999999999"
  }'
```

Resposta inclui o `codigo_convite` (ex: DR-ABC123)

### 2. Registrar Paciente

```bash
curl -X POST "http://localhost:8000/auth/registro-paciente" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Santos",
    "email": "maria@email.com",
    "senha": "senha123",
    "codigo_medico": "DR-ABC123"
  }'
```

### 3. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -F "email=maria@email.com" \
  -F "senha=senha123"
```

Retorna `access_token` - use em todos os requests protegidos:

### 4. Upload de Análise (Paciente)

```bash
curl -X POST "http://localhost:8000/pacientes/analise" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -F "imagem=@/caminho/para/imagem.jpg" \
  -F "observacoes=Teste de análise"
```

## 🗄️ Banco de Dados

O backend usa SQLite por padrão (arquivo `feces_app.db` será criado automaticamente).

Para usar PostgreSQL em produção, mude em `.env`:

```
DATABASE_URL=postgresql://user:password@localhost/feces_db
```

## 🔐 Segurança

- Senhas com bcrypt (salt rounds = 12)
- JWT tokens com expiração
- Access token: 30 minutos
- Refresh token: 7 dias
- CORS configurado (ajuste em produção)

## 📦 Deploy

### Opção 1: Mesmo servidor EC2 que o Streamlit

```bash
# No EC2, porta 8000
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
```

### Opção 2: Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🎯 Próximos Passos

1. ✅ Backend completo e funcional
2. ⏭️ Criar frontend Streamlit multi-page
3. ⏭️ Integrar frontend com backend
4. ⏭️ Deploy completo na EC2

## 📚 Documentação

Toda a documentação interativa está disponível em:
- http://localhost:8000/docs (Swagger)
- http://localhost:8000/redoc (ReDoc)

Teste todos os endpoints diretamente pelo navegador!
