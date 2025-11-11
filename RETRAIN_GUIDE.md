# 🚀 Guia de Retreinamento - Dataset V2 (360 imagens)

## ✅ PREPARAÇÃO COMPLETA

Tudo está pronto para retreinar os modelos com o novo dataset de 360 imagens!

---

## 📋 O QUE SERÁ TREINADO

O script `retrain_all_models.py` vai treinar **2 modelos** sequencialmente:

### 1️⃣ **Feature Extraction** (VGG16 Congelado)
- **Arquivo de saída**: `best_model_fe_V2.h5`
- **Abordagem**: VGG16 pré-treinado congelado + camadas classificadoras
- **Parâmetros treináveis**: ~7.5M (apenas camadas Dense)
- **Tamanho**: ~61 MB
- **Tempo estimado**: 15-25 minutos
- **Acurácia esperada**: 78-82%

### 2️⃣ **Fine-Tuning** (VGG16 Treinável)
- **Arquivo de saída**: `best_model_ft_V2.h5`
- **Abordagem**: VGG16 com últimas 4 camadas treináveis
- **Parâmetros treináveis**: ~10M
- **Tamanho**: ~115 MB
- **Tempo estimado**: 25-40 minutos
- **Acurácia esperada**: 80-85%

---

## 🚀 COMO EXECUTAR

### Opção 1: Script Automático (RECOMENDADO)

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar treinamento completo
python retrain_all_models.py
```

**Tempo total**: ~40-65 minutos (dependendo da CPU)

O script vai:
1. ✅ Carregar dataset V2 (360 imagens)
2. ✅ Treinar Feature Extraction → `best_model_fe_V2.h5`
3. ✅ Treinar Fine-Tuning → `best_model_ft_V2.h5`
4. ✅ Comparar resultados
5. ✅ Salvar relatório em `training_results_V2.txt`

---

### Opção 2: Notebook Jupyter (Passo a Passo)

```bash
# Abrir notebook
jupyter notebook train_model.ipynb
```

Execute as células sequencialmente. O notebook vai automaticamente usar o `labels.csv` atualizado (360 imagens).

---

## 📊 CHECKPOINTS E CONFIGURAÇÕES

### Data Augmentation
```python
rotation_range=20          # Rotação até 20°
width_shift_range=0.2      # Deslocamento horizontal 20%
height_shift_range=0.2     # Deslocamento vertical 20%
zoom_range=0.2             # Zoom até 20%
horizontal_flip=True       # Espelhar horizontalmente
brightness_range=[0.8, 1.2] # Variação de brilho
```

### Early Stopping
- **Feature Extraction**: Patience 10 épocas
- **Fine-Tuning**: Patience 15 épocas (mais paciência)

### Learning Rate
- **Feature Extraction**: 0.001 (padrão)
- **Fine-Tuning**: 0.0001 (10x menor - mais cuidadoso)

### Class Weights
Balanceamento automático para lidar com classes desbalanceadas:
- Tipo 1: ~0.93
- Tipo 2: ~1.36 (mais peso - classe rara)
- Tipo 3: ~0.70
- Tipo 4: ~0.55
- Etc.

---

## 📁 ARQUIVOS CRIADOS

Após o treinamento:

```
feces_analysis/
├── best_model_fe_V2.h5          # ✨ NOVO - Feature Extraction V2
├── best_model_ft_V2.h5          # ✨ NOVO - Fine-Tuning V2
├── training_results_V2.txt      # ✨ NOVO - Relatório de resultados
├── models_backup_v1/            # ✅ Backup dos modelos V1
│   ├── best_model_fe.h5         # V1 - 68.72%
│   ├── best_model_fe_AUGMENTED.h5  # V1 Aug - 75.42%
│   └── best_model_ft.h5         # V1 FT
├── labels.csv                   # Dataset V2 - 360 imagens ✅
└── retrain_all_models.py        # Script de treinamento ✅
```

---

## 📈 COMPARAÇÃO ESPERADA

| Modelo | Dataset | Acurácia V1 | Acurácia V2 Esperada | Ganho |
|--------|---------|-------------|---------------------|-------|
| **Feature Extraction** | 211 → 360 | 68.72% | **78-82%** | +10-14% 🔥 |
| **Feature Extraction Aug** | 301 (211+90) | 75.42% | - | - |
| **Fine-Tuning** | 211 → 360 | ??? | **80-85%** | Novo! |

### Por que esperar melhoria?

1. **+70% mais dados**: 211 → 360 imagens REAIS
2. **Tipos 3 e 4 dominam**: +139 imagens nas classes confusas
3. **Tipo 2 melhor**: +75% mais dados (12 → 21)
4. **Melhor balanceamento**: Dataset mais equilibrado

---

## ⏱️ CRONOGRAMA

```
[00:00] Início do script
[00:01] Carregamento de dados (360 imagens)
[00:02] Criação dos geradores de dados
[00:03] Início Feature Extraction
[15:00-25:00] ✅ Feature Extraction completo
[25:01] Início Fine-Tuning
[50:00-65:00] ✅ Fine-Tuning completo
[65:01] Comparação e relatório
[65:02] ✅ TUDO PRONTO!
```

---

## 🔍 MONITORAMENTO

Durante o treinamento, você verá:

```
Epoch 1/50
 1/14 ━━━━━━━━━━━━━━━━━━━━ 25s 2s/step - accuracy: 0.62 - loss: 1.45
