"""
Script para gerar todos os arquivos do backend FastAPI
Execute: python3 generate_backend.py
"""
import os

# Criar arquivo de models
MODELS_CODE = """# backend/models/models.py
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Medico(Base):
    __tablename__ = "medicos"

    id = Column(String, primary_key=True, default=generate_uuid)
    nome = Column(String(255), nullable=False)
    crm = Column(String(20), unique=True, nullable=False)
    uf_crm = Column(String(2), nullable=False)
    especialidade = Column(String(100))
    email = Column(String(255), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    codigo_convite = Column(String(20), unique=True, nullable=False)
    telefone = Column(String(20))
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    vinculos = relationship("VinculoMedicoPaciente", back_populates="medico")


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(String, primary_key=True, default=generate_uuid)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, nullable=True)
    data_nascimento = Column(Date, nullable=True)
    telefone = Column(String(20))
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    vinculos = relationship("VinculoMedicoPaciente", back_populates="paciente")
    analises = relationship("Analise", back_populates="paciente")


class VinculoMedicoPaciente(Base):
    __tablename__ = "vinculo_medico_paciente"

    id = Column(String, primary_key=True, default=generate_uuid)
    medico_id = Column(String, ForeignKey("medicos.id"), nullable=False)
    paciente_id = Column(String, ForeignKey("pacientes.id"), nullable=False)
    vinculado_em = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)

    # Relacionamentos
    medico = relationship("Medico", back_populates="vinculos")
    paciente = relationship("Paciente", back_populates="vinculos")


class Analise(Base):
    __tablename__ = "analises"

    id = Column(String, primary_key=True, default=generate_uuid)
    paciente_id = Column(String, ForeignKey("pacientes.id"), nullable=False)
    imagem_url = Column(String(500), nullable=False)
    tipo_bristol = Column(Integer, nullable=False)  # 1-7
    confianca = Column(Float, nullable=False)  # 0-100
    observacoes = Column(String)
    analisado_em = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    paciente = relationship("Paciente", back_populates="analises")
"""

# Criar arquivo schemas
SCHEMAS_CODE = """# backend/schemas/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date


# ========== AUTH ==========
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    tipo_usuario: str  # "medico" ou "paciente"


# ========== MEDICO ==========
class MedicoCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=255)
    crm: str = Field(..., min_length=4, max_length=20)
    uf_crm: str = Field(..., min_length=2, max_length=2)
    especialidade: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    senha: str = Field(..., min_length=6)
    telefone: Optional[str] = None


class MedicoResponse(BaseModel):
    id: str
    nome: str
    crm: str
    uf_crm: str
    especialidade: Optional[str]
    email: str
    codigo_convite: str
    telefone: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True


# ========== PACIENTE ==========
class PacienteCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    senha: str = Field(..., min_length=6)
    codigo_medico: str = Field(..., description="Código de convite do médico")
    cpf: Optional[str] = None
    data_nascimento: Optional[date] = None
    telefone: Optional[str] = None


class PacienteResponse(BaseModel):
    id: str
    nome: str
    email: str
    cpf: Optional[str]
    data_nascimento: Optional[date]
    telefone: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True


# ========== ANALISE ==========
class AnaliseCreate(BaseModel):
    observacoes: Optional[str] = None


class AnaliseResponse(BaseModel):
    id: str
    paciente_id: str
    imagem_url: str
    tipo_bristol: int
    confianca: float
    observacoes: Optional[str]
    analisado_em: datetime
    recomendacoes: Optional[List[str]] = []

    class Config:
        from_attributes = True


# ========== DASHBOARD ==========
class DashboardMedico(BaseModel):
    total_pacientes: int
    total_analises: int
    analises_hoje: int
    distribuicao_bristol: dict  # {1: 10, 2: 5, ...}


class DashboardPaciente(BaseModel):
    total_analises: int
    ultima_analise: Optional[AnaliseResponse]
    distribuicao_bristol: dict
    evolucao_temporal: List[dict]  # [{data: "2025-01-01", tipo: 3}, ...]
"""

