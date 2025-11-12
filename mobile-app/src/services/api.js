import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Change this to your backend URL
const API_URL = 'http://172.20.10.2:8000';

class APIClient {
  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to add auth token
    this.client.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, clear storage
          await AsyncStorage.multiRemove(['token', 'refreshToken', 'userType']);
        }
        return Promise.reject(error);
      }
    );
  }

  // ========== AUTH ENDPOINTS ==========

  async loginMedico(email, senha) {
    const formData = new FormData();
    formData.append('email', email);
    formData.append('senha', senha);

    const response = await this.client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    if (response.data.tipo_usuario === 'medico') {
      await AsyncStorage.setItem('token', response.data.access_token);
      await AsyncStorage.setItem('refreshToken', response.data.refresh_token);
      await AsyncStorage.setItem('userType', 'medico');
      return response.data;
    } else {
      throw new Error('Esta conta não é de médico');
    }
  }

  async loginPaciente(email, senha) {
    const formData = new FormData();
    formData.append('email', email);
    formData.append('senha', senha);

    const response = await this.client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    if (response.data.tipo_usuario === 'paciente') {
      await AsyncStorage.setItem('token', response.data.access_token);
      await AsyncStorage.setItem('refreshToken', response.data.refresh_token);
      await AsyncStorage.setItem('userType', 'paciente');
      return response.data;
    } else {
      throw new Error('Esta conta não é de paciente');
    }
  }

  async registroMedico(data) {
    // Remove empty optional fields
    const cleanData = { ...data };
    if (!cleanData.especialidade) delete cleanData.especialidade;
    if (!cleanData.telefone) delete cleanData.telefone;

    const response = await this.client.post('/auth/registro-medico', cleanData);
    return response.data;
  }

  async registroPaciente(data) {
    // Remove empty optional fields
    const cleanData = { ...data };
    if (!cleanData.cpf) delete cleanData.cpf;
    if (!cleanData.data_nascimento) delete cleanData.data_nascimento;
    if (!cleanData.telefone) delete cleanData.telefone;

    const response = await this.client.post('/auth/registro-paciente', cleanData);
    return response.data;
  }

  async logout() {
    await AsyncStorage.multiRemove(['token', 'refreshToken', 'userType']);
  }

  // ========== MEDICO ENDPOINTS ==========

  async getMedicoPerfil() {
    const response = await this.client.get('/medicos/perfil');
    return response.data;
  }

  async getMedicoPacientes() {
    const response = await this.client.get('/medicos/pacientes');
    return response.data;
  }

  async getMedicoPacienteAnalises(pacienteId) {
    const response = await this.client.get(`/medicos/paciente/${pacienteId}/analises`);
    return response.data;
  }

  // ========== PACIENTE ENDPOINTS ==========

  async getPacientePerfil() {
    const response = await this.client.get('/pacientes/perfil');
    return response.data;
  }

  async getPacienteAnalises() {
    const response = await this.client.get('/pacientes/analises');
    return response.data;
  }

  async criarAnalise(imageUri, observacoes = '') {
    const formData = new FormData();

    // Get filename from URI
    const filename = imageUri.split('/').pop();
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : 'image/jpeg';

    formData.append('imagem', {
      uri: imageUri,
      name: filename,
      type: type,
    });

    if (observacoes) {
      formData.append('observacoes', observacoes);
    }

    const response = await this.client.post('/pacientes/analise', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    return response.data;
  }

  // ========== PERFIL SAUDE ENDPOINTS ==========

  async getPerfilSaude() {
    const response = await this.client.get('/pacientes/perfil-saude');
    return response.data;
  }

  async criarPerfilSaude(perfilData) {
    const response = await this.client.post('/pacientes/perfil-saude', perfilData);
    return response.data;
  }

  async atualizarPerfilSaude(perfilData) {
    const response = await this.client.put('/pacientes/perfil-saude', perfilData);
    return response.data;
  }

  async getPerfilSaudePaciente(pacienteId) {
    const response = await this.client.get(`/medicos/paciente/${pacienteId}/perfil-saude`);
    return response.data;
  }

  // ========== HELPER METHODS ==========

  async isAuthenticated() {
    const token = await AsyncStorage.getItem('token');
    return !!token;
  }

  async getUserType() {
    return await AsyncStorage.getItem('userType');
  }
}

export default new APIClient();
