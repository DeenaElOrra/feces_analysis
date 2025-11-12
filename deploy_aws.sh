#!/bin/bash
"""
Script de Deploy AWS Lambda
Empacota modelo e dependências e faz deploy
"""

set -e

echo "======================================================================"
echo "🚀 DEPLOY AWS LAMBDA - Classificador de Fezes"
echo "======================================================================"

# Configurações
FUNCTION_NAME="feces-classifier"
REGION="us-east-1"
RUNTIME="python3.9"
HANDLER="lambda_function.lambda_handler"
ROLE_NAME="lambda-feces-classifier-role"

# Verificar AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI não encontrado. Instale com: brew install awscli"
    exit 1
fi

echo ""
echo "📋 Passo 1: Preparar pacote Lambda"
echo "----------------------------------------------------------------------"

# Criar diretório temporário
rm -rf lambda_package
mkdir -p lambda_package

# Copiar função Lambda
echo "✓ Copiando lambda_function.py..."
cp lambda_function.py lambda_package/

# Copiar modelo (PROBLEMA: 61 MB é muito grande!)
echo "⚠️  ATENÇÃO: Modelo tem 61 MB, Lambda permite máx 250 MB descompactado"
echo "✓ Copiando best_model_fe.h5..."
cp best_model_fe.h5 lambda_package/

# Instalar dependências
echo ""
echo "📦 Passo 2: Instalar dependências Python"
echo "----------------------------------------------------------------------"

pip install \
    --platform manylinux2014_x86_64 \
    --target=lambda_package \
    --implementation cp \
    --python-version 3.9 \
    --only-binary=:all: \
    --upgrade \
    tensorflow==2.14.0 \
    pillow numpy

echo "✓ Dependências instaladas"

# Criar ZIP
echo ""
echo "🗜️  Passo 3: Criar arquivo ZIP"
echo "----------------------------------------------------------------------"

cd lambda_package
zip -r9 ../lambda_function.zip .
cd ..

ZIP_SIZE=$(du -h lambda_function.zip | cut -f1)
echo "✓ ZIP criado: lambda_function.zip ($ZIP_SIZE)"

# Criar role IAM (se não existir)
echo ""
echo "🔐 Passo 4: Criar/Verificar IAM Role"
echo "----------------------------------------------------------------------"

ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text 2>/dev/null || echo "")

if [ -z "$ROLE_ARN" ]; then
    echo "Criando IAM Role..."

    # Criar trust policy
    cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    # Criar role
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file://trust-policy.json

    # Anexar política básica de Lambda
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

    # Aguardar role propagar
    echo "Aguardando role propagar (10s)..."
    sleep 10

    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
    echo "✓ Role criada: $ROLE_ARN"
else
    echo "✓ Role já existe: $ROLE_ARN"
fi

# Criar ou atualizar função Lambda
echo ""
echo "☁️  Passo 5: Deploy na AWS Lambda"
echo "----------------------------------------------------------------------"

FUNCTION_EXISTS=$(aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null || echo "")

if [ -z "$FUNCTION_EXISTS" ]; then
    echo "Criando função Lambda..."

    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --zip-file fileb://lambda_function.zip \
        --timeout 30 \
        --memory-size 512 \
        --region $REGION

    echo "✓ Função Lambda criada!"
else
    echo "Atualizando função Lambda existente..."

    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda_function.zip \
        --region $REGION

    echo "✓ Função Lambda atualizada!"
fi

# Criar API Gateway
echo ""
echo "🌐 Passo 6: Criar API Gateway"
echo "----------------------------------------------------------------------"

API_ID=$(aws apigatewayv2 get-apis --query "Items[?Name=='$FUNCTION_NAME-api'].ApiId" --output text --region $REGION)

if [ -z "$API_ID" ]; then
    echo "Criando API Gateway HTTP..."

    API_ID=$(aws apigatewayv2 create-api \
        --name "$FUNCTION_NAME-api" \
        --protocol-type HTTP \
        --target "arn:aws:lambda:$REGION:$(aws sts get-caller-identity --query Account --output text):function:$FUNCTION_NAME" \
        --query 'ApiId' \
        --output text \
        --region $REGION)

    echo "✓ API Gateway criada: $API_ID"
else
    echo "✓ API Gateway já existe: $API_ID"
fi

# Dar permissão para API Gateway invocar Lambda
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:$(aws sts get-caller-identity --query Account --output text):$API_ID/*/*" \
    --region $REGION \
    2>/dev/null || echo "✓ Permissão já existe"

# Obter endpoint
API_ENDPOINT=$(aws apigatewayv2 get-apis --query "Items[?ApiId=='$API_ID'].ApiEndpoint" --output text --region $REGION)

echo ""
echo "======================================================================"
echo "✅ DEPLOY COMPLETO!"
echo "======================================================================"
echo ""
echo "🌐 API Endpoint:"
echo "   $API_ENDPOINT"
echo ""
echo "📝 Exemplo de uso (curl):"
echo ""
echo "   curl -X POST $API_ENDPOINT \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"image\": \"BASE64_ENCODED_IMAGE\"}'"
echo ""
echo "======================================================================"

# Limpar arquivos temporários
echo ""
echo "🧹 Limpando arquivos temporários..."
rm -rf lambda_package
rm trust-policy.json
echo "✓ Limpeza completa"

echo ""
echo "🎉 Deploy finalizado com sucesso!"
