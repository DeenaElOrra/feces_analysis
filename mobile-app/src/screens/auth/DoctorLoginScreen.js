import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
  Platform,
  KeyboardAvoidingView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import api from '../../services/api';

export default function DoctorLoginScreen({ navigation }) {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);

  // Login form
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register form
  const [nome, setNome] = useState('');
  const [crm, setCrm] = useState('');
  const [ufCrm, setUfCrm] = useState('');
  const [email, setEmail] = useState('');
  const [especialidade, setEspecialidade] = useState('');
  const [telefone, setTelefone] = useState('');
  const [senha, setSenha] = useState('');
  const [senhaConfirm, setSenhaConfirm] = useState('');
  const [showSenha, setShowSenha] = useState(false);
  const [showSenhaConfirm, setShowSenhaConfirm] = useState(false);

  const formatPhoneNumber = (text) => {
    // Remove tudo que não é número
    const numbers = text.replace(/\D/g, '');

    // Limita a 11 dígitos
    const limited = numbers.substring(0, 11);

    // Formata conforme o usuário digita
    if (limited.length <= 2) {
      return limited;
    } else if (limited.length <= 7) {
      return `(${limited.substring(0, 2)}) ${limited.substring(2)}`;
    } else {
      return `(${limited.substring(0, 2)}) ${limited.substring(2, 7)}-${limited.substring(7)}`;
    }
  };

  const handlePhoneChange = (text) => {
    const formatted = formatPhoneNumber(text);
    setTelefone(formatted);
  };

  const handleLogin = async () => {
    if (!loginEmail || !loginPassword) {
      Alert.alert('Erro', 'Por favor, preencha todos os campos');
      return;
    }

    setLoading(true);
    try {
      await api.loginMedico(loginEmail, loginPassword);
      navigation.replace('DoctorDashboard');
    } catch (error) {
      Alert.alert(
        'Erro ao fazer login',
        error.response?.data?.detail || error.message
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    if (!nome || !crm || !ufCrm || !email || !senha || !senhaConfirm) {
      Alert.alert('Erro', 'Por favor, preencha todos os campos obrigatórios (*)');
      return;
    }

    if (senha.length < 6) {
      Alert.alert('Erro', 'A senha deve ter no mínimo 6 caracteres');
      return;
    }

    if (senha !== senhaConfirm) {
      Alert.alert('Erro', 'As senhas não conferem');
      return;
    }

    if (ufCrm.length !== 2) {
      Alert.alert('Erro', 'UF do CRM deve ter 2 caracteres (ex: SP, RJ)');
      return;
    }

    setLoading(true);
    try {
      const data = {
        nome,
        crm,
        uf_crm: ufCrm.toUpperCase(),
        email,
        senha,
      };

      if (especialidade) data.especialidade = especialidade;
      if (telefone) data.telefone = telefone;

      const response = await api.registroMedico(data);

      Alert.alert(
        'Conta criada com sucesso!',
        `Seu código de convite:\n\n${response.codigo_convite}\n\nCompartilhe com seus pacientes!`,
        [{ text: 'OK', onPress: () => setIsLogin(true) }]
      );
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      if (errorMsg.includes('Email já cadastrado')) {
        Alert.alert('Erro', 'Este email já está cadastrado');
      } else if (errorMsg.includes('CRM já cadastrado')) {
        Alert.alert('Erro', 'Este CRM já está cadastrado');
      } else {
        Alert.alert('Erro ao criar conta', errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.centerContainer}>
            <View style={styles.headerContainer}>
              <Text style={styles.header}>Acesso Médico</Text>
              <Text style={styles.subtitle}>Entre ou crie sua conta profissional</Text>
            </View>

        {/* Tab Switcher */}
        <View style={styles.tabContainer}>
          <TouchableOpacity
            style={[styles.tab, isLogin && styles.activeTab]}
            onPress={() => setIsLogin(true)}
          >
            <Text style={[styles.tabText, isLogin && styles.activeTabText]}>
              Login
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.tab, !isLogin && styles.activeTab]}
            onPress={() => setIsLogin(false)}
          >
            <Text style={[styles.tabText, !isLogin && styles.activeTabText]}>
              Cadastro
            </Text>
          </TouchableOpacity>
        </View>

        {/* Login Form */}
        {isLogin ? (
          <View style={styles.form}>
            <TextInput
              style={styles.input}
              placeholder="Email"
              value={loginEmail}
              onChangeText={setLoginEmail}
              keyboardType="email-address"
              autoCapitalize="none"
            />
            <TextInput
              style={styles.input}
              placeholder="Senha"
              value={loginPassword}
              onChangeText={setLoginPassword}
              secureTextEntry={true}
            />
            <TouchableOpacity
              style={styles.button}
              onPress={handleLogin}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>Entrar</Text>
              )}
            </TouchableOpacity>
          </View>
        ) : (
          /* Register Form */
          <View style={styles.form}>
            <View style={styles.infoCard}>
              <View style={styles.infoIconContainer}>
                <Text style={styles.infoIcon}>ℹ️</Text>
              </View>
              <Text style={styles.infoText}>
                Após o cadastro, você receberá um código de convite único para compartilhar com seus pacientes.
              </Text>
            </View>

            <TextInput
              style={styles.input}
              placeholder="Nome Completo *"
              value={nome}
              onChangeText={setNome}
            />
            <View style={styles.row}>
              <TextInput
                style={[styles.input, styles.halfInput]}
                placeholder="CRM *"
                value={crm}
                onChangeText={setCrm}
              />
              <TextInput
                style={[styles.input, styles.halfInput]}
                placeholder="UF *"
                value={ufCrm}
                onChangeText={setUfCrm}
                maxLength={2}
                autoCapitalize="characters"
              />
            </View>
            <TextInput
              style={styles.input}
              placeholder="Email *"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
            />
            <TextInput
              style={styles.input}
              placeholder="Especialidade"
              value={especialidade}
              onChangeText={setEspecialidade}
            />
            <TextInput
              style={styles.input}
              placeholder="Telefone"
              value={telefone}
              onChangeText={handlePhoneChange}
              keyboardType="phone-pad"
            />
            <View style={styles.passwordContainer}>
              <TextInput
                style={styles.passwordInput}
                placeholder="Senha (mínimo 6 caracteres) *"
                value={senha}
                onChangeText={setSenha}
                secureTextEntry={!showSenha}
              />
              <TouchableOpacity
                style={styles.eyeButton}
                onPress={() => setShowSenha(!showSenha)}
              >
                <Text style={styles.eyeIcon}>{showSenha ? '👁️' : '👁️‍🗨️'}</Text>
              </TouchableOpacity>
            </View>
            <View style={styles.passwordContainer}>
              <TextInput
                style={styles.passwordInput}
                placeholder="Confirmar Senha *"
                value={senhaConfirm}
                onChangeText={setSenhaConfirm}
                secureTextEntry={!showSenhaConfirm}
              />
              <TouchableOpacity
                style={styles.eyeButton}
                onPress={() => setShowSenhaConfirm(!showSenhaConfirm)}
              >
                <Text style={styles.eyeIcon}>{showSenhaConfirm ? '👁️' : '👁️‍🗨️'}</Text>
              </TouchableOpacity>
            </View>

            <Text style={styles.requiredText}>* Campos obrigatórios</Text>

            <TouchableOpacity
              style={styles.button}
              onPress={handleRegister}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>Criar Conta</Text>
              )}
            </TouchableOpacity>
          </View>
        )}

          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.backButtonText}>Voltar</Text>
          </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 24,
    paddingBottom: 40,
  },
  headerContainer: {
    marginBottom: 32,
    alignItems: 'center',
  },
  header: {
    fontSize: 32,
    fontWeight: '700',
    textAlign: 'center',
    color: '#1a1a1a',
    marginBottom: 8,
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: 15,
    color: '#666',
    textAlign: 'center',
    fontWeight: '400',
  },
  tabContainer: {
    flexDirection: 'row',
    marginBottom: 28,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#f5f5f5',
    padding: 4,
  },
  tab: {
    flex: 1,
    padding: 14,
    alignItems: 'center',
    backgroundColor: 'transparent',
    borderRadius: 10,
  },
  activeTab: {
    backgroundColor: '#fff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  tabText: {
    fontSize: 15,
    color: '#666',
    fontWeight: '600',
  },
  activeTabText: {
    color: '#1f77b4',
  },
  form: {
    marginBottom: 24,
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: '#f8fbff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#e3f2fd',
  },
  infoIconContainer: {
    marginRight: 12,
    marginTop: 2,
  },
  infoIcon: {
    fontSize: 20,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#555',
    lineHeight: 20,
  },
  input: {
    borderWidth: 1.5,
    borderColor: '#e0e0e0',
    borderRadius: 10,
    padding: 14,
    marginBottom: 16,
    fontSize: 16,
    backgroundColor: '#fafafa',
    color: '#333',
  },
  passwordContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1.5,
    borderColor: '#e0e0e0',
    borderRadius: 10,
    marginBottom: 16,
    backgroundColor: '#fafafa',
  },
  passwordInput: {
    flex: 1,
    padding: 14,
    fontSize: 16,
    color: '#333',
  },
  eyeButton: {
    padding: 12,
  },
  eyeIcon: {
    fontSize: 20,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  halfInput: {
    width: '48%',
  },
  requiredText: {
    fontSize: 13,
    color: '#999',
    marginBottom: 20,
    fontStyle: 'italic',
  },
  button: {
    backgroundColor: '#1f77b4',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#1f77b4',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  buttonText: {
    color: '#fff',
    fontSize: 17,
    fontWeight: '600',
    letterSpacing: 0.5,
  },
  backButton: {
    padding: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  backButtonText: {
    fontSize: 15,
    color: '#999',
    fontWeight: '500',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    width: '100%',
  },
});
