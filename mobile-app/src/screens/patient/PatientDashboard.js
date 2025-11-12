import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Image,
  TextInput,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import api from '../../services/api';
import HealthProfileForm from './HealthProfileForm';

const screenWidth = Dimensions.get('window').width;

export default function PatientDashboard({ navigation }) {
  const [loading, setLoading] = useState(true);
  const [perfil, setPerfil] = useState(null);
  const [analises, setAnalises] = useState([]);
  const [activeTab, setActiveTab] = useState('nova'); // 'nova', 'historico', 'stats', 'perfil'

  // New analysis state
  const [selectedImage, setSelectedImage] = useState(null);
  const [observacoes, setObservacoes] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [resultado, setResultado] = useState(null);

  // Health profile state
  const [perfilSaude, setPerfilSaude] = useState(null);
  const [savingPerfil, setSavingPerfil] = useState(false);
  const [formData, setFormData] = useState({
    padrao_intestinal: '',
    sintomas_intestinais: '',
    diagnosticos: '',
    cirurgias_abdominais: false,
    descricao_cirurgias: '',
    uso_antibioticos_recente: false,
    uso_laxantes: false,
    uso_antidiarreicos: false,
    uso_probioticos: false,
    outros_medicamentos: '',
    alergias_intolerâncias: '',
    tipo_dieta: '',
    consumo_agua: '',
    frequencia_atividade: '',
    nivel_estresse: null,
    qualidade_sono: null,
    doencas_intestinais_familia: false,
    descricao_hist_familiar: '',
    observacoes_gerais: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [perfilData, analisesData] = await Promise.all([
        api.getPacientePerfil(),
        api.getPacienteAnalises(),
      ]);
      setPerfil(perfilData);
      setAnalises(analisesData);

      // Try to load health profile (might not exist yet)
      try {
        const perfilSaudeData = await api.getPerfilSaude();
        setPerfilSaude(perfilSaudeData);
        setFormData({
          padrao_intestinal: perfilSaudeData.padrao_intestinal || '',
          sintomas_intestinais: perfilSaudeData.sintomas_intestinais || '',
          diagnosticos: perfilSaudeData.diagnosticos || '',
          cirurgias_abdominais: perfilSaudeData.cirurgias_abdominais || false,
          descricao_cirurgias: perfilSaudeData.descricao_cirurgias || '',
          uso_antibioticos_recente: perfilSaudeData.uso_antibioticos_recente || false,
          uso_laxantes: perfilSaudeData.uso_laxantes || false,
          uso_antidiarreicos: perfilSaudeData.uso_antidiarreicos || false,
          uso_probioticos: perfilSaudeData.uso_probioticos || false,
          outros_medicamentos: perfilSaudeData.outros_medicamentos || '',
          alergias_intolerâncias: perfilSaudeData.alergias_intolerâncias || '',
          tipo_dieta: perfilSaudeData.tipo_dieta || '',
          consumo_agua: perfilSaudeData.consumo_agua ? String(perfilSaudeData.consumo_agua) : '',
          frequencia_atividade: perfilSaudeData.frequencia_atividade || '',
          nivel_estresse: perfilSaudeData.nivel_estresse,
          qualidade_sono: perfilSaudeData.qualidade_sono,
          doencas_intestinais_familia: perfilSaudeData.doencas_intestinais_familia || false,
          descricao_hist_familiar: perfilSaudeData.descricao_hist_familiar || '',
          observacoes_gerais: perfilSaudeData.observacoes_gerais || '',
        });
      } catch (perfilError) {
        // Profile doesn't exist yet, keep default empty form
        console.log('Perfil de saúde não encontrado, será criado ao salvar');
      }
    } catch (error) {
      Alert.alert('Erro', 'Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  const pickImage = async (useCamera) => {
    try {
      const permission = useCamera
        ? await ImagePicker.requestCameraPermissionsAsync()
        : await ImagePicker.requestMediaLibraryPermissionsAsync();

      if (!permission.granted) {
        Alert.alert('Permissão negada', 'É necessário permitir acesso à câmera/galeria');
        return;
      }

      const result = useCamera
        ? await ImagePicker.launchCameraAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            allowsEditing: true,
            aspect: [4, 3],
            quality: 0.8,
          })
        : await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            allowsEditing: true,
            aspect: [4, 3],
            quality: 0.8,
          });

      if (!result.canceled) {
        setSelectedImage(result.assets[0].uri);
        setResultado(null);
      }
    } catch (error) {
      Alert.alert('Erro', 'Erro ao selecionar imagem');
    }
  };

  const handleAnalyze = async () => {
    if (!selectedImage) {
      Alert.alert('Erro', 'Por favor, selecione uma imagem');
      return;
    }

    setAnalyzing(true);
    try {
      const result = await api.criarAnalise(selectedImage, observacoes);
      setResultado(result);

      // Reload history
      const analisesData = await api.getPacienteAnalises();
      setAnalises(analisesData);

      Alert.alert('Sucesso', 'Análise concluída!');
    } catch (error) {
      Alert.alert('Erro', 'Erro ao analisar imagem: ' + error.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setSelectedImage(null);
    setObservacoes('');
    setResultado(null);
  };

  const handleSavePerfil = async () => {
    setSavingPerfil(true);
    try {
      // Prepare data - convert consumo_agua to float
      const dataToSend = {
        ...formData,
        consumo_agua: formData.consumo_agua ? parseFloat(formData.consumo_agua) : null,
      };

      // If profile exists, update it; otherwise create it
      if (perfilSaude) {
        await api.atualizarPerfilSaude(dataToSend);
        Alert.alert('Sucesso', 'Perfil de saúde atualizado!');
      } else {
        const novoPerfil = await api.criarPerfilSaude(dataToSend);
        setPerfilSaude(novoPerfil);
        Alert.alert('Sucesso', 'Perfil de saúde criado!');
      }
    } catch (error) {
      console.error('Erro ao salvar perfil:', error);
      Alert.alert('Erro', 'Erro ao salvar perfil de saúde: ' + error.message);
    } finally {
      setSavingPerfil(false);
    }
  };

  const handleLogout = async () => {
    Alert.alert('Sair', 'Deseja realmente sair?', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Sair',
        onPress: async () => {
          await api.logout();
          navigation.replace('Welcome');
        },
      },
    ]);
  };

  const getBristolColor = (tipo) => {
    const colors = {
      1: '#8B4513',
      2: '#A0522D',
      3: '#CD853F',
      4: '#DEB887',
      5: '#F4A460',
      6: '#FFD700',
      7: '#FFA500',
    };
    return colors[tipo] || '#999';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR') + ' às ' + date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  const groupAnalisesByPeriod = () => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

    const grupos = {
      hoje: [],
      semana: [],
      mes: [],
      antigo: [],
    };

    analises.forEach((analise) => {
      const date = new Date(analise.analisado_em);
      if (date >= today) {
        grupos.hoje.push(analise);
      } else if (date >= weekAgo) {
        grupos.semana.push(analise);
      } else if (date >= monthAgo) {
        grupos.mes.push(analise);
      } else {
        grupos.antigo.push(analise);
      }
    });

    return grupos;
  };

  const calculateStats = () => {
    if (analises.length === 0) return null;

    // Contagem por tipo
    const counts = {};
    analises.forEach((a) => {
      counts[a.tipo_bristol] = (counts[a.tipo_bristol] || 0) + 1;
    });

    // Tipo mais frequente
    const mostFrequent = Object.entries(counts).reduce((a, b) =>
      counts[a[0]] > counts[b[0]] ? a : b
    )[0];

    // Últimos 7 dias
    const last7Days = analises.filter((a) => {
      const date = new Date(a.analisado_em);
      const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
      return date >= weekAgo;
    });

    return {
      total: analises.length,
      mostFrequent: parseInt(mostFrequent),
      last7DaysCount: last7Days.length,
      distribution: counts,
    };
  };

  const renderChart = () => {
    const stats = calculateStats();
    if (!stats) return null;

    const maxCount = Math.max(...Object.values(stats.distribution));
    const chartWidth = screenWidth - 120;

    return (
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Distribuição por Tipo Bristol</Text>
        {[1, 2, 3, 4, 5, 6, 7].map((tipo) => {
          const count = stats.distribution[tipo] || 0;
          const percentage = (count / stats.total) * 100;
          const barWidth = maxCount > 0 ? (count / maxCount) * chartWidth : 0;

          return (
            <View key={tipo} style={styles.chartRow}>
              <View style={styles.chartLabelContainer}>
                <View
                  style={[
                    styles.chartColorBox,
                    { backgroundColor: getBristolColor(tipo) },
                  ]}
                />
                <Text style={styles.chartLabel}>Tipo {tipo}</Text>
              </View>
              <View style={styles.chartBarContainer}>
                <View
                  style={[
                    styles.chartBar,
                    { width: barWidth, backgroundColor: getBristolColor(tipo) },
                  ]}
                />
                <Text style={styles.chartValue}>
                  {count} ({percentage.toFixed(0)}%)
                </Text>
              </View>
            </View>
          );
        })}
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#2ca02c" />
      </View>
    );
  }

  const grupos = groupAnalisesByPeriod();
  const stats = calculateStats();

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <Text style={styles.headerTitle}>Dashboard Paciente</Text>
          <Text style={styles.headerSubtitle}>{perfil?.nome}</Text>
        </View>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>Sair</Text>
        </TouchableOpacity>
      </View>

      {/* Tabs */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'nova' && styles.activeTab]}
          onPress={() => setActiveTab('nova')}
        >
          <Text style={[styles.tabText, activeTab === 'nova' && styles.activeTabText]}>
            Nova
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'historico' && styles.activeTab]}
          onPress={() => setActiveTab('historico')}
        >
          <Text style={[styles.tabText, activeTab === 'historico' && styles.activeTabText]}>
            Histórico
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'stats' && styles.activeTab]}
          onPress={() => setActiveTab('stats')}
        >
          <Text style={[styles.tabText, activeTab === 'stats' && styles.activeTabText]}>
            Estatísticas
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'perfil' && styles.activeTab]}
          onPress={() => setActiveTab('perfil')}
        >
          <Text style={[styles.tabText, activeTab === 'perfil' && styles.activeTabText]}>
            Perfil
          </Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      {activeTab === 'perfil' ? (
        /* Perfil Tab - No outer ScrollView since HealthProfileForm has its own */
        <HealthProfileForm
          formData={formData}
          setFormData={setFormData}
          onSave={handleSavePerfil}
          saving={savingPerfil}
        />
      ) : (
        <ScrollView style={styles.content}>
          {activeTab === 'nova' ? (
          /* New Analysis Tab */
          <View>
            <Text style={styles.sectionTitle}>Tire ou selecione uma foto</Text>

            {selectedImage && (
              <Image source={{ uri: selectedImage }} style={styles.imagePreview} />
            )}

            <View style={styles.buttonRow}>
              <TouchableOpacity
                style={[styles.button, styles.cameraButton]}
                onPress={() => pickImage(true)}
              >
                <Text style={styles.buttonText}>Câmera</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.button, styles.galleryButton]}
                onPress={() => pickImage(false)}
              >
                <Text style={styles.buttonText}>Galeria</Text>
              </TouchableOpacity>
            </View>

            {selectedImage && (
              <>
                <TextInput
                  style={styles.textArea}
                  placeholder="Observações (opcional)"
                  value={observacoes}
                  onChangeText={setObservacoes}
                  multiline={true}
                  numberOfLines={4}
                />

                <TouchableOpacity
                  style={[styles.button, styles.analyzeButton]}
                  onPress={handleAnalyze}
                  disabled={analyzing}
                >
                  {analyzing ? (
                    <ActivityIndicator color="#fff" />
                  ) : (
                    <Text style={styles.buttonText}>Analisar Agora</Text>
                  )}
                </TouchableOpacity>
              </>
            )}

            {resultado && (
              <View style={styles.resultCard}>
                <Text style={styles.resultTitle}>Resultado da Análise</Text>

                <View
                  style={[
                    styles.bristolBadge,
                    { backgroundColor: getBristolColor(resultado.tipo_bristol) },
                  ]}
                >
                  <Text style={styles.bristolText}>
                    Tipo Bristol {resultado.tipo_bristol}
                  </Text>
                </View>

                {resultado.recomendacoes && resultado.recomendacoes.length > 0 && (
                  <View style={styles.recomendacoesContainer}>
                    <Text style={styles.recomendacoesTitle}>Recomendações:</Text>
                    {resultado.recomendacoes.map((rec, idx) => (
                      <Text key={idx} style={styles.recomendacaoItem}>
                        • {rec}
                      </Text>
                    ))}
                  </View>
                )}

                <TouchableOpacity
                  style={[styles.button, styles.newButton]}
                  onPress={resetAnalysis}
                >
                  <Text style={styles.buttonText}>Nova Análise</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        ) : activeTab === 'historico' ? (
          /* History Tab */
          <View>
            <Text style={styles.sectionTitle}>
              Meu Histórico ({analises.length})
            </Text>

            {analises.length === 0 ? (
              <Text style={styles.emptyText}>
                Você ainda não fez análises.
              </Text>
            ) : (
              <>
                {/* Hoje */}
                {grupos.hoje.length > 0 && (
                  <>
                    <Text style={styles.periodTitle}>Hoje</Text>
                    {grupos.hoje.map((analise) => (
                      <View key={analise.id} style={styles.analiseCard}>
                        <View
                          style={[
                            styles.bristolBadge,
                            { backgroundColor: getBristolColor(analise.tipo_bristol) },
                          ]}
                        >
                          <Text style={styles.bristolText}>
                            Tipo {analise.tipo_bristol}
                          </Text>
                        </View>

                        <Text style={styles.analiseDate}>
                          {formatDate(analise.analisado_em)}
                        </Text>

                        {analise.observacoes && (
                          <Text style={styles.observacoes}>
                            Obs: {analise.observacoes}
                          </Text>
                        )}

                        {analise.recomendacoes && analise.recomendacoes.length > 0 && (
                          <View style={styles.recomendacoesContainer}>
                            <Text style={styles.recomendacoesTitle}>
                              Recomendações:
                            </Text>
                            {analise.recomendacoes.map((rec, idx) => (
                              <Text key={idx} style={styles.recomendacaoItem}>
                                • {rec}
                              </Text>
                            ))}
                          </View>
                        )}
                      </View>
                    ))}
                  </>
                )}

                {/* Esta Semana */}
                {grupos.semana.length > 0 && (
                  <>
                    <Text style={styles.periodTitle}>Esta Semana</Text>
                    {grupos.semana.map((analise) => (
                      <View key={analise.id} style={styles.analiseCard}>
                        <View
                          style={[
                            styles.bristolBadge,
                            { backgroundColor: getBristolColor(analise.tipo_bristol) },
                          ]}
                        >
                          <Text style={styles.bristolText}>
                            Tipo {analise.tipo_bristol}
                          </Text>
                        </View>

                        <Text style={styles.analiseDate}>
                          {formatDate(analise.analisado_em)}
                        </Text>

                        {analise.observacoes && (
                          <Text style={styles.observacoes}>
                            Obs: {analise.observacoes}
                          </Text>
                        )}
                      </View>
                    ))}
                  </>
                )}

                {/* Este Mês */}
                {grupos.mes.length > 0 && (
                  <>
                    <Text style={styles.periodTitle}>Este Mês</Text>
                    {grupos.mes.map((analise) => (
                      <View key={analise.id} style={styles.analiseCard}>
                        <View
                          style={[
                            styles.bristolBadge,
                            { backgroundColor: getBristolColor(analise.tipo_bristol) },
                          ]}
                        >
                          <Text style={styles.bristolText}>
                            Tipo {analise.tipo_bristol}
                          </Text>
                        </View>

                        <Text style={styles.analiseDate}>
                          {formatDate(analise.analisado_em)}
                        </Text>

                        {analise.observacoes && (
                          <Text style={styles.observacoes}>
                            Obs: {analise.observacoes}
                          </Text>
                        )}
                      </View>
                    ))}
                  </>
                )}

                {/* Mais Antigo */}
                {grupos.antigo.length > 0 && (
                  <>
                    <Text style={styles.periodTitle}>Mais Antigo</Text>
                    {grupos.antigo.map((analise) => (
                      <View key={analise.id} style={styles.analiseCard}>
                        <View
                          style={[
                            styles.bristolBadge,
                            { backgroundColor: getBristolColor(analise.tipo_bristol) },
                          ]}
                        >
                          <Text style={styles.bristolText}>
                            Tipo {analise.tipo_bristol}
                          </Text>
                        </View>

                        <Text style={styles.analiseDate}>
                          {formatDate(analise.analisado_em)}
                        </Text>

                        {analise.observacoes && (
                          <Text style={styles.observacoes}>
                            Obs: {analise.observacoes}
                          </Text>
                        )}
                      </View>
                    ))}
                  </>
                )}
              </>
            )}
          </View>
        ) : (
          /* Statistics Tab */
          <View>
            <Text style={styles.sectionTitle}>Estatísticas</Text>

            {!stats ? (
              <Text style={styles.emptyText}>
                Você ainda não tem análises suficientes para gerar estatísticas.
              </Text>
            ) : (
              <>
                {/* Summary Cards */}
                <View style={styles.statsGrid}>
                  <View style={styles.statCard}>
                    <Text style={styles.statValue}>{stats.total}</Text>
                    <Text style={styles.statLabel}>Total de Análises</Text>
                  </View>
                  <View style={styles.statCard}>
                    <Text style={styles.statValue}>{stats.last7DaysCount}</Text>
                    <Text style={styles.statLabel}>Últimos 7 Dias</Text>
                  </View>
                </View>

                <View style={styles.statCardWide}>
                  <Text style={styles.statLabel}>Tipo Mais Frequente</Text>
                  <View
                    style={[
                      styles.bristolBadgeLarge,
                      { backgroundColor: getBristolColor(stats.mostFrequent) },
                    ]}
                  >
                    <Text style={styles.bristolTextLarge}>
                      Tipo {stats.mostFrequent}
                    </Text>
                  </View>
                </View>

                {/* Chart */}
                {renderChart()}

                {/* Frequency Chart */}
                {(() => {
                  // Group analyses by date and count frequency
                  const frequencyByDate = {};
                  analises.forEach(analise => {
                    const date = new Date(analise.analisado_em).toLocaleDateString('pt-BR');
                    frequencyByDate[date] = (frequencyByDate[date] || 0) + 1;
                  });

                  // Get last 14 days (including days with no data)
                  const today = new Date();
                  const last14Days = [];
                  for (let i = 13; i >= 0; i--) {
                    const date = new Date(today);
                    date.setDate(today.getDate() - i);
                    const dateStr = date.toLocaleDateString('pt-BR');
                    last14Days.push(dateStr);
                    // Initialize with 0 if no data
                    if (!frequencyByDate[dateStr]) {
                      frequencyByDate[dateStr] = 0;
                    }
                  }

                  const maxFrequency = Math.max(...last14Days.map(date => frequencyByDate[date]), 1);

                  return (
                    <View style={styles.timelineChartContainer}>
                      <Text style={styles.chartTitle}>Frequência de Idas ao Banheiro</Text>
                      <Text style={styles.timelineSubtitle}>
                        Últimos 14 dias
                      </Text>

                      <View style={styles.frequencyChart}>
                        {/* Y-axis scale */}
                        <View style={styles.yAxisFreq}>
                          {[maxFrequency, Math.ceil(maxFrequency / 2), 0].map((value, idx) => (
                            <View key={idx} style={styles.yAxisFreqLabel}>
                              <Text style={styles.yAxisFreqText}>{value}</Text>
                            </View>
                          ))}
                        </View>

                        {/* Bars */}
                        <View style={styles.barsContainer}>
                          {last14Days.map((date, index) => {
                            const count = frequencyByDate[date];
                            const heightPercent = (count / maxFrequency) * 100;

                            return (
                              <View key={date} style={styles.barColumn}>
                                <View style={styles.barWrapper}>
                                  <View
                                    style={[
                                      styles.bar,
                                      {
                                        height: `${heightPercent}%`,
                                        backgroundColor: count === 0 ? '#9E9E9E' : count >= 3 ? '#4CAF50' : count >= 2 ? '#FFC107' : '#FF5722',
                                      },
                                    ]}
                                  >
                                    <Text style={styles.barLabel}>{count}</Text>
                                  </View>
                                </View>
                                <Text style={styles.dateLabel} numberOfLines={1}>
                                  {date.split('/').slice(0, 2).join('/')}
                                </Text>
                              </View>
                            );
                          })}
                        </View>
                      </View>

                      {/* Legend */}
                      <View style={styles.timelineLegend}>
                        <Text style={styles.legendTitle}>Frequência:</Text>
                        <View style={styles.legendItems}>
                          <View style={styles.legendItem}>
                            <View style={[styles.legendDot, { backgroundColor: '#4CAF50' }]} />
                            <Text style={styles.legendText}>3+: Normal</Text>
                          </View>
                          <View style={styles.legendItem}>
                            <View style={[styles.legendDot, { backgroundColor: '#FFC107' }]} />
                            <Text style={styles.legendText}>2: Atenção</Text>
                          </View>
                          <View style={styles.legendItem}>
                            <View style={[styles.legendDot, { backgroundColor: '#FF5722' }]} />
                            <Text style={styles.legendText}>1: Baixo</Text>
                          </View>
                          <View style={styles.legendItem}>
                            <View style={[styles.legendDot, { backgroundColor: '#9E9E9E' }]} />
                            <Text style={styles.legendText}>0: Constipação</Text>
                          </View>
                        </View>
                      </View>
                    </View>
                  );
                })()}
              </>
            )}
          </View>
        )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fafafa',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fafafa',
  },
  header: {
    backgroundColor: '#fff',
    paddingHorizontal: 24,
    paddingVertical: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  headerContent: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1a1a1a',
    letterSpacing: -0.5,
  },
  headerSubtitle: {
    fontSize: 15,
    color: '#666',
    marginTop: 4,
    fontWeight: '400',
  },
  logoutButton: {
    backgroundColor: '#f5f5f5',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  logoutButtonText: {
    color: '#666',
    fontSize: 15,
    fontWeight: '600',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    paddingHorizontal: 4,
  },
  tab: {
    flex: 1,
    padding: 16,
    alignItems: 'center',
    borderBottomWidth: 3,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: '#2ca02c',
  },
  tabText: {
    fontSize: 15,
    color: '#666',
    fontWeight: '600',
  },
  activeTabText: {
    color: '#2ca02c',
    fontWeight: '700',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 16,
    letterSpacing: -0.3,
  },
  periodTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#2ca02c',
    marginTop: 16,
    marginBottom: 10,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  imagePreview: {
    width: '100%',
    height: 250,
    borderRadius: 12,
    marginBottom: 16,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  button: {
    flex: 1,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginHorizontal: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  cameraButton: {
    backgroundColor: '#2ca02c',
    shadowColor: '#2ca02c',
  },
  galleryButton: {
    backgroundColor: '#1f77b4',
    shadowColor: '#1f77b4',
  },
  analyzeButton: {
    backgroundColor: '#ff7f0e',
    width: '100%',
    shadowColor: '#ff7f0e',
  },
  newButton: {
    backgroundColor: '#2ca02c',
    width: '100%',
    marginTop: 16,
    shadowColor: '#2ca02c',
  },
  buttonText: {
    color: '#fff',
    fontSize: 17,
    fontWeight: '600',
    letterSpacing: 0.5,
  },
  textArea: {
    borderWidth: 1.5,
    borderColor: '#e0e0e0',
    borderRadius: 10,
    padding: 14,
    marginBottom: 16,
    fontSize: 16,
    backgroundColor: '#fafafa',
    color: '#333',
    minHeight: 100,
    textAlignVertical: 'top',
  },
  resultCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginTop: 16,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  resultTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 16,
    letterSpacing: -0.3,
  },
  bristolBadge: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    alignSelf: 'flex-start',
    marginBottom: 12,
  },
  bristolText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 13,
    letterSpacing: 0.3,
  },
  bristolBadgeLarge: {
    paddingHorizontal: 24,
    paddingVertical: 16,
    borderRadius: 24,
    alignSelf: 'center',
    marginTop: 12,
  },
  bristolTextLarge: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 24,
  },
  recomendacoesContainer: {
    marginTop: 12,
    padding: 16,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
  },
  recomendacoesTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  recomendacaoItem: {
    fontSize: 14,
    color: '#555',
    marginBottom: 6,
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    fontSize: 15,
    marginTop: 40,
    fontStyle: 'italic',
  },
  analiseCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
  },
  analiseDate: {
    fontSize: 13,
    color: '#999',
    marginTop: 8,
    marginBottom: 4,
  },
  observacoes: {
    fontSize: 14,
    color: '#555',
    fontStyle: 'italic',
    marginTop: 8,
    lineHeight: 20,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 18,
    borderRadius: 12,
    alignItems: 'center',
    marginHorizontal: 6,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    shadowColor: '#2ca02c',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 2,
  },
  statCardWide: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    shadowColor: '#2ca02c',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 2,
  },
  statValue: {
    fontSize: 36,
    fontWeight: '700',
    color: '#2ca02c',
    marginBottom: 6,
    letterSpacing: -1,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    fontWeight: '500',
  },
  chartContainer: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  chartTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 18,
    letterSpacing: -0.2,
  },
  chartRow: {
    marginBottom: 14,
  },
  chartLabelContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  chartColorBox: {
    width: 18,
    height: 18,
    borderRadius: 4,
    marginRight: 10,
  },
  chartLabel: {
    fontSize: 14,
    color: '#555',
    fontWeight: '600',
  },
  chartBarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    height: 26,
  },
  chartBar: {
    height: 26,
    borderRadius: 6,
    marginRight: 10,
    minWidth: 2,
  },
  chartValue: {
    fontSize: 13,
    color: '#666',
    fontWeight: '600',
  },
  timelineChartContainer: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  timelineSubtitle: {
    fontSize: 13,
    color: '#999',
    marginBottom: 16,
    fontStyle: 'italic',
  },
  timelineChart: {
    flexDirection: 'row',
    height: 200,
    marginBottom: 16,
  },
  yAxis: {
    width: 30,
    justifyContent: 'space-between',
    paddingRight: 8,
  },
  yAxisLabel: {
    height: 28,
    justifyContent: 'center',
    alignItems: 'flex-end',
  },
  yAxisText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '600',
  },
  chartArea: {
    flex: 1,
    position: 'relative',
  },
  gridLine: {
    position: 'absolute',
    width: '100%',
    height: 1,
    backgroundColor: '#f0f0f0',
    top: '0%',
  },
  dataLayer: {
    position: 'absolute',
    width: '100%',
    height: '100%',
  },
  dataPoint: {
    position: 'absolute',
    width: 10,
    height: 10,
    borderRadius: 5,
    marginLeft: -5,
    marginTop: -5,
    borderWidth: 2,
    borderColor: '#fff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 3,
    elevation: 3,
  },
  connectingLine: {
    position: 'absolute',
    height: 2,
    backgroundColor: '#2ca02c',
    transformOrigin: 'left center',
  },
  xAxis: {
    position: 'absolute',
    bottom: -25,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  xAxisLabel: {
    fontSize: 11,
    color: '#999',
    fontWeight: '500',
  },
  timelineLegend: {
    marginTop: 20,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  legendTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#666',
    marginBottom: 10,
  },
  legendItems: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 8,
  },
  legendDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 6,
    borderWidth: 1,
    borderColor: '#fff',
  },
  legendText: {
    fontSize: 12,
    color: '#666',
  },
  // Frequency chart styles
  frequencyChart: {
    flexDirection: 'row',
    height: 220,
    marginBottom: 16,
  },
  yAxisFreq: {
    width: 30,
    justifyContent: 'space-between',
    paddingRight: 8,
  },
  yAxisFreqLabel: {
    height: 28,
    justifyContent: 'center',
    alignItems: 'flex-end',
  },
  yAxisFreqText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '600',
  },
  barsContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'space-around',
    paddingHorizontal: 4,
  },
  barColumn: {
    flex: 1,
    alignItems: 'center',
    marginHorizontal: 2,
  },
  barWrapper: {
    width: '100%',
    height: 180,
    justifyContent: 'flex-end',
    alignItems: 'center',
  },
  bar: {
    width: '80%',
    minHeight: 20,
    borderRadius: 4,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  barLabel: {
    color: '#fff',
    fontSize: 11,
    fontWeight: 'bold',
  },
  dateLabel: {
    fontSize: 10,
    color: '#999',
    marginTop: 4,
    textAlign: 'center',
  },
});
