# Análise Final - Modelos Bristol Stool Scale

## Resumo Executivo

Após extensiva análise e testes com diferentes datasets, **o modelo V1 original continua sendo o melhor modelo** para classificação da Escala de Bristol.

## Modelos Disponíveis e Performance

### Ranking Final (Avaliação Justa - Dataset Completo)

| Posição | Modelo | Dataset | Acurácia | Arquivo |
|---------|--------|---------|----------|---------|
| **🥇 1º** | **Feature Extraction V1** | **211 imgs** | **68.72%** | `best_model_fe.h5` |
| 🥈 2º | Feature Extraction V1 Augmented | 301 imgs | 64.93% | `best_model_fe_AUGMENTED.h5` |
| 🥉 3º | Feature Extraction V2 | 360 imgs | 37.22% | `best_model_fe_V2.h5` |
| 4º | Fine-Tuning V2 | 360 imgs | 20.00% | `best_model_ft_V2.h5` |
| 5º | Feature Extraction V2 Balanced | 222 imgs | 20.00% | `best_model_fe_balanced.h5` |
| 6º | Fine-Tuning V2 Balanced | 222 imgs | 13.33% | `best_model_ft_balanced.h5` |

## Modelo Recomendado para Uso em Produção

### **🏆 best_model_fe.h5**

- **Acurácia:** 68.72%
- **Dataset:** 211 imagens originais
- **Arquitetura:** VGG16 Feature Extraction (base congelada)
- **Tamanho:** 61 MB
- **Distribuição do dataset:**
  - Tipo 1: 31 imagens (14.7%)
  - Tipo 2: 12 imagens (5.7%)
  - Tipo 3: 27 imagens (12.8%)
  - Tipo 4: 43 imagens (20.4%)
  - Tipo 5: 35 imagens (16.6%)
  - Tipo 6: 37 imagens (17.5%)
  - Tipo 7: 26 imagens (12.3%)

## Por que V2 (360 imagens) Falhou?

### Problema Principal: Dataset EXTREMAMENTE Desbalanceado

As 149 novas imagens tinham distribuição completamente enviesada:

- **Tipos 3 + 4:** 139 imagens (93.3%) ← Concentração crítica
- **Tipos 1, 6, 7:** 0 imagens
- **Resultado:** O modelo aprendeu a "chutar" sempre Tipo 4 (estatisticamente mais provável)

### Dataset V2 Desbalanceado (360 imagens):
- Tipo 1: 31 (8.6%)
- Tipo 2: 21 (5.8%)
- Tipo 3: 92 (25.6%) ← Muito!
- Tipo 4: 117 (32.5%) ← Muito!
- Tipo 5: 36 (10.0%)
- Tipo 6: 37 (10.3%)
- Tipo 7: 26 (7.2%)

**Coeficiente de Variação:** 67.28% (muito desbalanceado)

## Por que Balanceamento (222 imagens) Também Falhou?

### Problema: Dataset Muito Pequeno Após Undersampling

1. **Perda de dados crítica:**
   - Removemos 138 imagens (38% do dataset original V2)
   - Restaram apenas 222 imagens
   - Com split 80/20: apenas 177 treino, 45 teste

2. **Insuficiente para transfer learning:**
   - VGG16 precisa de dados suficientes mesmo com transfer learning
   - Tipos minoritários continuaram com poucos exemplos (Tipo 2: 21 imgs)
   - Modelo não conseguiu aprender padrões robustos

3. **Resultado:**
   - Feature Extraction: 20.00% (pior que chance aleatória)
   - Fine-Tuning: 13.33% (completamente falhou)

## Lições Aprendidas

### ✅ O que funcionou:
1. **Dataset original (211 imagens)** tem distribuição adequada
2. **Feature Extraction** (VGG16 congelado) funciona melhor que Fine-Tuning
3. **Avaliação justa** (dataset completo) é crucial para comparações

### ❌ O que NÃO funcionou:
1. Adicionar imagens desbalanceadas piora drasticamente
2. Undersampling excessivo remove informação crítica
3. Fine-Tuning com dataset pequeno causa overfitting severo

## Recomendações Futuras

### Para Melhorar o Modelo (além de 68.72%):

#### Opção 1: Coletar Dados Balanceados (RECOMENDADO)
- **Objetivo:** Ter 40-50 imagens de cada tipo (7 tipos)
- **Total desejado:** 300-350 imagens bem distribuídas
- **Foco:** Coletar prioritariamente dos tipos raros:
  - Tipo 1 (Constipação severa)
  - Tipo 2 (Constipação leve)
  - Tipo 7 (Diarreia líquida)

#### Opção 2: Técnicas Avançadas com Dataset Atual
- **Data Augmentation mais agressiva:**
  - Variações de cor/brilho
  - Rotações e flips
  - Zoom e crops
- **Class Weights ainda mais fortes**
- **Ensemble de modelos** (combinar previsões)
- **Focal Loss** (para lidar com desbalanço)

#### Opção 3: Modelos Alternativos
- Testar outras arquiteturas:
  - ResNet50
  - EfficientNet
  - MobileNetV2 (mais leve)

## Arquivos Importantes

### Modelos Salvos:
- `best_model_fe.h5` ← **USE ESTE**
- `best_model_fe_AUGMENTED.h5`
- `models_backup_v1/` (backup dos modelos V1)

### Datasets:
- `labels.csv` (211 imagens) ← **DATASET PRINCIPAL**
- `labels_backup_v1.csv` (backup)
- `labels_v2_desbalanceado.csv` (360 imgs - NÃO usar)
- `labels_v2_balanced.csv` (222 imgs - NÃO usar)

### Scripts de Treinamento:
- `train_model.ipynb` - Notebook original
- `retrain_all_models.py` - Script de retreinamento
- `retrain_balanced_models.py` - Teste com dataset balanceado

### Scripts de Análise:
- `investigate_dataset_problem.py` - Análise do desbalanço
- `reevaluate_all_models_fair.py` - Comparação justa
- `balance_dataset_v2.py` - Script de balanceamento

### Resultados:
- `fair_evaluation_results.txt` - Comparação final
- `balanced_training_results.txt` - Resultados balanceados

## Decisão Final

**Manter dataset original de 211 imagens e modelo `best_model_fe.h5`** como versão de produção.

### Justificativa:
1. ✅ Melhor performance comprovada (68.72%)
2. ✅ Dataset relativamente balanceado
3. ✅ Modelo estável e confiável
4. ✅ Tamanho adequado para deploy (61 MB)

### Próximos Passos:
1. Usar `best_model_fe.h5` para inferência
2. Coletar mais dados balanceados quando possível
3. Retreinar periodicamente com novos dados de qualidade

---

**Data da Análise:** 10 de Novembro de 2025
**Modelo Recomendado:** `best_model_fe.h5` (68.72% acurácia)
**Dataset Recomendado:** `labels.csv` (211 imagens)
