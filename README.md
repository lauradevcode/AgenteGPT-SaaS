#AgenteGPT - Seu Agente Inteligente no WhatsApp

Este projeto implementa um agente inteligente (AgenteGPT) que interage com usuários via WhatsApp, utilizando a API do Google Gemini para geração de respostas e a plataforma UltraMsg para comunicação com o WhatsApp.

Pré-requisitos
Antes de começar, você precisará ter o seguinte instalado:

Python 3.7 ou superior: Certifique-se de que o Python esteja instalado em seu sistema. Você pode verificar sua versão executando python --version ou python3 --version no terminal.
pip: O gerenciador de pacotes do Python, geralmente instalado com o Python.
ngrok: Uma ferramenta para expor seu servidor local à internet, necessária para receber webhooks do UltraMsg. Você pode baixá-lo em https://ngrok.com/download e precisar criar uma conta para obter um token authtoken.
Configuração
Siga estas etapas para configurar o projeto:

Clone o repositório (se aplicável):
Se você tem o código em um repositório (por exemplo, GitHub), clone-o para o seu computador.
```bash
git clone SEU_REPOSITORIO_AQUI
cd agenteGPT
```

Crie um ambiente virtual:
É recomendado usar um ambiente virtual para isolar as dependências do projeto.
```bash
python -m venv venv
```
Ative o ambiente virtual:

No Windows: ```bash venv\Scripts\activate ```
No macOS e Linux: ```bash source venv/bin/activate ```
Instale as dependências:
Navegue até a pasta do projeto (onde o arquivo app.py está localizado) e instale as bibliotecas necessárias a partir do arquivo (se você tiver um requirements.txt) ou instalando individualmente:
```bash
pip install Flask requests python-dotenv google-generativeai
```

Configure as variáveis de ambiente:
Crie um arquivo chamado .env na raiz do seu projeto e adicione as seguintes variáveis com suas respectivas informações:
```
ULTRA_API_INSTANCE=SUA_INSTANCIA_ULTRAMSG
ULTRA_API_TOKEN=SEU_TOKEN_ULTRAMSG
GEMINI_API_KEY=SUA_CHAVE_DE_API_DO_GEMINI
```

Você obterá a ULTRA_API_INSTANCE e ULTRA_API_TOKEN ao criar uma instância na plataforma UltraMsg (https://ultramsg.com/).
Você obterá a GEMINI_API_KEY ao criar um projeto no Google AI Studio (https://aistudio.google.com/).
Como Rodar o Projeto
Ative o ambiente virtual (se ainda não estiver ativo):

Windows: venv\\Scripts\\activate
macOS/Linux: source venv/bin/activate
Execute o servidor Flask:
Navegue até a pasta do projeto no seu terminal e execute o seguinte comando:
```bash
python app.py
```
Você deverá ver uma saída indicando que o servidor Flask está rodando (geralmente em http://127.0.0.1:5000/).

Exponha seu servidor local com ngrok:
Abra um novo terminal (mantenha o terminal do Flask rodando). Execute o seguinte comando, substituindo 5000 pela porta que o Flask está usando, se for diferente:
```bash
ngrok http 5000
```
O ngrok irá fornecer um URL público https://<seu_subdominio>.ngrok-free.app (ou similar). Copie este URL HTTPS.

Configure o Webhook no UltraMsg:

Acesse o painel da sua instância UltraMsg (https://ultramsg.com/client/instances).
Localize sua instância.
Vá para as configurações de "Webhook".
No campo "Webhook URL", cole o URL HTTPS do ngrok que você copiou, adicionando /webhook ao final. Por exemplo: https://<seu_subdominio>.ngrok-free.app/webhook.
Salve as configurações do Webhook.
Como Usar
Envie uma mensagem de WhatsApp para o número conectado à sua instância UltraMsg.
O seu AgenteGPT receberá a mensagem através do webhook configurado no UltraMsg.
A mensagem será processada pelo seu servidor Flask (app.py).
O AgenteGPT usará a API do Google Gemini para gerar uma resposta com base no conteúdo da sua mensagem e no perfil configurado.
A resposta gerada será enviada de volta para você via WhatsApp através da API do UltraMsg.
Observações Importantes:

Mantenha as janelas do terminal do servidor Flask (python app.py) e do ngrok rodando enquanto você quiser que o AgenteGPT esteja online e respondendo.
Certifique-se de que sua chave de API do Google Gemini tenha créditos ou esteja configurada corretamente.
Verifique os logs no terminal do servidor Flask para quaisquer erros ou informações de depuração.
