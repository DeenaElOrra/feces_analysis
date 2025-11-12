import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function WelcomeScreen({ navigation }) {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Bem-vindo à</Text>
        <Text style={styles.appName}>Flora</Text>
        <Text style={styles.subtitle}>
          Análise inteligente de saúde intestinal
        </Text>

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.button, styles.doctorButton]}
            onPress={() => navigation.navigate('DoctorLogin')}
          >
            <Text style={styles.emoji}>👨‍⚕️</Text>
            <Text style={styles.buttonText}>Sou Médico</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.patientButton]}
            onPress={() => navigation.navigate('PatientLogin')}
          >
            <Text style={styles.emoji}>🧑</Text>
            <Text style={styles.buttonText}>Sou Paciente</Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    color: '#666',
    marginBottom: 5,
  },
  appName: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#999',
    textAlign: 'center',
    marginBottom: 60,
  },
  buttonContainer: {
    width: '100%',
    maxWidth: 300,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 18,
    borderRadius: 12,
    marginBottom: 15,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  doctorButton: {
    backgroundColor: '#1f77b4',
  },
  patientButton: {
    backgroundColor: '#2ca02c',
  },
  emoji: {
    fontSize: 24,
    marginRight: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
