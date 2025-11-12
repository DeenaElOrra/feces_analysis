# frontend/utils/api_client.py
import requests
from typing import Optional, Dict, Any
import streamlit as st


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """Get headers with optional authentication token"""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    # ========== AUTH ENDPOINTS ==========
    def registro_medico(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new doctor"""
        response = self.session.post(
            f"{self.base_url}/auth/registro-medico",
            json=data
        )
        response.raise_for_status()
        return response.json()

    def registro_paciente(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new patient"""
        response = self.session.post(
            f"{self.base_url}/auth/registro-paciente",
            json=data
        )
        response.raise_for_status()
        return response.json()

    def login(self, email: str, senha: str) -> Dict[str, Any]:
        """Login (doctor or patient)"""
        response = self.session.post(
            f"{self.base_url}/auth/login",
            data={"email": email, "senha": senha}
        )
        response.raise_for_status()
        return response.json()

    # ========== MEDICO ENDPOINTS ==========
    def get_perfil_medico(self, token: str) -> Dict[str, Any]:
        """Get doctor profile"""
        response = self.session.get(
            f"{self.base_url}/medicos/perfil",
            headers=self._get_headers(token)
        )
        response.raise_for_status()
        return response.json()

    def get_pacientes(self, token: str) -> list:
        """Get list of patients"""
        response = self.session.get(
            f"{self.base_url}/medicos/pacientes",
            headers=self._get_headers(token)
        )
        response.raise_for_status()
        return response.json()

    def get_analises_paciente(self, token: str, paciente_id: str) -> list:
        """Get patient's analysis history"""
        response = self.session.get(
            f"{self.base_url}/medicos/paciente/{paciente_id}/analises",
            headers=self._get_headers(token)
        )
        response.raise_for_status()
        return response.json()

    # ========== PACIENTE ENDPOINTS ==========
    def get_perfil_paciente(self, token: str) -> Dict[str, Any]:
        """Get patient profile"""
        response = self.session.get(
            f"{self.base_url}/pacientes/perfil",
            headers=self._get_headers(token)
        )
        response.raise_for_status()
        return response.json()

    def criar_analise(self, token: str, imagem, observacoes: Optional[str] = None) -> Dict[str, Any]:
        """Upload and analyze feces image"""
        files = {"imagem": imagem}
        data = {}
        if observacoes:
            data["observacoes"] = observacoes

        response = self.session.post(
            f"{self.base_url}/pacientes/analise",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
            data=data
        )
        response.raise_for_status()
        return response.json()

    def get_minhas_analises(self, token: str) -> list:
        """Get my analysis history"""
        response = self.session.get(
            f"{self.base_url}/pacientes/analises",
            headers=self._get_headers(token)
        )
        response.raise_for_status()
        return response.json()

    # ========== HEALTH CHECK ==========
    def health_check(self) -> Dict[str, Any]:
        """Check if API is running"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


# Global API client instance
def get_api_client() -> APIClient:
    """Get or create API client instance"""
    if 'api_client' not in st.session_state:
        # Try to get backend URL from environment or use default
        backend_url = "http://localhost:8000"
        st.session_state.api_client = APIClient(backend_url)
    return st.session_state.api_client
