# backend/schemas/schemas.py
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


# ========== PERFIL SAUDE ==========
class PerfilSaudeCreate(BaseModel):
    # Histórico Intestinal
    padrao_intestinal: Optional[str] = Field(None, max_length=50, description="constipado, normal, diarreico, oscilante")
    sintomas_intestinais: Optional[str] = Field(None, description="JSON string com checkboxes de sintomas")

    # Condições de Saúde
    diagnosticos: Optional[str] = Field(None, description="JSON string com condições de saúde")
    cirurgias_abdominais: Optional[bool] = False
    descricao_cirurgias: Optional[str] = None

    # Medicamentos e Suplementos
    uso_antibioticos_recente: Optional[bool] = False
    uso_laxantes: Optional[bool] = False
    uso_antidiarreicos: Optional[bool] = False
    uso_probioticos: Optional[bool] = False
    outros_medicamentos: Optional[str] = None

    # Alergias e Intolerâncias
    alergias_intolerâncias: Optional[str] = Field(None, description="JSON string com alergias")

    # Estilo de Vida
    tipo_dieta: Optional[str] = Field(None, max_length=50)
    consumo_agua: Optional[float] = Field(None, ge=0, le=10, description="Litros por dia")
    frequencia_atividade: Optional[str] = Field(None, max_length=50)
    nivel_estresse: Optional[int] = Field(None, ge=1, le=5, description="Escala de 1 a 5")
    qualidade_sono: Optional[int] = Field(None, ge=1, le=5, description="Escala de 1 a 5")

    # Histórico Familiar
    doencas_intestinais_familia: Optional[bool] = False
    descricao_hist_familiar: Optional[str] = None

    # Observações
    observacoes_gerais: Optional[str] = None


class PerfilSaudeResponse(BaseModel):
    id: str
    paciente_id: str

    # Histórico Intestinal
    padrao_intestinal: Optional[str]
    sintomas_intestinais: Optional[str]

    # Condições de Saúde
    diagnosticos: Optional[str]
    cirurgias_abdominais: bool
    descricao_cirurgias: Optional[str]

    # Medicamentos e Suplementos
    uso_antibioticos_recente: bool
    uso_laxantes: bool
    uso_antidiarreicos: bool
    uso_probioticos: bool
    outros_medicamentos: Optional[str]

    # Alergias e Intolerâncias
    alergias_intolerâncias: Optional[str]

    # Estilo de Vida
    tipo_dieta: Optional[str]
    consumo_agua: Optional[float]
    frequencia_atividade: Optional[str]
    nivel_estresse: Optional[int]
    qualidade_sono: Optional[int]

    # Histórico Familiar
    doencas_intestinais_familia: bool
    descricao_hist_familiar: Optional[str]

    # Observações
    observacoes_gerais: Optional[str]

    # Timestamps
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True
