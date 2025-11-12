# Setup - Classificador de Fezes

## Requisitos

- Python 3.11+
- AWS Account (para deploy)
- Git

## Instalação Local

### 1. Clonar repositório

```bash
git clone <seu-repo>
cd feces_analysis
```

### 2. Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Download do modelo

O modelo treinado (`best_model_fe.h5`) não está no Git (arquivo grande).

**Opções:**
1. Baixar do Google Drive/Dropbox compartilhado
2. Treinar localmente com `train_model.ipynb`

Colocar o arquivo `best_model_fe.h5` na raiz do projeto.

## Uso Local

### Streamlit Web App

```bash
streamlit run app.py
```

Acesse: http://localhost:8501

### Script de Predição

```bash
# Modo interativo
python predict_fast.py

# Arquivo específico
python predict_fast.py "caminho/para/imagem.jpg"
```

## Deploy AWS EC2

Veja: [EC2_DEPLOY_GUIDE.md](EC2_DEPLOY_GUIDE.md)

```bash
# Passo a passo completo no guia
chmod +x deploy_ec2.sh
./deploy_ec2.sh
```

## Estrutura do Projeto

```
feces_analysis/
├── app.py                    # Web app Streamlit
├── predict_fast.py           # Script de predição
├── best_model_fe.h5          # Modelo treinado (não no Git)
├── labels.csv                # Dataset labels
├── dataset/                  # Imagens de treino
├── requirements.txt          # Dependências
├── train_model.ipynb         # Notebook de treino
├── deploy_ec2.sh            # Deploy automático EC2
├── EC2_DEPLOY_GUIDE.md      # Guia de deploy
└── SETUP.md                 # Este arquivo
```

## Problemas Comuns

### Erro: "No module named tensorflow"

```bash
pip install tensorflow>=2.15.0
```

### Erro: "best_model_fe.h5 not found"

O modelo não está no Git. Baixe ou treine.

### Erro: Streamlit não inicia

```bash
pip install --upgrade streamlit
```

## Desenvolvimento

### Retreinar modelo

```bash
jupyter notebook train_model.ipynb
```

### Adicionar novas imagens

1. Colocar imagens em `dataset/`
2. Atualizar `labels.csv`
3. Retreinar modelo

## Suporte

Problemas? Abra uma issue no GitHub.
