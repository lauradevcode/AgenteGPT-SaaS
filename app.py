import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Importa a biblioteca do Google Gemini
import google.generativeai as genai

# --- Carrega as variáveis de ambiente do arquivo .env ---
load_dotenv()

# --- Configurações do Aplicativo Flask ---
app = Flask(__name__, static_folder='static', template_folder='templates')

# --- Credenciais e Configurações de API ---
ULTRA_API_INSTANCE = os.getenv('ULTRA_API_INSTANCE')
ULTRA_API_TOKEN = os.getenv('ULTRA_API_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') # Chave da API do Gemini do seu .env

# Configura o Google Gemini com a API Key
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY) # Reverte para esta forma mais simples
else:
    print("AVISO: GEMINI_API_KEY não configurada no arquivo .env. As respostas da IA não funcionarão.")

# Dicionário para armazenar o prompt base do perfil ativo (simplificado para um único perfil global)
current_profile_prompt = {
    "prompt": "Você é um assistente prestativo e amigável."
}

# --- Funções Auxiliares ---

def enviar_mensagem_whatsapp(mensagem, numero_destino):
    """Envia mensagem via API do UltraMsg"""
    try:
        if not all([ULTRA_API_INSTANCE, ULTRA_API_TOKEN]):
            raise ValueError("Credenciais da API do UltraMsg não configuradas no .env.")

        url = f"https://api.ultramsg.com/{ULTRA_API_INSTANCE}/messages/chat"
        
        payload = {
            "token": ULTRA_API_TOKEN,
            "to": numero_destino,
            "body": mensagem
        }
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status() # Lança exceção para erros HTTP (4xx ou 5xx)
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem via UltraMsg: {e}")
        raise Exception(f"Erro na API do UltraMsg: {str(e)}")
    except ValueError as e:
        print(f"Erro de configuração: {e}")
        raise

def gerar_resposta_gemini(pergunta_usuario, perfil_prompt):
    """Gera uma resposta usando a API do Google Gemini"""
    try:
        if not GEMINI_API_KEY:
            raise ValueError("Chave da API do Gemini não configurada no .env.")

        # --- CÓDIGO TEMPORÁRIO PARA DEPURAR MODELOS ---
        # Este bloco vai listar os modelos disponíveis e parar.
        # Você deve remover isso assim que encontrar o nome do modelo correto.
        found_model = None
        print("\n--- Modelos Gemini Disponíveis e Suportados para 'generateContent' ---")
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                print(f"Modelo: {m.name}")
                if "gemini-pro" in m.name: # Tentativa de encontrar o nome mais adequado para gemini-pro
                    found_model = m.name
        print("----------------------------------------------------------------------\n")

        if not found_model:
            raise Exception("Nenhum modelo Gemini adequado para 'generateContent' foi encontrado. Verifique sua chave de API e região.")

        # O modelo que será realmente usado (usamos o encontrado ou 'models/gemini-pro' como fallback se for o caso)
        # Se a lista acima te der um nome exato, use ele! Ex: 'models/gemini-1.0-pro'
        model_to_use = found_model # Usará o primeiro 'gemini-pro' encontrado

        # --- FIM DO CÓDIGO TEMPORÁRIO PARA DEPURAR MODELOS ---

        # Escolhe o modelo da Gemini
        model = genai.GenerativeModel('gemini-1.5-flash') # <-- AGORA USA A VARIÁVEL 'model_to_use'

        chat = model.start_chat(history=[
            {"role": "user", "parts": [perfil_prompt]},
            {"role": "model", "parts": ["Ok, entendi. Como posso ajudar?"]}
        ])

        response = chat.send_message(pergunta_usuario)

        return response.text

    except Exception as e:
        print(f"Erro ao gerar resposta com Gemini: {e}")
# --- Rotas do Aplicativo ---

@app.route('/')
def home():
    """Rota inicial para exibir a página principal."""
    return render_template('index.html')