# Criar arquivo main.py completo
MAIN_CODE = """# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
from datetime import datetime, timedelta

from .core.config import get_settings
from .core.database import engine, get_db, Base
from .core.security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, decode_token, generate_invite_code
)
from .models.models import Medico, Paciente, VinculoMedicoPaciente, Analise
from .schemas.schemas import (
    MedicoCreate, MedicoResponse, PacienteCreate, PacienteResponse,
    AnaliseResponse, Token, DashboardMedico, DashboardPaciente
)
from .services.ml_service import MLService

settings = get_settings()
security = HTTPBearer()

# Criar app FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para classificação de fezes na Escala de Bristol"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Criar diretório de uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Inicializar serviço ML
ml_service = MLService(settings.MODEL_PATH)


# ========== DEPENDENCIES ==========
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    user_id = payload.get("sub")
    user_type = payload.get("type")

    if user_type == "medico":
        user = db.query(Medico).filter(Medico.id == user_id).first()
    elif user_type == "paciente":
        user = db.query(Paciente).filter(Paciente.id == user_id).first()
    else:
        raise HTTPException(status_code=401, detail="Tipo de usuário inválido")

    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return {"user": user, "type": user_type}


# ========== AUTH ENDPOINTS ==========
@app.post("/auth/registro-medico", response_model=MedicoResponse)
def registro_medico(medico: MedicoCreate, db: Session = Depends(get_db)):
    # Verificar se email já existe
    if db.query(Medico).filter(Medico.email == medico.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Verificar se CRM já existe
    if db.query(Medico).filter(Medico.crm == medico.crm).first():
        raise HTTPException(status_code=400, detail="CRM já cadastrado")

    # Gerar código de convite único
    while True:
        codigo = generate_invite_code()
        if not db.query(Medico).filter(Medico.codigo_convite == codigo).first():
            break

    # Criar médico
    novo_medico = Medico(
        nome=medico.nome,
        crm=medico.crm,
        uf_crm=medico.uf_crm.upper(),
        especialidade=medico.especialidade,
        email=medico.email,
        senha_hash=hash_password(medico.senha),
        codigo_convite=codigo,
        telefone=medico.telefone
    )

    db.add(novo_medico)
    db.commit()
    db.refresh(novo_medico)
    return novo_medico


@app.post("/auth/registro-paciente", response_model=PacienteResponse)
def registro_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    # Verificar se email já existe
    if db.query(Paciente).filter(Paciente.email == paciente.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Verificar se código do médico existe
    medico = db.query(Medico).filter(Medico.codigo_convite == paciente.codigo_medico).first()
    if not medico:
        raise HTTPException(status_code=400, detail="Código do médico inválido")

    # Criar paciente
    novo_paciente = Paciente(
        nome=paciente.nome,
        email=paciente.email,
        senha_hash=hash_password(paciente.senha),
        cpf=paciente.cpf,
        data_nascimento=paciente.data_nascimento,
        telefone=paciente.telefone
    )

    db.add(novo_paciente)
    db.commit()
    db.refresh(novo_paciente)

    # Criar vínculo médico-paciente
    vinculo = VinculoMedicoPaciente(
        medico_id=medico.id,
        paciente_id=novo_paciente.id
    )
    db.add(vinculo)
    db.commit()

    return novo_paciente


@app.post("/auth/login", response_model=Token)
def login(email: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    # Tentar médico
    medico = db.query(Medico).filter(Medico.email == email).first()
    if medico and verify_password(senha, medico.senha_hash):
        access_token = create_access_token({"sub": medico.id, "type": "medico"})
        refresh_token = create_refresh_token({"sub": medico.id, "type": "medico"})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "tipo_usuario": "medico"
        }

    # Tentar paciente
    paciente = db.query(Paciente).filter(Paciente.email == email).first()
    if paciente and verify_password(senha, paciente.senha_hash):
        access_token = create_access_token({"sub": paciente.id, "type": "paciente"})
        refresh_token = create_refresh_token({"sub": paciente.id, "type": "paciente"})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "tipo_usuario": "paciente"
        }

    raise HTTPException(status_code=401, detail="Email ou senha incorretos")


# ========== MEDICO ENDPOINTS ==========
@app.get("/medicos/perfil", response_model=MedicoResponse)
def get_perfil_medico(current_user = Depends(get_current_user)):
    if current_user["type"] != "medico":
        raise HTTPException(status_code=403, detail="Acesso negado")
    return current_user["user"]


@app.get("/medicos/pacientes", response_model=List[PacienteResponse])
def get_pacientes(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["type"] != "medico":
        raise HTTPException(status_code=403, detail="Acesso negado")

    vinculos = db.query(VinculoMedicoPaciente).filter(
        VinculoMedicoPaciente.medico_id == current_user["user"].id,
        VinculoMedicoPaciente.ativo == True
    ).all()

    pacientes = [v.paciente for v in vinculos]
    return pacientes


@app.get("/medicos/paciente/{paciente_id}/analises", response_model=List[AnaliseResponse])
def get_analises_paciente(paciente_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["type"] != "medico":
        raise HTTPException(status_code=403, detail="Acesso negado")

    # Verificar se médico tem acesso a este paciente
    vinculo = db.query(VinculoMedicoPaciente).filter(
        VinculoMedicoPaciente.medico_id == current_user["user"].id,
        VinculoMedicoPaciente.paciente_id == paciente_id,
        VinculoMedicoPaciente.ativo == True
    ).first()

    if not vinculo:
        raise HTTPException(status_code=403, detail="Acesso negado a este paciente")

    analises = db.query(Analise).filter(Analise.paciente_id == paciente_id).order_by(Analise.analisado_em.desc()).all()
    return analises


# ========== PACIENTE ENDPOINTS ==========
@app.get("/pacientes/perfil", response_model=PacienteResponse)
def get_perfil_paciente(current_user = Depends(get_current_user)):
    if current_user["type"] != "paciente":
        raise HTTPException(status_code=403, detail="Acesso negado")
    return current_user["user"]


@app.post("/pacientes/analise", response_model=AnaliseResponse)
async def criar_analise(
    imagem: UploadFile = File(...),
    observacoes: Optional[str] = Form(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["type"] != "paciente":
        raise HTTPException(status_code=403, detail="Acesso negado")

    # Salvar imagem
    file_extension = os.path.splitext(imagem.filename)[1]
    filename = f"{current_user['user'].id}_{datetime.now().timestamp()}{file_extension}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(imagem.file, buffer)

    # Classificar com ML
    resultado = ml_service.classify(filepath)

    # Criar análise no banco
    nova_analise = Analise(
        paciente_id=current_user["user"].id,
        imagem_url=filepath,
        tipo_bristol=resultado["tipo_bristol"],
        confianca=resultado["confianca"],
        observacoes=observacoes
    )

    db.add(nova_analise)
    db.commit()
    db.refresh(nova_analise)

    return {**nova_analise.__dict__, "recomendacoes": resultado.get("recomendacoes", [])}


@app.get("/pacientes/analises", response_model=List[AnaliseResponse])
def get_minhas_analises(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["type"] != "paciente":
        raise HTTPException(status_code=403, detail="Acesso negado")

    analises = db.query(Analise).filter(
        Analise.paciente_id == current_user["user"].id
    ).order_by(Analise.analisado_em.desc()).all()

    return analises


# ========== HEALTH CHECK ==========
@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

# Criar ML Service
ML_SERVICE_CODE = """# backend/services/ml_service.py
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image


class MLService:
    def __init__(self, model_path: str):
        print(f"Carregando modelo de: {model_path}")
        self.model = load_model(model_path)
        print("Modelo carregado com sucesso!")

        # Recomendações por tipo Bristol
        self.recomendacoes = {
            1: [
                "Constipação severa - Hidratação inadequada",
                "Aumentar consumo de fibras (frutas, vegetais, grãos integrais)",
                "Beber pelo menos 2 litros de água por dia",
                "Consulte um médico se persistir por mais de 3 dias"
            ],
            2: [
                "Constipação leve",
                "Aumentar consumo de fibras",
                "Melhorar hidratação (1.5-2L de água/dia)",
                "Praticar atividade física regular"
            ],
            3: [
                "Normal - Formato ideal",
                "Parabéns! Suas fezes estão saudáveis",
                "Mantenha a alimentação equilibrada",
                "Continue bebendo bastante água"
            ],
            4: [
                "Normal - Textura ideal",
                "Excelente! Trato digestivo funcionando bem",
                "Mantenha seus hábitos alimentares",
                "Continue a rotina de hidratação"
            ],
            5: [
                "Fezes amolecidas - Leve diarreia",
                "Pode indicar falta de fibras ou excesso de líquidos",
                "Reduzir alimentos muito gordurosos",
                "Se persistir, consulte um médico"
            ],
            6: [
                "Diarreia leve",
                "Aumentar consumo de probióticos",
                "Evitar alimentos irritantes",
                "Consulte um médico se durar mais de 2 dias"
            ],
            7: [
                "Diarreia severa",
                "CONSULTE UM MÉDICO IMEDIATAMENTE",
                "Manter hidratação com soro caseiro",
                "Pode indicar infecção ou intolerância alimentar"
            ]
        }

    def preprocess_image(self, image_path: str):
        \"\"\"
        Preprocessa imagem para o modelo
        \"\"\"
        img = Image.open(image_path)
        img = img.resize((224, 224))  # VGG16 input size
        img_array = np.array(img)

        # Se imagem for grayscale, converter para RGB
        if len(img_array.shape) == 2:
            img_array = np.stack([img_array] * 3, axis=-1)

        # Normalizar
        img_array = img_array.astype('float32') / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def classify(self, image_path: str) -> dict:
        \"\"\"
        Classifica imagem e retorna resultado
        \"\"\"
        # Preprocessar
        img_array = self.preprocess_image(image_path)

        # Predição
        predictions = self.model.predict(img_array, verbose=0)

        # Tipo Bristol (1-7)
        tipo_bristol = int(np.argmax(predictions[0])) + 1  # +1 porque modelo retorna 0-6

        # Confiança (%)
        confianca = float(predictions[0].max() * 100)

        # Recomendações
        recomendacoes = self.recomendacoes.get(tipo_bristol, [])

        return {
            "tipo_bristol": tipo_bristol,
            "confianca": round(confianca, 2),
            "recomendacoes": recomendacoes,
            "probabilidades": {i+1: float(predictions[0][i]*100) for i in range(7)}
        }
"""

# Escrever todos os arquivos
files_to_create = {
    "backend/models/models.py": MODELS_CODE,
    "backend/schemas/schemas.py": SCHEMAS_CODE,
    "backend/main.py": MAIN_CODE,
    "backend/services/ml_service.py": ML_SERVICE_CODE,
}

for filepath, content in files_to_create.items():
    with open(filepath, "w") as f:
        f.write(content)
    print(f"✅ Criado: {filepath}")

print("\n🎉 Backend completo criado com sucesso!")
print("\nPróximos passos:")
print("1. cd backend")
print("2. python3 -m venv venv")
print("3. source venv/bin/activate")
print("4. pip install -r requirements.txt")
print("5. cp .env.example .env")
print("6. python -m backend.main")
print("\nDocumentação interativa: http://localhost:8000/docs")
