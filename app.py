import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import re

import google.generativeai as genai

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

ULTRA_API_INSTANCE = os.getenv('ULTRA_API_INSTANCE')
ULTRA_API_TOKEN = os.getenv('ULTRA_API_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("AVISO: GEMINI_API_KEY não configurada no arquivo .env. As respostas da IA não funcionarão.")

# Prompt padrão inicial (fallback)
current_profile_prompt = {
    "prompt": "**ATENÇÃO: Responda de forma clara e organizada. Utilize LISTAS (com números somente) e TÓPICOS para estruturar informações detalhadas quando for apropriado, facilitando a leitura. Evite negrito e itálico EXCESSIVOS, a menos que seja para um destaque pontual e importante. NÃO use quebras de linha duplas desnecessárias.** Você é um assistente prestativo e amigável, focado em oferecer informações úteis de forma concisa e direta. Responda de forma analítica, oferecendo sugestões quando relevante, mas mantenha um tom informal. Priorize sempre a clareza e a utilidade prática da informação."
}

product_info = {
    "name": "",
    "sale_link": "",
    "keywords": [],
    "description": ""
}

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
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem via UltraMsg: {e}")
        raise Exception(f"Erro na API do UltraMsg: {str(e)}")
    except ValueError as e:
        print(f"Erro de configuração: {e}")
        raise

def gerar_resposta_gemini(pergunta_usuario, perfil_prompt_base, force_product_context=None):
    """
    Gera uma resposta usando a API do Google Gemini.
    Adicionado force_product_context para injeção direta de contexto do produto.
    """
    try:
        if not GEMINI_API_KEY:
            raise ValueError("Chave da API do Gemini não configurada no .env.")

        model = genai.GenerativeModel('gemini-1.5-flash') 

        generation_config = {
            "temperature": 0.2, 
            "max_output_tokens": 500
        }

        global product_info
        
        product_context = ""
        
        if force_product_context and product_info["name"]:
            print("DEBUG: Gerando resposta com contexto de produto FORÇADO (intenção de compra/produto clara).")
            # --- MODIFICAÇÃO PRINCIPAL AQUI ---
            product_context += "\n\nO usuário explicitamente perguntou sobre o PRODUTO ou expressou intenção de compra. **Priorize a resposta sobre este produto, mantendo SEMPRE O TOM E O ESTILO do perfil ativo.** Apresente o produto, seus benefícios, e ofereça o link de venda ou mais detalhes diretamente, SEM divagar para informações genéricas sobre o tema principal. O produto em questão é:"
            product_context += f"\n- **Nome do Produto:** {product_info['name']}"
            if product_info["description"]:
                product_context += f"\n- **Descrição Detalhada:** {product_info['description']}"
            if product_info["sale_link"]:
                product_context += f"\n- **Link Direto para Compra/Mais Detalhes:** {product_info['sale_link']}"
            
        elif product_info["name"]:
            print("DEBUG: Gerando resposta com contexto de produto NORMAL.")
            product_context += "\n\nVocê tem acesso às informações do seguinte PRODUTO, mas **NÃO O MENCIONE OU SE REFIRA A ELE em sua PRIMEIRA SAUDAÇÃO ou em respostas genéricas que não perguntem sobre ele.**"
            product_context += "Somente inclua informações sobre o produto ou o mencione se a pergunta do usuário for explicitamente sobre um produto, compra, ou um tópico que suas 'keywords' associem ao produto. "
            
            product_context += f"\n- **Nome do Produto Principal:** {product_info['name']}"
            if product_info["description"]:
                product_context += f"\n- **Descrição Detalhada do Produto:** {product_info['description']}"
            if product_info["keywords"]:
                keywords_for_gemini = ", ".join(product_info['keywords'])
                product_context += f"\n- **Palavras-chave para identificar o produto:** {keywords_for_gemini} (Use estas palavras para saber que o usuário está falando deste produto)"
            if product_info["sale_link"]:
                product_context += f"\n- **Link para Venda/Mais Detalhes:** {product_info['sale_link']}"
            
            product_context += "\n\nSua prioridade é iniciar uma conversa genérica e útil. **APENAS ABORDE O PRODUTO SE O USUÁRIO EXPRESSAR INTERESSE OU PERGUNTAR ALGO RELACIONADO AO PRODUTO, VENDAS, OU UM TÓPICO QUE CORRESPONDA ÀS KEYWORDS FORNECIDAS.** Se o usuário perguntar algo como 'olá', 'tudo bem?', 'preciso de ajuda', responda de forma genérica e amigável, sem mencionar o produto, e convide-o a fazer sua pergunta."

        full_perfil_instruction = perfil_prompt_base + product_context
        
        initial_history_parts = [full_perfil_instruction]
        if product_info["name"]:
            initial_history_parts.append(f"Eu sou um assistente com o perfil definido, e o produto chave que posso ajudar é '{product_info['name']}'.")

        chat = model.start_chat(history=[
            {"role": "user", "parts": initial_history_parts},
            {"role": "model", "parts": ["Entendido. Minhas respostas serão conversacionais e úteis. Abordarei o produto apenas se o usuário expressar interesse ou fizer uma pergunta relacionada, reconhecendo o nome do produto. Como posso ajudar?"]}
        ])
        
        response = chat.send_message(pergunta_usuario, generation_config=generation_config)
        
        return response.text
    
    except Exception as e:
        print(f"Erro ao gerar resposta com Gemini: {e}")
        raise Exception(f"Erro na API do Gemini: {str(e)}")

# --- Rotas do Aplicativo ---

@app.route('/')
def home():
    """Rota inicial para exibir a página principal, AGORA SERÁ O LOGIN."""
    return render_template('login.html')

@app.route('/login.html')
def login_page():
    """Rota para exibir a página de login (agora idêntica à rota /)."""
    return render_template('login.html')

@app.route('/index.html') 
def index_page():
    """Rota para exibir a página principal (seleção de perfis)."""
    return render_template('index.html')

@app.route('/cadastrarproduto.html')
def cadastrar_produto_page():
    """Rota para exibir a página de cadastro de produto."""
    return render_template('cadastrarproduto.html')

@app.route('/testar')
def testar_mensagem():
    """
    Resta para testar o envio de uma mensagem de WhatsApp.
    Esta rota não é acionada ao clicar em um perfil na interface web.
    É mantida para depuração manual se necessário.
    """
    try:
        resposta = enviar_mensagem_whatsapp("Olá! Sou seu AgenteGPT! O que precisa para hoje? 👋", "+5561998548265")
        return jsonify({"status": "success", "response": resposta})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ativar-perfil', methods=['POST'])
def ativar_perfil():
    """
    Rota para ativar um perfil de IA e definir o prompt base,
    além de armazenar os dados do produto.
    """
    global current_profile_prompt
    global product_info

    try:
        data = request.json
        perfil_solicitado = data.get('perfil') # Este é o valor de data-profile do frontend
        received_product_data = data.get('product_data', {}) 
        
        if not perfil_solicitado:
            return jsonify({"error": "Perfil não especificado."}), 400

        keywords_str = received_product_data.get("keywords", "")
        # Garante que keywords sejam uma lista, mesmo que vazia
        cleaned_keywords = [k.strip().lower() for k in re.split(r'[,\s]+', keywords_str) if k.strip()]
        
        product_info.update({
            "name": received_product_data.get("name", ""),
            "sale_link": received_product_data.get("sale_link", ""),
            "keywords": cleaned_keywords, 
            "description": received_product_data.get("description", "")
        })
        
        print(f"\nDEBUG: Dados do produto recebidos e armazenados na memória do Agente: {product_info}\n")

        # --- AQUI ESTÁ A CORREÇÃO PRINCIPAL: AS CHAVES DO DICIONÁRIO 'prompt_bases' ---
        # --- AGORA ELAS CORRESPONDEM EXATAMENTE AOS VALORES DE 'data-profile' DO SEU HTML/JS ---
        prompt_bases = {
            "ebook_vendedor": """**ATENÇÃO: Responda de forma clara e organizada. Utilize LISTAS (com números) e TÓPICOS para estruturar informações detalhadas quando for apropriado, facilitando a leitura. Evite negrito e itálico EXCESSIVOS, a menos que seja para um destaque pontual e importante. NÃO use quebras de linha duplas desnecessárias.** Você é um assistente de vendas focado em Ebooks. Seu objetivo é responder dúvidas comuns, apresentar os benefícios do ebook, usar provas sociais (se aplicáveis) e gatilhos mentais (escassez, urgência, autoridade) para direcionar o lead para o link de venda. Seja persuasivo, amigável e direto na conversão.""",
            
            "curso_gravado": """**ATENÇÃO: Responda de forma clara e organizada. Utilize LISTAS (com números) e TÓPICOS para estruturar informações detalhadas quando for apropriado, facilitando a leitura. Evite negrito e itálico EXCESSIVOS, a menos que seja para um destaque pontual e importante. NÃO use quebras de linha duplas desnecessárias.** Você é um assistente para um Curso Gravado. Seu foco é apresentar os módulos do curso, seus benefícios e diferenciais. Destaque como o curso pode transformar o aluno e leve o lead a se inscrever. Seja didático, inspirador e convide a explorar mais o curso e o link de matrícula.""",
            
            "mentoria_consultoria": """**ATENÇÃO: Responda de forma clara e organizada. Utilize LISTAS (com números) e TÓPICOS para estruturar informações detalhadas quando for apropriado, facilitando a leitura. Evite negrito e itálico EXCESSIVOS, a menos que seja para um destaque pontual e importante. NÃO use quebras de linha duplas desnecessárias.** Você é um assistente de vendas para Mentoria/Consultoria. Sua principal função é demonstrar a autoridade do mentor, tirar objeções profundas, entender as dores do lead e qualificá-lo, preparando-o para uma conversa individual (1 a 1) com o consultor/mentor. Use uma linguagem profissional, empática e focada em resultados e transformação.""",
            
            "comunidade_paga": """**ATENÇÃO: Responda de forma clara e organizada. Utilize LISTAS (com números) e TÓPICOS para estruturar informações detalhadas quando for apropriado, facilitando a leitura. Evite negrito e itálico EXCESSIVOS, a menos que seja para um destaque pontual e importante. NÃO use quebras de linha duplas desnecessárias.** Você é um assistente focado em promover uma Comunidade Paga. Destaque os benefícios do networking, os conteúdos exclusivos, o senso de pertencimento à "tribo" e o suporte contínuo. Incentive a participação e mostre o valor de fazer parte, criando desejo de comunidade e exclusividade."""
        }
        
        # Tenta obter o prompt usando o nome do perfil recebido
        # Se não encontrar, usa o prompt padrão definido globalmente
        prompt_definido = prompt_bases.get(perfil_solicitado.lower(), current_profile_prompt["prompt"])
        
        current_profile_prompt["prompt"] = prompt_definido
        mensagem_status = f"Perfil '{perfil_solicitado.replace('_', ' ')}' ativado com sucesso!"

        return jsonify({
            "success": True,
            "message": mensagem_status,
            "prompt_atual": current_profile_prompt["prompt"], # Retorna o prompt que FOI definido
            "product_data_status": product_info
        })
        
    except Exception as e:
        print(f"ERRO ao ativar perfil: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook_whatsapp():
    """
    Endpoint para receber mensagens de webhook do UltraMsg.
    Este é o coração do seu Agente de IA para responder automaticamente.
    """
    try:
        data = request.json
        if not data:
            data = request.form

        if not data:
            print("DEBUG: Nenhum dado recebido no webhook.")
            return jsonify({"status": "error", "message": "Nenhum dado recebido no webhook."}), 400

        print(f"DEBUG: Webhook Data Recebido: {data}")

        webhook_payload_data = data.get('data')

        if not webhook_payload_data:
            print("DEBUG: Payload do webhook não contém 'data' aninhada esperada.")
            # UltraMsg pode enviar outros tipos de eventos que não contêm 'data',
            # então retornamos 200 para evitar reenvios.
            return jsonify({"status": "error", "message": "Payload mal formatado ou evento não relevante."}), 200

        numero_remetente_raw = webhook_payload_data.get('from')
        mensagem_recebida_raw = webhook_payload_data.get('body')
        mensagem_tipo = webhook_payload_data.get('type')
        
        if webhook_payload_data.get('fromMe'):
            print(f"DEBUG: Ignorando mensagem enviada pelo próprio bot (fromMe: {webhook_payload_data.get('fromMe')}).")
            return jsonify({"status": "ignored", "message": "Mensagem enviada pelo próprio bot."}), 200

        if mensagem_tipo != 'chat':
            resposta_aviso = "Olá! No momento, só consigo responder a mensagens de texto. Por favor, digite sua pergunta."
            print(f"DEBUG: Mensagem de tipo '{mensagem_tipo}' recebida de {numero_remetente_raw}. Enviando aviso.")
            envio_whatsapp = enviar_mensagem_whatsapp(resposta_aviso, numero_remetente_raw.replace('@c.us', ''))
            return jsonify({
                "status": "warning",
                "message": "Tipo de mensagem não suportado. Aviso enviado.",
                "whatsapp_response": envio_whatsapp
            }), 200

        if not numero_remetente_raw:
            print("DEBUG: Número do remetente ausente no webhook.")
            return jsonify({"status": "error", "message": "Número do remetente ausente."}), 400

        numero_remetente = numero_remetente_raw.replace('@c.us', '')

        if not mensagem_recebida_raw:
            print("DEBUG: Mensagem de texto vazia recebida.")
            return jsonify({"status": "error", "message": "Mensagem de texto vazia."}), 200

        mensagem_recebida = mensagem_recebida_raw.lower() 
        
        print(f"DEBUG: Mensagem de texto recebida de {numero_remetente}: '{mensagem_recebida}'")

        # --- LÓGICA DA MINI BASE DE CONHECIMENTO APRIMORADA ---
        force_product_context = False
        if product_info["name"]: 
            product_name_lower = product_info['name'].lower()
            product_keywords_list = product_info['keywords'] 

            purchase_keywords = ['comprar', 'onde comprar', 'quero comprar', 'preço', 'valor', 'link', 'adquirir', 'compro'] # Adicionado mais palavras
            
            # Verifica se o nome do produto ou alguma keyword está na mensagem
            product_or_keyword_mentioned = product_name_lower in mensagem_recebida or \
                                           any(keyword in mensagem_recebida for keyword in product_keywords_list)
            
            # Verifica se há intenção de compra
            purchase_intent_detected = any(pk in mensagem_recebida for pk in purchase_keywords)

            if product_or_keyword_mentioned and purchase_intent_detected:
                force_product_context = True
                print(f"DEBUG: Intenção de compra do produto '{product_name_lower}' detectada na mensagem. Forçando contexto do produto COM foco em venda.")
            elif product_or_keyword_mentioned:
                force_product_context = True
                print(f"DEBUG: Produto '{product_name_lower}' ou keyword detectada. Forçando contexto do produto para informações gerais.")


        print("DEBUG: Chamando gerar_resposta_gemini...")
        resposta_ia = gerar_resposta_gemini(mensagem_recebida, current_profile_prompt["prompt"], force_product_context)
        print(f"DEBUG: Resposta do Gemini recebida: '{resposta_ia}'")

        mensagem_formatada = resposta_ia

        # Ajustes de formatação para WhatsApp
        mensagem_formatada = mensagem_formatada.replace('**', '') # Remove negrito
        mensagem_formatada = mensagem_formatada.replace('* ', '• ') # Converte listas de Gemini para bullets do WhatsApp
        mensagem_formatada = mensagem_formatada.replace('*', '') # Remove itálico
        mensagem_formatada = mensagem_formatada.replace('__', '') # Remove itálico do Gemini
        mensagem_formatada = re.sub(r'\n{3,}', '\n\n', mensagem_formatada) # Normaliza múltiplas quebras de linha
        
        print(f"DEBUG: Resposta do Gemini recebida (após formatação): '{mensagem_formatada}'")

        print("DEBUG: Chamando enviar_mensagem_whatsapp...")
        envio_sucesso = enviar_mensagem_whatsapp(mensagem_formatada, numero_remetente) 
        print(f"DEBUG: Resposta do UltraMsg recebida: '{envio_sucesso}'")
        
        print(f"DEBUG: Resposta da IA enviada para {numero_remetente}: '{mensagem_formatada}'")

        return jsonify({
            "status": "success",
            "message": "Mensagem processada e resposta enviada.",
            "ia_response": resposta_ia,
            "formatted_ia_response": mensagem_formatada,
            "whatsapp_response": envio_sucesso
        })

    except Exception as e:
        print(f"ERRO CRÍTICO NO WEBHOOK: {e}")
        # Retorna 200 mesmo em caso de erro para evitar que o UltraMsg reenvie o webhook repetidamente.
        # O erro será logado no console.
        return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 200

if __name__ == '__main__':
    if not ULTRA_API_TOKEN:
        print("AVISO: ULTRA_API_TOKEN não configurado no arquivo .env")
    if not ULTRA_API_INSTANCE:
        print("AVISO: ULTRA_API_INSTANCE não configurado no arquivo .env")
    if not GEMINI_API_KEY:
        print("AVISO: GEMINI_API_KEY não configurada no arquivo .env. As respostas da IA não funcionarão.")

    app.run(debug=True, port=5000)