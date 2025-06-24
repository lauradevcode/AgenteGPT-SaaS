# 🤖 AgenteGPT: Seu Assistente Inteligente no WhatsApp

**Automatize conversas, qualifique leads e encante seus clientes usando IA no WhatsApp.**
O **AgenteGPT** é um sistema inteligente que integra o poder do **Google Gemini** com a API da **UltraMsg**, transformando seu WhatsApp em um verdadeiro agente de atendimento e vendas 24/7.

---

## 🚀 O Que é o AgenteGPT?

O **AgenteGPT** é um chatbot inteligente desenvolvido em Python com Flask, que entende, responde e interage com seus clientes no WhatsApp de forma humanizada. Ele utiliza o **Google Gemini** para gerar respostas dinâmicas e personalizadas, com base no conteúdo da conversa.

### ✨ Benefícios

* **Atendimento Humanizado** com IA
* **Disponibilidade 24/7**, sem depender de você
* **Instalação simples** e rápida
* **Ideal para:** infoprodutores, e-commerces, prestadores de serviço, atendimento ao cliente e pré-vendas

---

## 🧰 Pré-requisitos

Antes de começar, garanta que você tem o ambiente configurado:

| Requisito      | Como instalar/verificar                                     |
| -------------- | ----------------------------------------------------------- |
| Python 3.7+    | `python --version` ou [python.org](https://www.python.org/) |
| pip            | Já vem com o Python                                         |
| ngrok          | [ngrok.com/download](https://ngrok.com/download)            |
| Conta ngrok    | Para gerar seu authtoken                                    |
| Conta UltraMsg | Para gerar instância e token                                |
| Conta Gemini   | [aistudio.google.com](https://aistudio.google.com/)         |

---

## 🛠️ Instalação e Configuração

### 1. Clone o Projeto

```bash
git clone SEU_REPOSITORIO_AQUI
cd agenteGPT
```

### 2. Crie e Ative o Ambiente Virtual

```bash
python -m venv venv
# Ative:
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
# ou manualmente:
pip install Flask requests python-dotenv google-generativeai
```

### 4. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
ULTRA_API_INSTANCE=SUA_INSTANCIA_ULTRAMSG
ULTRA_API_TOKEN=SEU_TOKEN_ULTRAMSG
GEMINI_API_KEY=SUA_CHAVE_DE_API_DO_GEMINI
```

Você obterá a **ULTRA\_API\_INSTANCE** e **ULTRA\_API\_TOKEN** ao criar uma instância na plataforma [UltraMsg](https://ultramsg.com/).
Você obterá a **GEMINI\_API\_KEY** ao criar um projeto no [Google AI Studio](https://aistudio.google.com/).

---

## ▶️ Executando o AgenteGPT

### 1. Inicie o Servidor Flask

```bash
python app.py
```

O servidor estará disponível em `http://127.0.0.1:5000`.

### 2. Exponha via Ngrok

Em um novo terminal:

```bash
ngrok http 5000
```

Copie a URL gerada (`https://<seu_subdominio>.ngrok-free.app`).

### 3. Configure o Webhook na UltraMsg

1. Acesse: [ultramsg.com/client/instances](https://ultramsg.com/client/instances)
2. Entre na instância desejada
3. Vá até **Configurações → Webhook**
4. Cole a URL do ngrok, com `/webhook` no final
   **Exemplo:** `https://<subdominio>.ngrok-free.app/webhook`
5. Salve

---

## 💬 Como Funciona?

1. O cliente envia uma mensagem para seu WhatsApp
2. A UltraMsg envia a mensagem via webhook para o seu servidor Flask
3. O Flask processa e envia o texto para a API do Gemini
4. O Gemini retorna uma resposta inteligente e contextualizada
5. O servidor devolve a resposta ao cliente via UltraMsg

---

## 📌 Observações Importantes

* **Deixe os dois terminais abertos**: `Flask` e `ngrok`
* Certifique-se de que sua **chave Gemini** está válida
* Verifique os **logs** para eventuais erros

---

## 🧠 Exemplos de Uso

| Cenário                  | Aplicação                                      |
| ------------------------ | ---------------------------------------------- |
| Vendas de Infoproduto    | Pré-venda automatizada e qualificação de leads |
| E-commerce               | Atendimento de pedidos e dúvidas 24h           |
| Serviços (freelas, etc.) | Conversas personalizadas com clientes          |
| Atendimento corporativo  | Respostas técnicas baseadas em documentação    |

---

## 🧪 Em breve...

* Painel de configuração via interface web
* Treinamento personalizado com arquivos PDF
* Perfis de atendimento com personalidade

---

## 👨‍💻 Desenvolvido por \ Laura Beatriz

Se quiser testar, contribuir ou contratar a solução personalizada:

📲 Me chama no WhatsApp \ https://api.whatsapp.com/send?phone=5561998548265

