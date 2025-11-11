# Classificador de Fezes - Escala de Bristol

Modelo de classificação de fezes humanas em vasos sanitários de acordo com a Escala de Bristol para mensurar o nível de constipação do paciente.

## 🏆 Modelo em Produção

**Arquivo:** `best_model_fe.h5`
**Acurácia:** 68.72%
**Dataset:** 211 imagens

### Como Usar

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Fazer predição em uma imagem
python predict.py dataset/sua_imagem.jpg
```

## 📊 Dataset

### V1 - Dataset Original (211 imagens) ✅ RECOMENDADO

Distribuição por tipo de Bristol:
- Tipo 1: 31 imagens (14.7%)
- Tipo 2: 12 imagens (5.7%)
- Tipo 3: 27 imagens (12.8%)
- Tipo 4: 43 imagens (20.4%)
- Tipo 5: 35 imagens (16.6%)
- Tipo 6: 37 imagens (17.5%)
- Tipo 7: 26 imagens (12.3%)

**Split de treinamento:**
- 64% das imagens para treinamento efetivo
- 16% para validação durante o treino (early stopping, etc)
- 20% para teste final (nunca visto pelo modelo)

## 📈 Comparação de Modelos

Após extensiva análise com diferentes datasets:

| Modelo | Dataset | Acurácia | Status |
|--------|---------|----------|--------|
| **Feature Extraction V1** | **211 imgs** | **68.72%** | ✅ **PRODUÇÃO** |
| Feature Extraction V1 Augmented | 301 imgs | 64.93% | ✅ |
| Feature Extraction V2 | 360 imgs | 37.22% | ❌ Desbalanceado |
| Fine-Tuning V2 | 360 imgs | 20.00% | ❌ Desbalanceado |

**Conclusão:** Dataset V2 (360 imagens) falhou devido a desbalanceamento extremo (93% das novas imagens eram Tipos 3 e 4).

## 📁 Arquivos Principais

### Modelos
- `best_model_fe.h5` - **Modelo de produção** (68.72%)
- `best_model_fe_AUGMENTED.h5` - Modelo com augmentation (64.93%)
- `models_backup_v1/` - Backup dos modelos V1

### Datasets
- `labels.csv` - **Dataset principal** (211 imagens)
- `dataset/` - Diretório com as imagens

### Scripts
- `predict.py` - Script de predição para usar o modelo
- `train_model.ipynb` - Notebook de treinamento original
- `retrain_all_models.py` - Script de retreinamento

### Documentação
- `FINAL_ANALYSIS.md` - Análise completa e decisões técnicas
- `fair_evaluation_results.txt` - Resultados das avaliações

## 🔍 Escala de Bristol

- **Tipo 1:** Pedaços duros separados (constipação severa)
- **Tipo 2:** Forma de salsicha, mas irregular
- **Tipo 3:** Forma de salsicha com rachaduras
- **Tipo 4:** Forma de salsicha ou cobra, lisa e macia (IDEAL)
- **Tipo 5:** Pedaços macios com bordas bem definidas
- **Tipo 6:** Pedaços fofos com bordas irregulares
- **Tipo 7:** Aquoso, sem pedaços sólidos (diarreia)

## 📝 Notas Técnicas

- Para fezes que se enquadram em dois tipos de classificação, escolhemos o tipo na escala de Bristol de menor número
- Modelo baseado em VGG16 com transfer learning (Feature Extraction)
- Preprocessamento: normalização 0-1, resize para 224x224
- Data augmentation: rotação, shift, zoom, brightness, flip horizontal

