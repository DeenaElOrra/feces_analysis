#!/bin/bash

################################################################################
# Script de Deploy Automático - EC2
# Classificador de Fezes (Escala de Bristol)
################################################################################

set -e  # Parar em caso de erro

# Configurações
KEY_NAME="feces-classifier-key"
KEY_PATH="$HOME/.ssh/${KEY_NAME}.pem"
SECURITY_GROUP="feces-classifier-sg"
INSTANCE_TYPE="t3.micro"  # Free Tier elegível
REGION="us-east-1"
AMI_ID="ami-0e2c8caa4b6378d8c"  # Ubuntu 24.04 LTS (us-east-1)
INSTANCE_NAME="feces-classifier"

echo "======================================================================"
echo "🚀 Deploy Automático - Classificador de Fezes (EC2)"
echo "======================================================================"

# 1. Verificar AWS CLI
echo ""
echo "⏳ Verificando AWS CLI..."
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI não encontrado. Instale com: brew install awscli"
    exit 1
fi
echo "✅ AWS CLI encontrado"

# 2. Criar par de chaves (se não existir)
echo ""
echo "⏳ Criando par de chaves SSH..."
if [ -f "$KEY_PATH" ]; then
    echo "✅ Chave já existe: $KEY_PATH"
else
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --query 'KeyMaterial' \
        --output text \
        --region $REGION > $KEY_PATH
    chmod 400 $KEY_PATH
    echo "✅ Chave criada: $KEY_PATH"
fi

# 3. Obter VPC padrão ou criar uma
echo ""
echo "⏳ Verificando VPC..."
VPC_ID=$(aws ec2 describe-vpcs \
    --filters "Name=is-default,Values=true" \
    --region $REGION \
    --query 'Vpcs[0].VpcId' \
    --output text 2>/dev/null)

if [ "$VPC_ID" == "None" ] || [ -z "$VPC_ID" ]; then
    echo "⚠️  Nenhuma VPC padrão encontrada. Criando VPC..."
    VPC_ID=$(aws ec2 create-vpc \
        --cidr-block 10.0.0.0/16 \
        --region $REGION \
        --query 'Vpc.VpcId' \
        --output text)

    # Esperar VPC estar disponível
    aws ec2 wait vpc-available --vpc-ids $VPC_ID --region $REGION

    # Criar subnet
    SUBNET_ID=$(aws ec2 create-subnet \
        --vpc-id $VPC_ID \
        --cidr-block 10.0.1.0/24 \
        --region $REGION \
        --query 'Subnet.SubnetId' \
        --output text)

    # Criar Internet Gateway
    IGW_ID=$(aws ec2 create-internet-gateway \
        --region $REGION \
        --query 'InternetGateway.InternetGatewayId' \
        --output text)

    # Anexar IGW à VPC
    aws ec2 attach-internet-gateway \
        --vpc-id $VPC_ID \
        --internet-gateway-id $IGW_ID \
        --region $REGION

    # Criar Route Table
    ROUTE_TABLE_ID=$(aws ec2 create-route-table \
        --vpc-id $VPC_ID \
        --region $REGION \
        --query 'RouteTable.RouteTableId' \
        --output text)

    # Adicionar rota para internet
    aws ec2 create-route \
        --route-table-id $ROUTE_TABLE_ID \
        --destination-cidr-block 0.0.0.0/0 \
        --gateway-id $IGW_ID \
        --region $REGION

    # Associar subnet à route table
    aws ec2 associate-route-table \
        --subnet-id $SUBNET_ID \
        --route-table-id $ROUTE_TABLE_ID \
        --region $REGION

    # Habilitar IP público automático
    aws ec2 modify-subnet-attribute \
        --subnet-id $SUBNET_ID \
        --map-public-ip-on-launch \
        --region $REGION

    echo "✅ VPC criada: $VPC_ID"
    USING_SUBNET=true
else
    echo "✅ VPC encontrada: $VPC_ID"
    USING_SUBNET=false
fi

# 4. Criar Security Group (se não existir)
echo ""
echo "⏳ Configurando Security Group..."
SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SECURITY_GROUP" "Name=vpc-id,Values=$VPC_ID" \
    --region $REGION \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null)

if [ "$SG_ID" == "None" ] || [ -z "$SG_ID" ]; then
    # Criar
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP \
        --description "Security group for feces classifier" \
        --vpc-id $VPC_ID \
        --region $REGION \
        --query 'GroupId' \
        --output text)

    # SSH
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region $REGION

    # Streamlit
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 8501 \
        --cidr 0.0.0.0/0 \
        --region $REGION

    echo "✅ Security Group criado: $SG_ID"
