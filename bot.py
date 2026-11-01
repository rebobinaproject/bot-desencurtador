import os
import re
import threading
import sys
from flask import Flask
import telebot
import requests

# 1. Configuração do Servidor Web Flask (para o Render)
app = Flask(name)

@app.route('/')
def health_check():
    return "Bot Online e Funcional!", 200

def iniciar_servidor_web():
    port = int(os.environ.get("PORT", 10000))
    print(f"Iniciando servidor web na porta {port}...")
    app.run(host="0.0.0.0", port=port)

# 2. Leitura e validação do Token do Telegram
TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    print("ERRO CRÍTICO: A variável TELEGRAM_TOKEN não foi encontrada nas Environment Variables do Render!")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

# 3. Lógica para extrair e resolver URLs encurtadas
def resolver_url(url_encurtada):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Requisição inicial
        resposta = requests.get(url_encurtada, allow_redirects=True, timeout=10, headers=headers)
        url_atual = resposta.url
        
        # Tratamento específico para encurtador.dev / l1nq.com
        if "encurtador.dev" in url_atual or "l1nq.com" in url_atual:
            html = resposta.text
            
            # Busca por redirecionamentos em Meta Tags HTML
            meta_match = re.search(r'content=["\'].*?url=(https?://[^"\']+)["\']', html, re.IGNORECASE)
            if meta_match:
                return meta_match.group(1)
            
            # Busca por redirecionamentos via JavaScript
            js_match = re.search(r'window\.location(?:\.href)?\s*=\s*["\'](https?://[^"\']+)["\']', html, re.IGNORECASE)
            if js_match:
                return js_match.group(1)

            # Busca por links de saída dentro do HTML
            links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html)
            for link in links:
                if "encurtador.dev" not in link and "l1nq.com" not in link:
                    return link

        return url_atual
    except Exception as e:
        print(f"Erro ao resolver URL: {e}")
        return None

# 4. Handlers do Bot do Telegram
@bot.message_handler(commands=['start', 'help'])
def comando_inicio(message):
    bot.reply_to(message, "Envie um link encurtado e eu retornarei a URL de destino original.")

@bot.message_handler(func=lambda msg: True)
def tratar_mensagens(message):
    texto = message.text.strip()
    if texto.startswith("http://") or texto.startswith("https://"):
        bot.send_chat_action(message.chat.id, 'typing')
        url_final = resolver_url(texto)
        if url_final:
            bot.reply_to(message, f"🔗 Link Original:\n{url_final}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "⚠️ Não foi possível acessar ou resolver este link.")
    else:
        bot.reply_to(message, "Envie uma URL válida (iniciando com http:// ou https://).")

# 5. Execução Principal
if name == "main":
    # Inicia o Flask em uma thread separada para não bloquear o polling do Telegram
    t = threading.Thread(target=iniciar_servidor_web, daemon=True)
    t.start()
    
    print("Bot ativo e aguardando mensagens no Telegram...")
    bot.infinity_polling()
