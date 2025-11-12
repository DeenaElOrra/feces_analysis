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
import DateTimePicker from '@react-native-community/datetimepicker';
import api from '../../services/api';

export default function PatientLoginScreen({ navigation }) {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);

  // Login form
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register form
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [cpf, setCpf] = useState('');
  const [telefone, setTelefone] = useState('');
  const [dataNascimento, setDataNascimento] = useState(new Date(2000, 0, 1));
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [codigoMedico, setCodigoMedico] = useState('');
  const [senha, setSenha] = useState('');
  const [senhaConfirm, setSenhaConfirm] = useState('');
  const [showSenha, setShowSenha] = useState(false);
  const [showSenhaConfirm, setShowSenhaConfirm] = useState(false);

  const handleLogin = async () => {
    if (!loginEmail || !loginPassword) {
      Alert.alert('Erro', 'Por favor, preencha todos os campos');
      return;
    }

    setLoading(true);
    try {
      await api.loginPaciente(loginEmail, loginPassword);
      navigation.replace('PatientDashboard');
    } catch (error) {
      Alert.alert(
        'Erro ao fazer login',
        error.response?.data?.detail || error.message
      );
    } finally {
      setLoading(false);
    }
  };

  const onDateChange = (event, selectedDate) => {
    // No Android, fecha automaticamente quando seleciona ou cancela
    if (Platform.OS === 'android') {
      setShowDatePicker(false);
    }

    // Se uma data foi selecionada, atualiza o estado
    if (selectedDate) {
      setDataNascimento(selectedDate);
      // No iOS, fecha o picker após selecionar
      if (Platform.OS === 'ios') {
        setShowDatePicker(false);
      }
    }
  };

  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

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

  const handleRegister = async () => {
    if (!nome || !email || !codigoMedico || !senha || !senhaConfirm) {
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

    setLoading(true);
    try {
      const data = {
        nome,
        email,
        senha,
        codigo_medico: codigoMedico.toUpperCase(),
      };

      if (cpf) data.cpf = cpf;
      if (dataNascimento) data.data_nascimento = formatDate(dataNascimento);
      if (telefone) data.telefone = telefone;

      console.log('PatientRegister: Enviando dados:', data);

      await api.registroPaciente(data);

      Alert.alert(
        'Conta criada com sucesso!',
        'Sua conta foi criada e vinculada ao médico.\n\nAgora você pode fazer login!',
        [{ text: 'OK', onPress: () => setIsLogin(true) }]
      );
    } catch (error) {
      console.error('PatientRegister: Erro ao criar conta:', error);
      console.error('PatientRegister: Detalhes:', error.response?.data);

      const errorMsg = error.response?.data?.detail || error.message;
      if (errorMsg.includes('Email já cadastrado')) {
        Alert.alert('Erro', 'Este email já está cadastrado');
      } else if (errorMsg.includes('Código do médico inválido') || errorMsg.includes('404')) {
        Alert.alert('Erro', 'Código do médico inválido. Verifique com seu médico.');
      } else {
        Alert.alert(
          'Erro ao criar conta',
          errorMsg + '\n\nVerifique se preencheu a data de nascimento no formato YYYY-MM-DD (ex: 2000-01-15)'
        );
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
              <Text style={styles.header}>Acesso Paciente</Text>
              <Text style={styles.subtitle}>Entre ou crie sua conta</Text>
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
                Você precisa do código de convite do seu médico para criar sua conta e vincular-se a ele.
              </Text>
            </View>

            <TextInput
              style={styles.input}
              placeholder="Nome Completo *"
              value={nome}
              onChangeText={setNome}
            />
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
              placeholder="CPF"
              value={cpf}
              onChangeText={setCpf}
              keyboardType="number-pad"
            />
            <TextInput
              style={styles.input}
              placeholder="Telefone"
              value={telefone}
              onChangeText={handlePhoneChange}
              keyboardType="phone-pad"
            />

            <TouchableOpacity
              style={styles.dateButton}
              onPress={() => setShowDatePicker(true)}
            >
              <Text style={styles.dateButtonText}>
                Data de Nascimento: {formatDate(dataNascimento)}
              </Text>
            </TouchableOpacity>

            {showDatePicker && (
              <DateTimePicker
                value={dataNascimento}
                mode="date"
                display={Platform.OS === 'ios' ? 'spinner' : 'default'}
                onChange={onDateChange}
                maximumDate={new Date()}
                minimumDate={new Date(1900, 0, 1)}
              />
            )}

            <TextInput
              style={styles.input}
              placeholder="Código do Médico (ex: DR-ABC123) *"
              value={codigoMedico}
              onChangeText={setCodigoMedico}
              autoCapitalize="characters"
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
    color: '#2ca02c',
  },
  form: {
    marginBottom: 24,
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: '#f8fff8',
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#e8f5e9',
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
  dateButton: {
    borderWidth: 1.5,
    borderColor: '#e0e0e0',
    borderRadius: 10,
    padding: 14,
    marginBottom: 16,
    backgroundColor: '#fafafa',
  },
  dateButtonText: {
    fontSize: 16,
    color: '#555',
  },
  requiredText: {
    fontSize: 13,
    color: '#999',
    marginBottom: 20,
    fontStyle: 'italic',
  },
  button: {
    backgroundColor: '#2ca02c',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#2ca02c',
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