...
Epoch 15/50
14/14 ━━━━━━━━━━━━━━━━━━━━ 28s 2s/step - accuracy: 0.81 - loss: 0.65 - val_accuracy: 0.79 - val_loss: 0.71
```

**Métricas importantes**:
- `accuracy`: Acurácia no treino (deve subir)
- `val_accuracy`: Acurácia na validação (deve subir e se aproximar da treino)
- `loss`: Erro no treino (deve cair)
- `val_loss`: Erro na validação (deve cair)

**Sinais bons**:
- ✅ `val_accuracy` aumentando
- ✅ Gap pequeno entre `accuracy` e `val_accuracy` (<10%)
- ✅ `val_loss` diminuindo

**Sinais de overfitting**:
- ⚠️ `accuracy` muito maior que `val_accuracy` (>15%)
- ⚠️ `val_loss` aumentando enquanto `loss` diminui

---

## 📊 APÓS O TREINAMENTO

### 1. Ver Resultados

```bash
cat training_results_V2.txt
```

### 2. Comparar TODOS os Modelos

```bash
python compare_all_models.py
```

Vai comparar:
- V1: Feature Extraction (68.72%)
- V1: Feature Extraction Augmented (75.42%)
- V1: Fine-Tuning
- **V2: Feature Extraction** ← NOVO
- **V2: Fine-Tuning** ← NOVO

### 3. Escolher Melhor Modelo

O script mostrará qual modelo teve melhor desempenho.

---

## ✅ CHECKLIST

- [x] Backup dos modelos V1 criado (`models_backup_v1/`)
- [x] Dataset V2 com 360 imagens pronto (`labels.csv`)
- [x] Script de treinamento criado (`retrain_all_models.py`)
- [ ] ⏳ Executar treinamento
- [ ] ⏳ Avaliar resultados
- [ ] ⏳ Escolher melhor modelo

---

## 🚦 PRÓXIMOS PASSOS

### AGORA:
```bash
source venv/bin/activate
python retrain_all_models.py
```

### DEPOIS:
1. Verificar `training_results_V2.txt`
2. Comparar todos os modelos
3. Escolher o melhor para produção

---

## 💡 DICAS

1. **☕ Pausa**: O treinamento leva ~1 hora. Ótimo momento para um café!

2. **🔌 Energia**: Conecte o laptop na tomada (vai usar bastante CPU)

3. **📊 Monitore**: Acompanhe os valores de `val_accuracy` - devem chegar a 78-82%

4. **⚠️ Se travar**:
   - Ctrl+C para cancelar
   - Modelos parciais são salvos em `best_model_*_V2.h5`
   - Pode retomar do ponto de parada

5. **🎯 Meta**: Queremos ultrapassar 75.42% (melhor modelo atual)

---

## 📞 PRECISA DE AJUDA?

Se algo der errado:
1. Verifique os logs de erro
2. Confirme que o ambiente virtual está ativo
3. Verifique se `labels.csv` tem 360 linhas (`wc -l labels.csv`)

---

**🎉 BOA SORTE COM O TREINAMENTO!**

Expectativa: **78-82% de acurácia** com o novo dataset V2! 🚀
