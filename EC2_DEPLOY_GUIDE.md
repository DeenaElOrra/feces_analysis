# Guia de Deploy na AWS EC2 - Classificador de Fezes

## Por que EC2 em vez de Lambda?

- **Modelo grande (61 MB)** + TensorFlow = muito pesado para Lambda
- **EC2 Free Tier:** 750 horas/mês grátis (t2.micro ou t3.micro)
- **Mais controle:** Instalar o que quiser, sem limites de tamanho
- **Melhor para ML:** Mantém modelo carregado na memória

---

## 📋 Pré-requisitos

1. **Conta AWS** (Free Tier disponível)
2. **AWS CLI instalado e configurado**
3. **Par de chaves SSH** (vamos criar)

---

## 🚀 Deploy Passo a Passo

### 1. Criar Conta AWS

1. Acesse: https://aws.amazon.com/
2. Clique em "Create an AWS Account"
3. Preencha seus dados
4. **Importante:** Precisa de cartão de crédito, mas não será cobrado no Free Tier

### 2. Criar Par de Chaves SSH

```bash
# Criar par de chaves no AWS
aws ec2 create-key-pair \
    --key-name feces-classifier-key \
    --query 'KeyMaterial' \
    --output text > ~/.ssh/feces-classifier-key.pem

# Dar permissão correta (IMPORTANTE!)
chmod 400 ~/.ssh/feces-classifier-key.pem
```

### 3. Criar Security Group

```bash
# Criar security group que permite HTTP (80) e SSH (22)
aws ec2 create-security-group \
    --group-name feces-classifier-sg \
    --description "Security group for feces classifier API"

# Permitir SSH (porta 22)
aws ec2 authorize-security-group-ingress \
    --group-name feces-classifier-sg \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

# Permitir HTTP (porta 80)
aws ec2 authorize-security-group-ingress \
    --group-name feces-classifier-sg \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Permitir porta 8501 (Streamlit)
aws ec2 authorize-security-group-ingress \
    --group-name feces-classifier-sg \
    --protocol tcp \
    --port 8501 \
    --cidr 0.0.0.0/0
```

### 4. Executar Deploy Automático

```bash
# Dar permissão
chmod +x deploy_ec2.sh

# Executar deploy
./deploy_ec2.sh
```

O script vai:
1. ✅ Criar instância EC2 (t3.micro - Free Tier)
2. ✅ Esperar instância iniciar
3. ✅ Fazer upload do modelo e código
4. ✅ Instalar dependências
5. ✅ Iniciar servidor Streamlit
6. ✅ Retornar URL de acesso

---

## 🌐 Acessar Aplicação

Após o deploy, você receberá um endereço tipo:
```
http://ec2-54-123-45-67.compute-1.amazonaws.com:8501
```

**Acesse no navegador** e você verá a interface Streamlit!

---

## 🔧 Comandos Úteis

### Conectar via SSH

```bash
ssh -i ~/.ssh/feces-classifier-key.pem ubuntu@<SEU_IP_PUBLICO>
```

### Ver logs do Streamlit

```bash
ssh -i ~/.ssh/feces-classifier-key.pem ubuntu@<SEU_IP_PUBLICO> "tail -f /home/ubuntu/feces-classifier/streamlit.log"
```

### Reiniciar aplicação

```bash
ssh -i ~/.ssh/feces-classifier-key.pem ubuntu@<SEU_IP_PUBLICO> "sudo systemctl restart feces-classifier"
```

### Parar instância (economizar créditos)

```bash
# Parar (mantém dados, não cobra compute)
aws ec2 stop-instances --instance-ids <INSTANCE_ID>

# Iniciar novamente
aws ec2 start-instances --instance-ids <INSTANCE_ID>
```

### Ver status

```bash
aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=feces-classifier" \
    --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress]' \
    --output table
```

---

## 💰 Custos Estimados

### EC2 t3.micro (Free Tier)
- **750 horas grátis/mês** (primeiros 12 meses)
- **1 GB de RAM**
- **2 vCPUs**
- Depois do Free Tier: ~$0.0104/hora (~$7.50/mês)

### Armazenamento EBS
- **30 GB grátis/mês** (Free Tier)
- Depois: $0.10/GB/mês

### Transferência de dados
- **100 GB grátis/mês de saída**
- Depois: $0.09/GB