# @app.route('/testar')
# def testar_mensagem():
#     """Rota para testar o envio de uma mensagem de WhatsApp."""
#     try:
#         # Use um número de telefone de teste real para o WhatsApp
#         resposta = enviar_mensagem_whatsapp("Olá! Sou seu AgenteGPT! O que precisa para hoje? 👋", "+5561998548265")
#         return jsonify({"status": "success", "response": resposta})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/ativar-perfil', methods=['POST'])
def ativar_perfil():
    """Rota para ativar um perfil de IA e definir o prompt base."""
    global current_profile_prompt # Permite modificar a variável global

    try:
        data = request.json
        perfil_solicitado = data.get('perfil')
        
        if not perfil_solicitado:
            return jsonify({"error": "Perfil não especificado."}), 400

        # Mapeamento dos perfis para seus prompts
        prompt_bases = {
            "atendimento": "Você é uma atendente gentil que trata o cliente como ouro.",
            "suporte": "Você é direto, prático e resolve o problema rápido.",
            "criador": "Você cria conteúdo como um copywriter experiente.",
            "produto": "Você explica produto de forma clara e tira dúvidas.",
            "vendedor": "Você convence o cliente a comprar como um expert."
        }

        prompt_definido = prompt_bases.get(perfil_solicitado.lower())
        
        if prompt_definido:
            current_profile_prompt["prompt"] = prompt_definido # Atualiza o prompt global
            mensagem_envio = f"Perfil '{perfil_solicitado}' ativado com sucesso! 🚀 Agora sou um {perfil_solicitado}."
        else:
            current_profile_prompt["prompt"] = "Você é um assistente prestativo e amigável." # Volta ao padrão
            mensagem_envio = f"Perfil '{perfil_solicitado}' não reconhecido. Ativando perfil padrão."

        # Envia uma notificação de ativação para o WhatsApp (opcional, mas bom para feedback)
        # Use o número do administrador ou um número de teste
        envio_whatsapp = enviar_mensagem_whatsapp(mensagem_envio, "+5561998548265")

        return jsonify({
            "success": True,
            "message": f"Perfil '{perfil_solicitado}' ativado!",
            "prompt_atual": current_profile_prompt["prompt"],
            "whatsapp_response": envio_whatsapp
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook_whatsapp():
    """
    Endpoint para receber mensagens de webhook do UltraMsg.
    Este é o coração do seu Agente de IA para responder automaticamente.
    """
    try:
        # Tenta ler como JSON, se não for, tenta como form data
        data = request.json
        if not data:
            data = request.form

        if not data:
            print("Nenhum dado recebido no webhook.")
            return jsonify({"status": "error", "message": "Nenhum dado recebido no webhook."}), 400

        print(f"Webhook Data Recebido: {data}") # Log para depuração

        webhook_payload_data = data.get('data')

        if not webhook_payload_data:
            print("Payload do webhook não contém 'data' aninhada esperada.")
            return jsonify({"status": "error", "message": "Payload mal formatado."}), 200

        numero_remetente_raw = webhook_payload_data.get('from')
        mensagem_recebida_raw = webhook_payload_data.get('body')
        
        # Filtra mensagens indesejadas (enviadas pelo próprio bot, ou que não são de texto)
        if webhook_payload_data.get('fromMe') or webhook_payload_data.get('type') != 'chat':
            print(f"Ignorando mensagem de tipo '{webhook_payload_data.get('type')}' ou enviada pelo próprio bot (fromMe: {webhook_payload_data.get('fromMe')}).")
            return jsonify({"status": "ignored", "message": "Mensagem não relevante para processamento."}), 200

        if not numero_remetente_raw or not mensagem_recebida_raw:
            print("Dados essenciais (remetente ou mensagem) ausentes no webhook APÓS filtro.")
            return jsonify({"status": "error", "message": "Dados essenciais ausentes após filtro."}), 400

        numero_remetente = numero_remetente_raw.replace('@c.us', '')
        mensagem_recebida = mensagem_recebida_raw

        print(f"Mensagem recebida de {numero_remetente}: '{mensagem_recebida}'")

        # 1. Geração da Resposta com Gemini
        # Agora chamamos a função gerar_resposta_gemini
        resposta_ia = gerar_resposta_gemini(mensagem_recebida, current_profile_prompt["prompt"])
        
        # 2. Envio da Resposta via UltraMsg
        envio_sucesso = enviar_mensagem_whatsapp(resposta_ia, numero_remetente)
        print(f"Resposta da IA enviada para {numero_remetente}: '{resposta_ia}'")

        return jsonify({
            "status": "success",
            "message": "Mensagem processada e resposta enviada.",
            "ia_response": resposta_ia,
            "whatsapp_response": envio_sucesso
        })

    except Exception as e:
        print(f"Erro no webhook: {e}")
        return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 200

# --- Execução do Aplicativo ---

if __name__ == '__main__':
    # Verificações de variáveis de ambiente ao iniciar
    if not ULTRA_API_TOKEN:
        print("AVISO: ULTRA_API_TOKEN não configurado no arquivo .env")
    if not ULTRA_API_INSTANCE:
        print("AVISO: ULTRA_API_INSTANCE não configurado no arquivo .env")
    if not GEMINI_API_KEY: # Agora verifica a chave do Gemini
        print("AVISO: GEMINI_API_KEY não configurada no arquivo .env. As respostas da IA não funcionarão.")

    app.run(debug=True, port=5000)