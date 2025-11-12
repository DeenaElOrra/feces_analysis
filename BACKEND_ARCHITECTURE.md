# Backend Architecture - Bristol Stool Scale API

## 📁 Estrutura Criada

```
backend/
├── core/
│   ├── config.py          # Configurações da aplicação
│   ├── security.py        # JWT, hashing de senhas
│   └── database.py        # Conexão com banco de dados
│
├── models/                # SQLAlchemy models (ORM)
│   ├── medico.py
│   ├── paciente.py
│   ├── vinculo.py
│   └── analise.py
│
├── schemas/               # Pydantic schemas (validação)
│   ├── medico.py
│   ├── paciente.py
│   └── analise.py
│
├── routers/               # Endpoints da API
│   ├── auth.py           # Login, registro
│   ├── medicos.py        # Endpoints de médicos
│   ├── pacientes.py      # Endpoints de pacientes
│   └── analises.py       # Upload e classificação
│
├── services/             # Lógica de negócio
│   ├── ml_service.py    # Modelo ML
│   └── auth_service.py  # Autenticação
│
├── uploads/             # Diretório de uploads
├── requirements.txt     # Dependências
├── .env.example        # Exemplo de variáveis de ambiente
└── main.py            # Entry point da API
```

## 🗄️ Banco de Dados

### Tabelas:

**medicos**
- id (UUID)
- nome
- crm
- uf_crm
- especialidade
- email
- senha_hash
- codigo_convite (único - ex: DR-ABC123)
- telefone
- criado_em

**pacientes**
- id (UUID)
- nome
- email
- senha_hash
- cpf (opcional)
- data_nascimento
- telefone
- criado_em

**vinculo_medico_paciente**
- id (UUID)
- medico_id (FK)
- paciente_id (FK)
- vinculado_em
- ativo

**analises**
- id (UUID)
- paciente_id (FK)
- imagem_url
- tipo_bristol (1-7)
- confianca (0-100%)
- observacoes
- analisado_em

## 🔐 Autenticação

### Fluxo:
1. Login → Retorna access_token + refresh_token (JWT)
2. Requests → Header: `Authorization: Bearer {access_token}`
3. Token expira em 30 min
4. Refresh token válido por 7 dias

### Endpoints:

```python
POST /auth/registro-medico
{
  "nome": "Dr. João Silva",
  "crm": "123456",
  "uf_crm": "SP",
  "especialidade": "Gastroenterologia",
  "email": "joao@email.com",
  "senha": "senha123"
}

POST /auth/registro-paciente
{
  "nome": "Maria Santos",
  "email": "maria@email.com",
  "senha": "senha123",
  "codigo_medico": "DR-ABC123"  # Código do médico
}

POST /auth/login
{
  "email": "joao@email.com",
  "senha": "senha123"
}
→ Retorna: { "access_token": "...", "refresh_token": "...", "tipo_usuario": "medico" }
```

## 📊 Endpoints Principais

### Médico:

```python
GET /medicos/perfil
→ Retorna dados do médico logado

GET /medicos/pacientes
→ Lista todos os pacientes vinculados

GET /medicos/paciente/{id}/analises
→ Histórico completo de um paciente

GET /medicos/dashboard
→ Estatísticas gerais (total pacientes, análises por tipo, etc)
```

### Paciente:

```python
GET /pacientes/perfil
→ Retorna dados do paciente logado

POST /pacientes/analise
→ Upload de imagem + classificação ML
FormData: { imagem: File, observacoes?: string }

GET /pacientes/analises
→ Histórico de análises do paciente

GET /pacientes/dashboard
→ Gráficos de evolução, estatísticas
```

## 🤖 ML Service

```python
# services/ml_service.py

class MLService:
    def __init__(self):
        self.model = load_model('best_model_fe.h5')

    def classify(self, image_path: str) -> dict:
        # Preprocessa imagem
        img = preprocess_image(image_path)

        # Predição
        predictions = self.model.predict(img)
        tipo_bristol = np.argmax(predictions[0]) + 1  # 1-7
        confianca = float(predictions[0].max() * 100)

        # Recomendações
        recomendacoes = self.get_recomendacoes(tipo_bristol)

        return {
            "tipo_bristol": tipo_bristol,
            "confianca": confianca,
            "recomendacoes": recomendacoes
        }
```

## 🚀 Como Rodar

```bash
# 1. Entrar no backend
cd backend

# 2. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Mac/Linux

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# 5. Iniciar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# API estará em: http://localhost:8000
# Documentação Swagger: http://localhost:8000/docs
```

## 📱 Próximos Passos

### 1. Completar Backend (você pode fazer isso!)

Os arquivos já criados:
- ✅ `core/config.py` - Configurações
- ✅ `requirements.txt` - Dependências
- ✅ `.env.example` - Exemplo de variáveis

Arquivos que você precisa criar:

**core/database.py**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**core/security.py**
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

### 2. Frontend Streamlit Multi-Page

Criar interface separada em `frontend/` com páginas para:
- Login médico/paciente
- Dashboard médico (lista pacientes)
- Dashboard paciente (upload + histórico)
- Gráficos de evolução

### 3. Deploy

Opções:
- **EC2**: Já temos script de deploy
- **Docker**: Criar `docker-compose.yml`
- **Render/Railway**: Deploy gratuito

## 🎯 Código de Convite

O código é gerado automaticamente ao criar médico:

```python
import secrets
import string

def generate_invite_code():
    # Gera DR-XXXYYY (6 caracteres)
    chars = string.ascii_uppercase + string.digits
    code = ''.join(secrets.choice(chars) for _ in range(6))
    return f"DR-{code}"
```

Paciente usa este código ao se cadastrar, criando vínculo automático.

## 📚 Recursos

- FastAPI Docs: https://fastapi.tiangolo.com
- SQLAlchemy: https://docs.sqlalchemy.org
- JWT: https://jwt.io
- Pydantic: https://docs.pydantic.dev

## ❓ Perguntas?

Este é um guia completo da arquitetura. Os próximos passos são:

1. **Backend**: Completar os arquivos listados acima
2. **Testar**: Usar Swagger UI (http://localhost:8000/docs)
3. **Frontend**: Criar interface Streamlit
4. **Deploy**: Subir na EC2 ou Render

Quer que eu crie algum arquivo específico primeiro?