### Exemplo de uso (dentro do Free Tier):
- Instância rodando 24/7 por 30 dias = 720 horas
- **Custo:** $0 (dentro do free tier)

---

## ⚠️ IMPORTANTE: Configuração de Domínio (Opcional)

O IP público da EC2 muda quando você para/inicia a instância.

### Opções:

#### Opção A: Elastic IP (grátis se usado)
```bash
# Alocar IP fixo
aws ec2 allocate-address --domain vpc

# Associar à instância
aws ec2 associate-address \
    --instance-id <INSTANCE_ID> \
    --allocation-id <ALLOCATION_ID>
```

**Importante:** IP Elástico é grátis **ENQUANTO** a instância estiver rodando. Se parar a instância e manter o IP alocado, cobra $0.005/hora (~$3.60/mês).

#### Opção B: Domínio próprio + Route 53
- Registrar domínio (ex: meubristol.com.br)
- Usar Route 53 para DNS
- Mais profissional, mas custa ~$12/ano (domínio)

---

## 🔧 Troubleshooting

### Erro: "Connection refused" na porta 8501
```bash
# Verificar se Streamlit está rodando
ssh -i ~/.ssh/feces-classifier-key.pem ubuntu@<IP> "ps aux | grep streamlit"

# Se não estiver, reiniciar
ssh -i ~/.ssh/feces-classifier-key.pem ubuntu@<IP> "sudo systemctl restart feces-classifier"
```

### Erro: "Permission denied (publickey)"
```bash
# Verificar permissão da chave
chmod 400 ~/.ssh/feces-classifier-key.pem

# Verificar se está usando o usuário correto
# Para Amazon Linux: ec2-user
# Para Ubuntu: ubuntu
```

### Erro: Instância lenta
- t3.micro tem 1 GB RAM
- TensorFlow pode usar muita memória
- **Solução:** Aumentar para t3.small (2 GB RAM)
```bash
aws ec2 modify-instance-attribute \
    --instance-id <INSTANCE_ID> \
    --instance-type t3.small
```
**OBS:** t3.small NÃO está no Free Tier (~$15/mês)

---

## 🗑️ Deletar Recursos

Para evitar custos, delete tudo quando terminar:

```bash
# 1. Pegar Instance ID
INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=feces-classifier" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text)

# 2. Terminar instância
aws ec2 terminate-instances --instance-ids $INSTANCE_ID

# 3. Deletar security group (aguardar instância terminar)
aws ec2 delete-security-group --group-name feces-classifier-sg

# 4. Deletar chave
aws ec2 delete-key-pair --key-name feces-classifier-key
rm ~/.ssh/feces-classifier-key.pem

# 5. Se criou Elastic IP, liberar
aws ec2 release-address --allocation-id <ALLOCATION_ID>
```

---

## 📊 Monitoramento

### CloudWatch (gratuito)
Console AWS → CloudWatch → Metrics → EC2

Métricas disponíveis:
- CPU utilization
- Network in/out
- Status checks

### Logs da aplicação
```bash
ssh -i ~/.ssh/feces-classifier-key.pem ubuntu@<IP> "tail -100 /home/ubuntu/feces-classifier/streamlit.log"
```

---

## 🚀 Melhorias Futuras

1. **HTTPS:** Configurar certificado SSL com Let's Encrypt
2. **Domínio:** Registrar domínio próprio
3. **Autenticação:** Adicionar login com Streamlit authenticator
4. **Backup:** Snapshot automático do EBS
5. **Escalabilidade:** Load Balancer + Auto Scaling
6. **CI/CD:** GitHub Actions para deploy automático

---

## 📝 Arquitetura Final

```
Internet
    ↓
AWS Security Group (Firewall)
    ↓
EC2 Instance (t3.micro)
    ├── Ubuntu 24.04 LTS
    ├── Python 3.11
    ├── TensorFlow 2.15
    ├── Streamlit 1.28
    └── Modelo (best_model_fe.h5)
```

---

## 🆘 Precisa de Ajuda?

- AWS EC2 Docs: https://docs.aws.amazon.com/ec2/
- AWS Free Tier: https://aws.amazon.com/free/
- Streamlit Docs: https://docs.streamlit.io/
- Suporte: https://aws.amazon.com/support/
