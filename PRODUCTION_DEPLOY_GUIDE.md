# 🚀 Guia Completo de Deploy para Produção - Flora App

## 📋 Pré-requisitos

- [ ] Conta no GitHub (para hospedar código)
- [ ] Conta no Railway.app ou Render.com (backend - GRÁTIS)
- [ ] Conta Apple Developer ($99/ano) - para iOS
- [ ] Conta Google Play Console ($25 única vez) - para Android
- [ ] Expo account (grátis)

---

## 🎯 FASE 1: Deploy do Backend (30 minutos)

### Opção A: Railway (Recomendado - Mais Fácil)

#### 1. Preparar o Repositório

```bash
cd /Users/elorr/Documents/feces_analysis/feces_analysis

# Se ainda não tem git iniciado no backend
cd backend
git init
git add .
git commit -m "Initial backend commit"

# Criar repositório no GitHub e fazer push
# Vá em github.com/new e crie: flora-backend
git remote add origin https://github.com/SEU_USUARIO/flora-backend.git
git branch -M main
git push -u origin main
```

#### 2. Deploy no Railway

1. Acesse: https://railway.app
2. Clique em "Start a New Project"
3. Escolha "Deploy from GitHub repo"
4. Selecione o repositório `flora-backend`
5. Railway detecta automaticamente FastAPI

#### 3. Configurar Variáveis de Ambiente

No Railway, vá em **Variables** e adicione:

```env
DATABASE_URL=sqlite:///./feces_app.db
SECRET_KEY=SUA_CHAVE_SECRETA_AQUI_MUDE_ISSO
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PORT=8000
```

**⚠️ IMPORTANTE:** Gere uma SECRET_KEY forte:
```bash
openssl rand -hex 32
```

#### 4. Obter URL do Backend

Após deploy, Railway vai te dar uma URL tipo:
```
https://flora-backend-production-XXXX.up.railway.app
```

**✅ Salve essa URL! Você vai precisar dela.**

### Opção B: Render.com (Alternativa Grátis)

1. Acesse: https://render.com
2. "New" → "Web Service"
3. Conecte seu repositório GitHub
4. Configurações:
   - **Name:** flora-backend
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free
5. Adicione as mesmas variáveis de ambiente

---

## 📱 FASE 2: Configurar Mobile App (15 minutos)

### 1. Atualizar API_URL

Edite: `mobile-app/src/services/api.js`

```javascript
// ANTES (desenvolvimento)
const API_URL = 'http://172.20.10.2:8000';

// DEPOIS (produção)
const API_URL = 'https://flora-backend-production-XXXX.up.railway.app';
```

### 2. Instalar Expo CLI

```bash
npm install -g eas-cli
eas login
```

### 3. Configurar EAS

```bash
cd mobile-app
eas build:configure
```

Isso cria `eas.json`:

```json
{
  "cli": {
    "version": ">= 5.2.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "autoIncrement": true
    }
  },
  "submit": {
    "production": {}
  }
}
```

---

## 📦 FASE 3: Build do App (30-60 min por plataforma)

### Para Android (Google Play)

#### 1. Build APK para Teste

```bash
cd mobile-app
eas build --platform android --profile preview
```

Isso gera um APK que você pode compartilhar com amigos para testar.

#### 2. Build para Produção (Google Play)

```bash
eas build --platform android --profile production
```

### Para iOS (App Store)

#### 1. Build para TestFlight (Beta Testing)

```bash
eas build --platform ios --profile production
```

**Nota:** Precisa de conta Apple Developer ativa ($99/ano)

---

## 🏪 FASE 4: Publicar nas Lojas

### Google Play Store

1. Acesse: https://play.google.com/console
2. Criar aplicativo
3. Preencher informações:
   - Nome: Flora - Análise de Saúde Intestinal
   - Categoria: Saúde e fitness
   - Screenshots (tire do app rodando)
   - Descrição
   - Ícone (512x512px)
4. Upload do APK/AAB:
   ```bash
   eas submit --platform android
   ```
5. Preencher questionário de privacidade
6. Enviar para revisão (1-3 dias)

### Apple App Store

1. Acesse: https://appstoreconnect.apple.com
2. My Apps → + → New App
3. Preencher informações:
   - Nome: Flora
   - Categoria: Health & Fitness
   - Screenshots obrigatórios:
     - 6.5" iPhone (1284 x 2778)
     - 5.5" iPhone (1242 x 2208)
   - Descrição
   - Ícone (1024x1024px)
4. Upload do build:
   ```bash
   eas submit --platform ios
   ```
5. Enviar para revisão (1-2 dias)

---

## 🧪 FASE 5: Testar com Beta Testers (Recomendado)

### TestFlight (iOS)

```bash
eas build --platform ios --profile preview
```

Convide até 10,000 testers via email.

### Google Play Beta

No Play Console → Release → Testing → Internal testing

---

## 📊 Monitoramento

### Backend

Railway/Render tem logs integrados:
- Railway: aba "Deployments" → "View Logs"
- Render: aba "Logs"

### App Mobile

Expo tem analytics integrado:
```bash
expo whoami
```

Acesse: https://expo.dev → seu projeto → Analytics

---

## 💰 Custos Estimados

| Item | Custo | Frequência |
|------|-------|------------|
| Railway (Backend) | $5-10 | /mês |
| Render (Backend) | GRÁTIS | - |
| Apple Developer | $99 | /ano |
| Google Play Console | $25 | única vez |
| Domínio personalizado (opcional) | $10-15 | /ano |

**Total inicial:** $124-139 (se fizer ambas as plataformas)
**Mensal (após setup):** $5-10 (se usar Railway) ou GRÁTIS (Render)

---

## ✅ Checklist Final

Antes de lançar para clientes:

- [ ] Backend funcionando na URL pública
- [ ] API_URL atualizada no app
- [ ] Build do app testado em device real
- [ ] Pelo menos 5 beta testers testaram
- [ ] Screenshots e ícones prontos
- [ ] Política de privacidade criada
- [ ] Termos de uso criados
- [ ] Email de suporte configurado

---

## 🆘 Problemas Comuns

### "API_URL não atualizada"
- Verifique se fez novo build após mudar a URL
- Expo Go não funciona com builds de produção

### "Backend não responde"
- Verifique logs no Railway/Render
- Teste a URL direto no navegador: `https://sua-url.com/health`

### "Build falhou no iOS"
- Verifique se tem conta Apple Developer ativa
- Bundle ID precisa ser único (ex: com.seuusuario.flora)

---

## 📞 Suporte

Se tiver dúvidas:
1. Logs do Railway: `railway logs`
2. Logs do Expo: `eas build:list`
3. Documentação Expo: https://docs.expo.dev
4. Documentação Railway: https://docs.railway.app

---

**Próximo passo:** Comece pela Fase 1 (Deploy Backend)!
