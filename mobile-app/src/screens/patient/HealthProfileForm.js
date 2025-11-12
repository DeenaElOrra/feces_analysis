import React from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
} from 'react-native';

export default function HealthProfileForm({ formData, setFormData, onSave, saving }) {
  const updateField = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const renderCheckbox = (label, field) => (
    <TouchableOpacity
      style={styles.checkboxRow}
      onPress={() => updateField(field, !formData[field])}
    >
      <View style={[styles.checkbox, formData[field] && styles.checkboxChecked]}>
        {formData[field] && <Text style={styles.checkmark}>✓</Text>}
      </View>
      <Text style={styles.checkboxLabel}>{label}</Text>
    </TouchableOpacity>
  );

  const renderRatingButtons = (label, field, maxRating = 5) => (
    <View style={styles.ratingContainer}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <View style={styles.ratingButtons}>
        {[1, 2, 3, 4, 5].slice(0, maxRating).map((value) => (
          <TouchableOpacity
            key={value}
            style={[
              styles.ratingButton,
              formData[field] === value && styles.ratingButtonSelected,
            ]}
            onPress={() => updateField(field, value)}
          >
            <Text
              style={[
                styles.ratingButtonText,
                formData[field] === value && styles.ratingButtonTextSelected,
              ]}
            >
              {value}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Section 1: Histórico Intestinal */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Histórico Intestinal</Text>

        <Text style={styles.fieldLabel}>Padrão Intestinal</Text>
        <View style={styles.optionsRow}>
          {['Constipado', 'Normal', 'Diarreico', 'Oscilante'].map((option) => (
            <TouchableOpacity
              key={option}
              style={[
                styles.optionButton,
                formData.padrao_intestinal === option && styles.optionButtonSelected,
              ]}
              onPress={() => updateField('padrao_intestinal', option)}
            >
              <Text
                style={[
                  styles.optionButtonText,
                  formData.padrao_intestinal === option && styles.optionButtonTextSelected,
                ]}
              >
                {option}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.fieldLabel}>Sintomas Intestinais</Text>
        <TextInput
          style={styles.multilineInput}
          placeholder="Ex: dor abdominal, gases, distensão..."
          value={formData.sintomas_intestinais}
          onChangeText={(value) => updateField('sintomas_intestinais', value)}
          multiline
          numberOfLines={3}
        />
      </View>

      {/* Section 2: Condições de Saúde */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Condições de Saúde</Text>

        <Text style={styles.fieldLabel}>Diagnósticos</Text>
        <TextInput
          style={styles.multilineInput}
          placeholder="Ex: SII, DII, diabetes..."
          value={formData.diagnosticos}
          onChangeText={(value) => updateField('diagnosticos', value)}
          multiline
          numberOfLines={3}
        />

        {renderCheckbox('Já fez cirurgias abdominais?', 'cirurgias_abdominais')}

        {formData.cirurgias_abdominais && (
          <>
            <Text style={styles.fieldLabel}>Descrição das Cirurgias</Text>
            <TextInput
              style={styles.multilineInput}
              placeholder="Descreva as cirurgias realizadas"
              value={formData.descricao_cirurgias}
              onChangeText={(value) => updateField('descricao_cirurgias', value)}
              multiline
              numberOfLines={3}
            />
          </>
        )}
      </View>

      {/* Section 3: Medicamentos e Suplementos */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Medicamentos e Suplementos</Text>

        {renderCheckbox('Uso recente de antibióticos?', 'uso_antibioticos_recente')}
        {renderCheckbox('Uso de laxantes?', 'uso_laxantes')}
        {renderCheckbox('Uso de antidiarreicos?', 'uso_antidiarreicos')}
        {renderCheckbox('Uso de probióticos?', 'uso_probioticos')}

        <Text style={styles.fieldLabel}>Outros Medicamentos</Text>
        <TextInput
          style={styles.multilineInput}
          placeholder="Liste outros medicamentos em uso"
          value={formData.outros_medicamentos}
          onChangeText={(value) => updateField('outros_medicamentos', value)}
          multiline
          numberOfLines={3}
        />
      </View>

      {/* Section 4: Alergias e Intolerâncias */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Alergias e Intolerâncias</Text>

        <TextInput
          style={styles.multilineInput}
          placeholder="Ex: lactose, glúten, frutos do mar..."
          value={formData.alergias_intolerâncias}
          onChangeText={(value) => updateField('alergias_intolerâncias', value)}
          multiline
          numberOfLines={3}
        />
      </View>

      {/* Section 5: Estilo de Vida */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Estilo de Vida</Text>

        <Text style={styles.fieldLabel}>Tipo de Dieta</Text>
        <View style={styles.optionsRow}>
          {['Onívora', 'Vegetariana', 'Vegana', 'Outra'].map((option) => (
            <TouchableOpacity
              key={option}
              style={[
                styles.optionButton,
                formData.tipo_dieta === option && styles.optionButtonSelected,
              ]}
              onPress={() => updateField('tipo_dieta', option)}
            >
              <Text
                style={[
                  styles.optionButtonText,
                  formData.tipo_dieta === option && styles.optionButtonTextSelected,
                ]}
              >
                {option}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.fieldLabel}>Consumo de Água (litros/dia)</Text>
        <TextInput
          style={styles.input}
          placeholder="Ex: 2.5"
          value={formData.consumo_agua}
          onChangeText={(value) => updateField('consumo_agua', value)}
          keyboardType="decimal-pad"
        />

        <Text style={styles.fieldLabel}>Frequência de Atividade Física</Text>
        <View style={styles.optionsRow}>
          {['Sedentário', 'Leve', 'Moderado', 'Intenso'].map((option) => (
            <TouchableOpacity
              key={option}
              style={[
                styles.optionButton,
                formData.frequencia_atividade === option && styles.optionButtonSelected,
              ]}
              onPress={() => updateField('frequencia_atividade', option)}
            >
              <Text
                style={[
                  styles.optionButtonText,
                  formData.frequencia_atividade === option && styles.optionButtonTextSelected,
                ]}
              >
                {option}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {renderRatingButtons('Nível de Estresse (1-5)', 'nivel_estresse')}
        {renderRatingButtons('Qualidade do Sono (1-5)', 'qualidade_sono')}
      </View>

      {/* Section 6: Histórico Familiar */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Histórico Familiar</Text>

        {renderCheckbox('Doenças intestinais na família?', 'doencas_intestinais_familia')}

        {formData.doencas_intestinais_familia && (
          <>
            <Text style={styles.fieldLabel}>Descrição do Histórico Familiar</Text>
            <TextInput
              style={styles.multilineInput}
              placeholder="Descreva as doenças intestinais na família"
              value={formData.descricao_hist_familiar}
              onChangeText={(value) => updateField('descricao_hist_familiar', value)}
              multiline
              numberOfLines={3}
            />
          </>
        )}
      </View>

      {/* Section 7: Observações Gerais */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Observações Gerais</Text>

        <TextInput
          style={styles.multilineInput}
          placeholder="Outras informações relevantes..."
          value={formData.observacoes_gerais}
          onChangeText={(value) => updateField('observacoes_gerais', value)}
          multiline
          numberOfLines={4}
        />
      </View>

      {/* Save Button */}
      <TouchableOpacity
        style={[styles.saveButton, saving && styles.saveButtonDisabled]}
        onPress={onSave}
        disabled={saving}
      >
        <Text style={styles.saveButtonText}>
          {saving ? 'Salvando...' : 'Salvar Perfil de Saúde'}
        </Text>
      </TouchableOpacity>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  section: {
    marginBottom: 28,
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 16,
    letterSpacing: -0.3,
  },
  fieldLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#555',
    marginBottom: 8,
    marginTop: 12,
  },
  input: {
    borderWidth: 1.5,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 15,
    backgroundColor: '#fafafa',
    color: '#333',
  },
  multilineInput: {
    borderWidth: 1.5,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 15,
    backgroundColor: '#fafafa',
    color: '#333',
    minHeight: 80,
    textAlignVertical: 'top',
  },
  checkboxRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 8,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#d0d0d0',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  checkboxChecked: {
    backgroundColor: '#2ca02c',
    borderColor: '#2ca02c',
  },
  checkmark: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  checkboxLabel: {
    fontSize: 15,
    color: '#555',
    flex: 1,
  },
  optionsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginTop: 8,
  },
  optionButton: {
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 8,
    borderWidth: 1.5,
    borderColor: '#d0d0d0',
    backgroundColor: '#fafafa',
  },
  optionButtonSelected: {
    backgroundColor: '#2ca02c',
    borderColor: '#2ca02c',
  },
  optionButtonText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  optionButtonTextSelected: {
    color: '#fff',
    fontWeight: '600',
  },
  ratingContainer: {
    marginTop: 12,
  },
  ratingButtons: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 8,
  },
  ratingButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 1.5,
    borderColor: '#d0d0d0',
    backgroundColor: '#fafafa',
    alignItems: 'center',
    justifyContent: 'center',
  },
  ratingButtonSelected: {
    backgroundColor: '#2ca02c',
    borderColor: '#2ca02c',
  },
  ratingButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
  },
  ratingButtonTextSelected: {
    color: '#fff',
  },
  saveButton: {
    backgroundColor: '#2ca02c',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 20,
    shadowColor: '#2ca02c',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 17,
    fontWeight: '600',
    letterSpacing: 0.5,
  },
});
