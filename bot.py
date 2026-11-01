import os
import threading
from flask import Flask
import telebot
import requests

# Servidor Flask simples para responder à verificação de estado (health check) do Render
app = Flask(name)

@app.route('/')
def health_check():
    return "Bot Online", 200

def iniciar_servidor_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Obtém o Token da variável de ambiente configurada no Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

def resolver_url(url_encurtada):
    try:
        # Simula um navegador real para evitar desvios para páginas de proteção
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari
