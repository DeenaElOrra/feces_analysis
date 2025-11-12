# backend/main.py
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
from .models.models import Medico, Paciente, VinculoMedicoPaciente, Analise, PerfilSaude
from .schemas.schemas import (
    MedicoCreate, MedicoResponse, PacienteCreate, PacienteResponse,
    AnaliseResponse, Token, DashboardMedico, DashboardPaciente,
    PerfilSaudeCreate, PerfilSaudeResponse
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


# ========== PERFIL SAUDE ENDPOINTS ==========
@app.get("/pacientes/perfil-saude", response_model=PerfilSaudeResponse)
def get_perfil_saude(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obter perfil de saúde do paciente autenticado"""
    if current_user["type"] != "paciente":
        raise HTTPException(status_code=403, detail="Acesso negado")

    perfil = db.query(PerfilSaude).filter(PerfilSaude.paciente_id == current_user["user"].id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil de saúde não encontrado")

    return perfil


@app.post("/pacientes/perfil-saude", response_model=PerfilSaudeResponse)
def criar_perfil_saude(
    perfil_data: PerfilSaudeCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar perfil de saúde do paciente (se não existir)"""
    if current_user["type"] != "paciente":
        raise HTTPException(status_code=403, detail="Acesso negado")

    # Verificar se já existe
    perfil_existente = db.query(PerfilSaude).filter(PerfilSaude.paciente_id == current_user["user"].id).first()
    if perfil_existente:
        raise HTTPException(status_code=400, detail="Perfil de saúde já existe. Use PUT para atualizar.")

    # Criar novo perfil
    novo_perfil = PerfilSaude(
        paciente_id=current_user["user"].id,
        **perfil_data.model_dump()
    )

    db.add(novo_perfil)
    db.commit()
    db.refresh(novo_perfil)

    return novo_perfil


@app.put("/pacientes/perfil-saude", response_model=PerfilSaudeResponse)
def atualizar_perfil_saude(
    perfil_data: PerfilSaudeCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar perfil de saúde do paciente"""
    if current_user["type"] != "paciente":
        raise HTTPException(status_code=403, detail="Acesso negado")

    perfil = db.query(PerfilSaude).filter(PerfilSaude.paciente_id == current_user["user"].id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil de saúde não encontrado. Use POST para criar.")

    # Atualizar campos
    for key, value in perfil_data.model_dump().items():
        setattr(perfil, key, value)

    db.commit()
    db.refresh(perfil)

    return perfil


@app.get("/medicos/paciente/{paciente_id}/perfil-saude", response_model=PerfilSaudeResponse)
def get_perfil_saude_paciente(
    paciente_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Médico obtém perfil de saúde de um paciente vinculado"""
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

    perfil = db.query(PerfilSaude).filter(PerfilSaude.paciente_id == paciente_id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil de saúde não encontrado")

    return perfil


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
