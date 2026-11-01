import os
import threading
from flask import Flask
import telebot
import requests

# Servidor Flask simples para atender ao check de saúde do Render
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot Telegram Online", 200

def iniciar_servidor_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Puxa o Token da variável de ambiente do servidor por segurança
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

def resolver_url(url_encurtada):
    try:
        resposta = requests.head(url_encurtada, allow_redirects=True, timeout=10)
        return resposta.url
    except Exception:
        return None

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
            bot.reply_to(message, f"🔗 **Link Original:**\n{url_final}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "⚠️ Não foi possível acessar ou resolver este link.")
    else:
        bot.reply_to(message, "Envie uma URL válida (iniciando com http:// ou https://).")

if __name__ == "__main__":
    # Inicia o servidor web em segundo plano
    threading.Thread(target=iniciar_servidor_web, daemon=True).start()
    
    print("Bot ativo e aguardando mensagens...")
    bot.infinity_polling()