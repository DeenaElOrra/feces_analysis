# backend/models/models.py
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


class PerfilSaude(Base):
    __tablename__ = "perfis_saude"

    id = Column(String, primary_key=True, default=generate_uuid)
    paciente_id = Column(String, ForeignKey("pacientes.id"), unique=True, nullable=False)

    # Histórico Intestinal
    padrao_intestinal = Column(String(50))  # constipado, normal, diarreico, oscilante
    sintomas_intestinais = Column(String)  # JSON string com checkboxes

    # Condições de Saúde
    diagnosticos = Column(String)  # JSON string com condições
    cirurgias_abdominais = Column(Boolean, default=False)
    descricao_cirurgias = Column(String)

    # Medicamentos e Suplementos
    uso_antibioticos_recente = Column(Boolean, default=False)
    uso_laxantes = Column(Boolean, default=False)
    uso_antidiarreicos = Column(Boolean, default=False)
    uso_probioticos = Column(Boolean, default=False)
    outros_medicamentos = Column(String)

    # Alergias e Intolerâncias
    alergias_intolerâncias = Column(String)  # JSON string

    # Estilo de Vida
    tipo_dieta = Column(String(50))
    consumo_agua = Column(Float)  # litros por dia
    frequencia_atividade = Column(String(50))
    nivel_estresse = Column(Integer)  # 1-5
    qualidade_sono = Column(Integer)  # 1-5

    # Histórico Familiar
    doencas_intestinais_familia = Column(Boolean, default=False)
    descricao_hist_familiar = Column(String)

    # Observações gerais
    observacoes_gerais = Column(String)

    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Relacionamento
    paciente = relationship("Paciente", foreign_keys=[paciente_id])
