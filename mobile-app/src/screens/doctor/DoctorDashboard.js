import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  FlatList,
  Clipboard,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import api from '../../services/api';

const screenWidth = Dimensions.get('window').width;

export default function DoctorDashboard({ navigation }) {
  const [loading, setLoading] = useState(true);
  const [perfil, setPerfil] = useState(null);
  const [pacientes, setPacientes] = useState([]);
  const [selectedPaciente, setSelectedPaciente] = useState(null);
  const [analises, setAnalises] = useState([]);
  const [perfilSaude, setPerfilSaude] = useState(null);
  const [loadingPerfilSaude, setLoadingPerfilSaude] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      console.log('DoctorDashboard: Carregando dados...');
      const [perfilData, pacientesData] = await Promise.all([
        api.getMedicoPerfil(),
        api.getMedicoPacientes(),
      ]);
      console.log('DoctorDashboard: Perfil recebido:', perfilData);
      console.log('DoctorDashboard: Pacientes recebidos:', pacientesData);

      setPerfil(perfilData);
      setPacientes(Array.isArray(pacientesData) ? pacientesData : []);
    } catch (error) {
      console.error('DoctorDashboard: Erro ao carregar dados:', error);
      console.error('DoctorDashboard: Detalhes do erro:', error.response?.data || error.message);
      Alert.alert(
        'Erro ao carregar dados',
        error.response?.data?.detail || error.message || 'Erro desconhecido'
      );
      // Set default values to avoid crashes
      setPerfil({ nome: 'Médico', codigo_convite: '...' });
      setPacientes([]);
    } finally {
      setLoading(false);
    }
  };

  const loadPacienteAnalises = async (paciente) => {
    console.log('DoctorDashboard: Carregando análises do paciente:', paciente);
    setSelectedPaciente(paciente);
    setLoadingPerfilSaude(true);
    try {
      const data = await api.getMedicoPacienteAnalises(paciente.id);
      console.log('DoctorDashboard: Análises recebidas:', data);
      setAnalises(Array.isArray(data) ? data : []);

      // Carregar perfil de saúde do paciente
      try {
        const perfilSaudeData = await api.getPerfilSaudePaciente(paciente.id);
        console.log('DoctorDashboard: Perfil de saúde recebido:', perfilSaudeData);
        setPerfilSaude(perfilSaudeData);
      } catch (perfilError) {
        console.log('DoctorDashboard: Paciente não possui perfil de saúde');
        setPerfilSaude(null);
      }
    } catch (error) {
      console.error('DoctorDashboard: Erro ao carregar análises:', error);
      console.error('DoctorDashboard: Detalhes:', error.response?.data || error.message);
      Alert.alert(
        'Erro ao carregar análises',
        error.response?.data?.detail || error.message || 'Erro desconhecido'
      );
      setAnalises([]);
      setPerfilSaude(null);
    } finally {
      setLoadingPerfilSaude(false);
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

  const handleCopyCode = () => {
    if (perfil?.codigo_convite) {
      Clipboard.setString(perfil.codigo_convite);
      Alert.alert('Copiado!', 'Código copiado para a área de transferência');
    }
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

  const calculateStats = () => {
    if (analises.length === 0) return null;

    const counts = {};
    analises.forEach((a) => {
      counts[a.tipo_bristol] = (counts[a.tipo_bristol] || 0) + 1;
    });

    const mostFrequent = Object.entries(counts).reduce((a, b) =>
      counts[a[0]] > counts[b[0]] ? a : b
    )[0];

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

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#1f77b4" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <Text style={styles.headerTitle}>Dashboard Médico</Text>
          <Text style={styles.headerSubtitle}>Dr(a). {perfil?.nome}</Text>
        </View>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>Sair</Text>
        </TouchableOpacity>
      </View>

      {/* Info Card - Only show when not viewing a patient */}
      {!selectedPaciente && (
        <View style={styles.infoCard}>
          <View style={styles.infoHeader}>
            <Text style={styles.infoLabel}>Código de Convite</Text>
          </View>
          <View style={styles.codeContainer}>
            <Text style={styles.infoValue}>{perfil?.codigo_convite}</Text>
            <TouchableOpacity style={styles.copyButton} onPress={handleCopyCode}>
              <Text style={styles.copyButtonText}>Copiar</Text>
            </TouchableOpacity>
          </View>
          <Text style={styles.infoHint}>
            Compartilhe este código com seus pacientes
          </Text>
        </View>
      )}

      {/* Patients List or Patient Details */}
      {!selectedPaciente ? (
        <View style={styles.content}>
          <Text style={styles.sectionTitle}>
            Meus Pacientes ({pacientes.length})
          </Text>
          <FlatList
            data={pacientes}
            keyExtractor={(item) => String(item.id)}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={styles.pacienteCard}
                onPress={() => loadPacienteAnalises(item)}
              >
                <Text style={styles.pacienteName}>{item.nome}</Text>
                <Text style={styles.pacienteEmail}>{item.email}</Text>
                <Text style={styles.viewButton}>Ver análises</Text>
              </TouchableOpacity>
            )}
            ListEmptyComponent={
              <Text style={styles.emptyText}>
                Nenhum paciente cadastrado ainda.
              </Text>
            }
          />
        </View>
      ) : (
        <View style={styles.content}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => setSelectedPaciente(null)}
          >
            <Text style={styles.backButtonText}>Voltar</Text>
          </TouchableOpacity>

          <Text style={styles.sectionTitle}>
            Análises de {selectedPaciente.nome}
          </Text>

          <ScrollView showsVerticalScrollIndicator={false}>
            {analises.length === 0 ? (
              <Text style={styles.emptyText}>
                Este paciente ainda não fez análises.
              </Text>
            ) : (
              <>
                {/* Statistics Cards */}
                {(() => {
                  const stats = calculateStats();
                  return stats ? (
                    <View style={styles.statsCards}>
                      <View style={styles.statCard}>
                        <Text style={styles.statNumber}>{stats.total}</Text>
                        <Text style={styles.statLabel}>Total de Análises</Text>
                      </View>
                      <View style={styles.statCard}>
                        <Text style={styles.statNumber}>
                          {stats.last7DaysCount}
                        </Text>
                        <Text style={styles.statLabel}>Últimos 7 dias</Text>
                      </View>
                      <View style={[styles.statCard, { flex: 1.2 }]}>
                        <View
                          style={[
                            styles.bristolBadge,
                            {
                              backgroundColor: getBristolColor(
                                stats.mostFrequent
                              ),
                            },
                          ]}
                        >
                          <Text style={styles.bristolText}>
                            Tipo {stats.mostFrequent}
                          </Text>
                        </View>
                        <Text style={styles.statLabel}>Mais Frequente</Text>
                      </View>
                    </View>
                  ) : null;
                })()}

                {/* Chart */}
                {renderChart()}

                {/* Health Profile Section */}
                {loadingPerfilSaude ? (
                  <View style={styles.perfilSaudeContainer}>
                    <Text style={styles.perfilSaudeTitle}>Perfil de Saúde do Paciente</Text>
                    <ActivityIndicator size="small" color="#1f77b4" style={{ marginTop: 10 }} />
                  </View>
                ) : perfilSaude ? (
                  <View style={styles.perfilSaudeContainer}>
                    <Text style={styles.perfilSaudeTitle}>Perfil de Saúde do Paciente</Text>

                    {/* Histórico Intestinal */}
                    <View style={styles.perfilSection}>
                      <Text style={styles.perfilSectionTitle}>Histórico Intestinal</Text>
                      {perfilSaude.padrao_intestinal && (
                        <View style={styles.perfilRow}>
                          <Text style={styles.perfilLabel}>Padrão Intestinal:</Text>
                          <Text style={styles.perfilValue}>{perfilSaude.padrao_intestinal}</Text>
                        </View>
                      )}
                      {perfilSaude.sintomas_intestinais && (
                        <View style={styles.perfilRow}>
                          <Text style={styles.perfilLabel}>Sintomas:</Text>
                          <Text style={styles.perfilValue}>{perfilSaude.sintomas_intestinais}</Text>
                        </View>
                      )}
                    </View>

                    {/* Condições de Saúde */}
                    <View style={styles.perfilSection}>
                      <Text style={styles.perfilSectionTitle}>Condições de Saúde</Text>
                      {perfilSaude.diagnosticos && (
                        <View style={styles.perfilRow}>
                          <Text style={styles.perfilLabel}>Diagnósticos:</Text>
                          <Text style={styles.perfilValue}>{perfilSaude.diagnosticos}</Text>
                        </View>
                      )}
                      {perfilSaude.cirurgias_abdominais && (
                        <View style={styles.perfilRow}>
                          <Text style={styles.perfilLabel}>Cirurgias Abdominais:</Text>
                          <Text style={styles.perfilValue}>Sim</Text>
                        </View>
                      )}
                      {perfilSaude.descricao_cirurgias && (
                        <View style={styles.perfilRow}>
                          <Text style={styles.perfilLabel}>Descrição:</Text>
                          <Text style={styles.perfilValue}>{perfilSaude.descricao_cirurgias}</Text>
                        </View>
                      )}
                    </View>

                    {/* Medicamentos e Suplementos */}
                    <View style={styles.perfilSection}>
                      <Text style={styles.perfilSectionTitle}>Medicamentos e Suplementos</Text>
                      {perfilSaude.uso_antibioticos_recente && (
                        <Text style={styles.perfilCheckItem}>✓ Uso recente de antibióticos</Text>
                      )}
                      {perfilSaude.uso_laxantes && (
                        <Text style={styles.perfilCheckItem}>✓ Uso de laxantes</Text>
                      )}
                      {perfilSaude.uso_antidiarreicos && (
                        <Text style={styles.perfilCheckItem}>✓ Uso de antidiarreicos</Text>
                      )}
                      {perfilSaude.uso_probioticos && (
                        <Text style={styles.perfilCheckItem}>✓ Uso de probióticos</Text>
                      )}
                      {perfilSaude.outros_medicamentos && (
                        <View style={styles.perfilRow}>
                          <Text style={styles.perfilLabel}>Outros medicamentos:</Text>
                          <Text style={styles.perfilValue}>{perfilSaude.outros_medicamentos}</Text>
                        </View>
                      )}
                    </View>

                    {/* Alergias e Intolerâncias */}
                    {perfilSaude.alergias_intolerâncias && (
                      <View style={styles.perfilSection}>
                        <Text style={styles.perfilSectionTitle}>Alergias e Intolerâncias</Text>
                        <Text style={styles.perfilValue}>{perfilSaude.alergias_intolerâncias}</Text>
                      </View>
                    )}

                    {/* Estilo de Vida */}
                    <View style={styles.perfilSection}>
                      <Text style={styles.perfilSectionTitle}>Estilo de Vida</Text>
                      {perfilSaude.tipo_dieta && (
                        <View style={styles.perfilRow}>
                          <Text style={styles.perfilLabel}>Tipo de Dieta:</Text>
                          <Text style={styles.perfilValue}>{perfilSaude.tipo_dieta}</Text>
                        </View>
                      )}
                      {perfilSaude.consumo_agua && (
                        <View style={styles.perfilRow}>
                          <Text style={styles.perfilLabel}>Consumo de Água:</Text>
                          <Text style={styles.perfilValue}>{perfilSaude.consumo_agua} L/dia</Text>
                        </View>
                      )}
                      {perfilSaude.frequencia_atividade && (
                        <View style={styles.perfilRow}>
                          <Text style={styles.perfilLabel}>Atividade Física:</Text>
                          <Text style={styles.perfilValue}>{perfilSaude.frequencia_atividade}</Text>
                        </View>
                      )}
                      {perfilSaude.nivel_estresse && (
                        <View style={styles.perfilRow}>
                          <Text style={styles.perfilLabel}>Nível de Estresse:</Text>
                          <Text style={styles.perfilValue}>{perfilSaude.nivel_estresse}/5</Text>
                        </View>
                      )}
                      {perfilSaude.qualidade_sono && (
                        <View style={styles.perfilRow}>
                          <Text style={styles.perfilLabel}>Qualidade do Sono:</Text>
                          <Text style={styles.perfilValue}>{perfilSaude.qualidade_sono}/5</Text>
                        </View>
                      )}
                    </View>

                    {/* Histórico Familiar */}
                    {perfilSaude.doencas_intestinais_familia && (
                      <View style={styles.perfilSection}>
                        <Text style={styles.perfilSectionTitle}>Histórico Familiar</Text>
                        <Text style={styles.perfilCheckItem}>✓ Doenças intestinais na família</Text>
                        {perfilSaude.descricao_hist_familiar && (
                          <Text style={styles.perfilValue}>{perfilSaude.descricao_hist_familiar}</Text>
                        )}
                      </View>
                    )}

                    {/* Observações Gerais */}
                    {perfilSaude.observacoes_gerais && (
                      <View style={styles.perfilSection}>
                        <Text style={styles.perfilSectionTitle}>Observações Gerais</Text>
                        <Text style={styles.perfilValue}>{perfilSaude.observacoes_gerais}</Text>
                      </View>
                    )}
                  </View>
                ) : null}

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

                {/* Timeline Header */}
                <Text style={styles.timelineTitle}>Histórico Detalhado</Text>

                {/* Grouped Analyses */}
                {(() => {
                  const grupos = groupAnalisesByPeriod();
                  return (
                    <>
                      {grupos.hoje.length > 0 && (
                        <>
                          <Text style={styles.periodHeader}>Hoje</Text>
                          {grupos.hoje.map((analise) => (
                            <View key={analise.id} style={styles.analiseCard}>
                              <View
                                style={[
                                  styles.bristolBadge,
                                  {
                                    backgroundColor: getBristolColor(
                                      analise.tipo_bristol
                                    ),
                                  },
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

                      {grupos.semana.length > 0 && (
                        <>
                          <Text style={styles.periodHeader}>Esta Semana</Text>
                          {grupos.semana.map((analise) => (
                            <View key={analise.id} style={styles.analiseCard}>
                              <View
                                style={[
                                  styles.bristolBadge,
                                  {
                                    backgroundColor: getBristolColor(
                                      analise.tipo_bristol
                                    ),
                                  },
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

                      {grupos.mes.length > 0 && (
                        <>
                          <Text style={styles.periodHeader}>Este Mês</Text>
                          {grupos.mes.map((analise) => (
                            <View key={analise.id} style={styles.analiseCard}>
                              <View
                                style={[
                                  styles.bristolBadge,
                                  {
                                    backgroundColor: getBristolColor(
                                      analise.tipo_bristol
                                    ),
                                  },
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

                      {grupos.antigo.length > 0 && (
                        <>
                          <Text style={styles.periodHeader}>Mais Antigo</Text>
                          {grupos.antigo.map((analise) => (
                            <View key={analise.id} style={styles.analiseCard}>
                              <View
                                style={[
                                  styles.bristolBadge,
                                  {
                                    backgroundColor: getBristolColor(
                                      analise.tipo_bristol
                                    ),
                                  },
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
                  );
                })()}
              </>
            )}
          </ScrollView>
        </View>
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
  infoCard: {
    backgroundColor: '#fff',
    padding: 20,
    margin: 16,
    marginBottom: 8,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    shadowColor: '#1f77b4',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  infoHeader: {
    marginBottom: 12,
  },
  infoLabel: {
    fontSize: 13,
    color: '#666',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  infoValue: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1f77b4',
    fontFamily: 'monospace',
    letterSpacing: 2,
  },
  infoHint: {
    fontSize: 13,
    color: '#999',
    marginTop: 12,
    fontStyle: 'italic',
  },
  codeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginVertical: 8,
  },
  copyButton: {
    backgroundColor: '#1f77b4',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 10,
    marginLeft: 12,
    shadowColor: '#1f77b4',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  copyButtonText: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '600',
    letterSpacing: 0.3,
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
  pacienteCard: {
    backgroundColor: '#fff',
    padding: 18,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
  },
  pacienteName: {
    fontSize: 17,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  pacienteEmail: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  viewButton: {
    fontSize: 14,
    color: '#1f77b4',
    fontWeight: '600',
    letterSpacing: 0.2,
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    fontSize: 15,
    marginTop: 40,
    fontStyle: 'italic',
  },
  backButton: {
    marginBottom: 16,
    alignSelf: 'flex-start',
  },
  backButtonText: {
    fontSize: 15,
    color: '#666',
    fontWeight: '500',
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
  analiseHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  bristolBadge: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    alignSelf: 'flex-start',
  },
  bristolText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 13,
    letterSpacing: 0.3,
  },
  confianca: {
    fontSize: 12,
    color: '#666',
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
  recomendacoesContainer: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
  },
  recomendacoesTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  recomendacaoItem: {
    fontSize: 13,
    color: '#555',
    marginBottom: 4,
  },
  statsCards: {
    flexDirection: 'row',
    marginBottom: 20,
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 18,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    shadowColor: '#1f77b4',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 2,
  },
  statNumber: {
    fontSize: 36,
    fontWeight: '700',
    color: '#1f77b4',
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
  timelineTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 16,
    marginTop: 12,
    letterSpacing: -0.3,
  },
  periodHeader: {
    fontSize: 13,
    fontWeight: '700',
    color: '#1f77b4',
    marginTop: 16,
    marginBottom: 10,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  perfilSaudeContainer: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    shadowColor: '#2ca02c',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 2,
  },
  perfilSaudeTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 16,
    letterSpacing: -0.3,
  },
  perfilSection: {
    marginBottom: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  perfilSectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#2ca02c',
    marginBottom: 12,
    letterSpacing: -0.2,
  },
  perfilRow: {
    marginBottom: 8,
  },
  perfilLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#666',
    marginBottom: 2,
  },
  perfilValue: {
    fontSize: 14,
    color: '#1a1a1a',
    lineHeight: 20,
  },
  perfilCheckItem: {
    fontSize: 14,
    color: '#2ca02c',
    marginBottom: 6,
    fontWeight: '500',
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
    backgroundColor: '#1f77b4',
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