else
    echo "✅ Security Group já existe: $SG_ID"
fi

# 5. Criar instância EC2
echo ""
echo "⏳ Criando instância EC2..."

if [ "$USING_SUBNET" = true ]; then
    # Usar subnet específica se criamos VPC nova
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --instance-type $INSTANCE_TYPE \
        --key-name $KEY_NAME \
        --subnet-id $SUBNET_ID \
        --security-group-ids $SG_ID \
        --region $REGION \
        --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":20,"VolumeType":"gp3"}}]' \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
        --query 'Instances[0].InstanceId' \
        --output text)
else
    # Usar VPC padrão
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --instance-type $INSTANCE_TYPE \
        --key-name $KEY_NAME \
        --security-group-ids $SG_ID \
        --region $REGION \
        --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":20,"VolumeType":"gp3"}}]' \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
        --query 'Instances[0].InstanceId' \
        --output text)
fi

echo "✅ Instância criada: $INSTANCE_ID"

# 6. Aguardar instância iniciar
echo ""
echo "⏳ Aguardando instância iniciar (pode levar 1-2 minutos)..."
aws ec2 wait instance-running \
    --instance-ids $INSTANCE_ID \
    --region $REGION
echo "✅ Instância rodando!"

# Esperar mais um pouco para SSH ficar disponível
echo "⏳ Aguardando SSH ficar disponível..."
sleep 30

# 6. Obter IP público
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "✅ IP público: $PUBLIC_IP"

# 7. Aguardar status checks
echo ""
echo "⏳ Aguardando status checks (pode levar 2-3 minutos)..."
aws ec2 wait instance-status-ok \
    --instance-ids $INSTANCE_ID \
    --region $REGION
echo "✅ Status checks OK!"

# 8. Preparar arquivos para upload
echo ""
echo "⏳ Preparando arquivos..."
mkdir -p deploy_temp
cp app.py deploy_temp/
cp best_model_fe.h5 deploy_temp/
cp requirements.txt deploy_temp/

cat > deploy_temp/setup.sh << 'EOF'
#!/bin/bash
set -e

echo "🔧 Instalando dependências do sistema..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv

echo "🔧 Criando diretório da aplicação..."
mkdir -p ~/feces-classifier
cd ~/feces-classifier

echo "🔧 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

echo "🔧 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Criando serviço systemd..."
sudo tee /etc/systemd/system/feces-classifier.service > /dev/null << 'SYSTEMD'
[Unit]
Description=Feces Classifier Streamlit App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/feces-classifier
Environment="PATH=/home/ubuntu/feces-classifier/venv/bin"
ExecStart=/home/ubuntu/feces-classifier/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
SYSTEMD

echo "🔧 Iniciando serviço..."
sudo systemctl daemon-reload
sudo systemctl enable feces-classifier
sudo systemctl start feces-classifier

echo "✅ Setup completo!"
EOF

chmod +x deploy_temp/setup.sh

# 9. Upload de arquivos
echo ""
echo "⏳ Fazendo upload de arquivos..."
scp -i $KEY_PATH \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    deploy_temp/* ubuntu@$PUBLIC_IP:~/

echo "✅ Arquivos enviados!"

# 10. Executar setup remoto
echo ""
echo "⏳ Instalando aplicação na EC2..."
ssh -i $KEY_PATH \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    ubuntu@$PUBLIC_IP "bash ~/setup.sh"

echo "✅ Aplicação instalada!"

# 11. Limpar arquivos temporários
rm -rf deploy_temp

# 12. Resultado final
echo ""
echo "======================================================================"
echo "✅ DEPLOY COMPLETO!"
echo "======================================================================"
echo ""
echo "📋 Informações da instância:"
echo "   Instance ID: $INSTANCE_ID"
echo "   IP Público:  $PUBLIC_IP"
echo ""
echo "🌐 Acesse a aplicação em:"
echo "   http://$PUBLIC_IP:8501"
echo ""
echo "🔑 Conectar via SSH:"
echo "   ssh -i $KEY_PATH ubuntu@$PUBLIC_IP"
echo ""
echo "📊 Ver logs:"
echo "   ssh -i $KEY_PATH ubuntu@$PUBLIC_IP 'sudo journalctl -u feces-classifier -f'"
echo ""
echo "⏸️  Parar instância (economizar créditos):"
echo "   aws ec2 stop-instances --instance-ids $INSTANCE_ID --region $REGION"
echo ""
echo "▶️  Iniciar novamente:"
echo "   aws ec2 start-instances --instance-ids $INSTANCE_ID --region $REGION"
echo ""
echo "🗑️  Deletar tudo:"
echo "   aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region $REGION"
echo ""
echo "======================================================================"
