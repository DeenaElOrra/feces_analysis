# Setup do Projeto - Classificador de Fezes (Escala de Bristol)

## Pré-requisitos

- Python 3.8 ou superior (você tem Python 3.13.1 ✓)
- pip instalado

## Instruções de Setup

### 1. Criar ambiente virtual

```bash
# Criar venv
python3 -m venv venv

# Ativar venv (macOS/Linux)
source venv/bin/activate

# Ativar venv (Windows)
# venv\Scripts\activate
```

Quando ativado, você verá `(venv)` no início da linha do terminal.

### 2. Instalar dependências

```bash
# Com venv ativado
pip install --upgrade pip
pip install -r requirements.txt
```

Isso vai instalar:
- TensorFlow (para deep learning)
- Pandas, NumPy (manipulação de dados)
- Matplotlib, Seaborn (visualização)
- Scikit-learn (métricas ML)
- Jupyter (notebooks)
- Pillow (processamento de imagens)

### 3. Verificar instalação

```bash
python -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)"
python -c "import pandas as pd; print('Pandas:', pd.__version__)"
```

### 4. Rodar o notebook

```bash
# Iniciar Jupyter
jupyter notebook

# Ou usar Jupyter Lab (interface mais moderna)
jupyter lab
```

O navegador vai abrir automaticamente. Clique em `train_model.ipynb` para começar.

## Estrutura do Projeto

```
feces_analysis/
├── venv/                          # Ambiente virtual (será criado)
├── dataset/                       # Imagens classificadas
│   ├── *.jpg
│   └── *.png
├── labels.csv                     # Labels das imagens
├── train_model.ipynb             # Notebook principal de treinamento
├── requirements.txt              # Dependências Python
├── SETUP.md                      # Este arquivo
└── README.md                     # Descrição do projeto
```

## Modelos que serão gerados

Após o treinamento, você terá:

```
├── best_model_fe.h5              # Melhor modelo (Feature Extraction)
├── best_model_ft.h5              # Melhor modelo (Fine-Tuning)
├── bristol_classifier_final.h5   # Modelo final escolhido
└── bristol_classifier_final/     # Modelo final (formato TensorFlow)
```

## Troubleshooting

### Erro: "No module named 'tensorflow'"
```bash
# Certifique-se que o venv está ativado
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "Could not install packages due to OSError"
```bash
# Tente com --user
pip install --user -r requirements.txt
```

### Erro de memória durante treinamento
```python
# No notebook, reduza o BATCH_SIZE
BATCH_SIZE = 8  # ao invés de 16
```

### TensorFlow não detecta GPU (macOS com Apple Silicon)
```bash
# Instalar TensorFlow Metal plugin (para M1/M2/M3)
pip install tensorflow-metal
```

## Próximos Passos

1. Ativar venv: `source venv/bin/activate`
2. Instalar dependências: `pip install -r requirements.txt`
3. Abrir Jupyter: `jupyter notebook`
4. Executar: `train_model.ipynb`

## Desativar venv

Quando terminar de trabalhar:

```bash
deactivate
```

## Recursos Adicionais

- [Documentação TensorFlow](https://www.tensorflow.org/tutorials)
- [Guia de Transfer Learning](https://www.tensorflow.org/tutorials/images/transfer_learning)
- [VGG16 Paper](https://arxiv.org/abs/1409.1556)
