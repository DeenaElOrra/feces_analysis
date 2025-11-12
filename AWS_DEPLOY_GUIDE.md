# Guia de Deploy na AWS - Classificador de Fezes

## 📋 Pré-requisitos

1. **Conta AWS** (Free Tier)
2. **AWS CLI instalado**
3. **Credenciais AWS configuradas**

---

## 🚀 Deploy Passo a Passo

### 1. Criar Conta AWS

1. Acesse: https://aws.amazon.com/
2. Clique em "Create an AWS Account"
3. Preencha seus dados
4. **Importante:** Precisa de cartão de crédito, mas não será cobrado no Free Tier

### 2. Criar Usuário IAM (para credenciais)

1. Acesse: https://console.aws.amazon.com/iam/
2. Vá em "Users" → "Add users"
3. Nome: `feces-classifier-deploy`
4. Marque: "Programmatic access"
5. Permissions: "Attach existing policies directly"
   - Marque: `AWSLambdaFullAccess`
   - Marque: `AmazonAPIGatewayAdministrator`
   - Marque: `IAMFullAccess`
6. Clique "Next" até "Create user"
7. **IMPORTANTE:** Copie:
   - Access Key ID
   - Secret Access Key

### 3. Instalar e Configurar AWS CLI

```bash
# Instalar
brew install awscli

# Verificar instalação
aws --version

# Configurar credenciais
aws configure
```

Vai pedir:
```
AWS Access Key ID: [cole aqui]
AWS Secret Access Key: [cole aqui]
Default region name: us-east-1
Default output format: json
```

### 4. Executar Deploy

```bash
# Dar permissão
chmod +x deploy_aws.sh

# Executar deploy
./deploy_aws.sh
```

O script vai:
1. ✅ Empacotar modelo e dependências
2. ✅ Criar IAM Role
3. ✅ Criar função Lambda
4. ✅ Criar API Gateway
5. ✅ Retornar endpoint da API

### 5. Testar API

Você vai receber um endpoint tipo:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com
```

Teste com:
```bash
python test_api.py https://seu-endpoint.amazonaws.com
```

---

## ⚠️ PROBLEMA: Modelo Muito Grande

O modelo `best_model_fe.h5` tem **61 MB**. AWS Lambda permite até **250 MB descompactado**.

Com TensorFlow + dependências, pode ultrapassar o limite.

### Soluções:

#### Opção A: Usar S3 para hospedar modelo

1. Upload modelo para S3:
```bash
aws s3 mb s3://feces-classifier-models
aws s3 cp best_model_fe.h5 s3://feces-classifier-models/
```

2. Modificar lambda_function.py para baixar de S3

#### Opção B: Usar AWS SageMaker (mais caro)

SageMaker é feito para ML e não tem limite de tamanho.

#### Opção C: Otimizar modelo

Reduzir tamanho com quantização:
```python
import tensorflow as tf

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Salvar modelo menor
with open('model_optimized.tflite', 'wb') as f:
    f.write(tflite_model)
```

---

## 💰 Custos Estimados

### AWS Lambda (Free Tier)
- **1 milhão de requests grátis/mês**
- **400,000 GB-segundos grátis/mês**

Depois do Free Tier:
- $0.20 por 1 milhão de requests
- $0.0000166667 por GB-segundo

### Exemplo:
- 10,000 requests/mês
- 512 MB RAM
- 5 segundos/request

**Custo:** ~$0 (dentro do free tier)

### API Gateway (Free Tier)
- **1 milhão de chamadas grátis** (primeiros 12 meses)

Depois:
- $1.00 por milhão de requests

---

## 🔧 Troubleshooting

### Erro: "Function too large"
- Modelo + dependências > 250 MB
- **Solução:** Use S3 para hospedar modelo (Opção A acima)

### Erro: "Timeout"
- Função demorando > 30 segundos
- **Solução:** Aumentar timeout:
```bash
aws lambda update-function-configuration \
    --function-name feces-classifier \
    --timeout 60
```

### Erro: "Out of memory"
- Modelo precisa de mais RAM
- **Solução:** Aumentar memória:
```bash
aws lambda update-function-configuration \
    --function-name feces-classifier \
    --memory-size 1024
```

---

## 📊 Monitoramento

### Ver logs:
```bash
aws logs tail /aws/lambda/feces-classifier --follow
```

### Ver métricas:
Console AWS → CloudWatch → Metrics → Lambda

---

## 🗑️ Deletar Recursos

Para evitar custos, delete tudo quando terminar de testar:

```bash
# Deletar função Lambda
aws lambda delete-function --function-name feces-classifier

# Deletar API Gateway
aws apigatewayv2 delete-api --api-id [SEU_API_ID]

# Deletar IAM Role
aws iam detach-role-policy \
    --role-name lambda-feces-classifier-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam delete-role --role-name lambda-feces-classifier-role
```

---

## 📝 Próximos Passos

1. ✅ Deploy básico funcionando
2. Adicionar autenticação (API Key)
3. Adicionar rate limiting
4. Configurar domínio customizado
5. Adicionar monitoramento avançado

---

## 🆘 Precisa de Ajuda?

- AWS Lambda Docs: https://docs.aws.amazon.com/lambda/
- AWS Free Tier: https://aws.amazon.com/free/
- Suporte: https://aws.amazon.com/support/
