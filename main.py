import os
import sys
import requests
from flask import Flask
import threading
import time

app = Flask(__name__)

# Настройки
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8225982359:AAFTkgY86NgkaeMcb8SUzee-n8kws-IYMZQ")
CHAT_ID = os.environ.get("CHAT_ID", "-1003679701875")

print("="*50, file=sys.stderr)
print("🚀 БОТ ЗАПУСКАЕТСЯ", file=sys.stderr)
print(f"BOT_TOKEN: {'✅' if BOT_TOKEN else '❌'}", file=sys.stderr)
print(f"CHAT_ID: {CHAT_ID}", file=sys.stderr)
print("="*50, file=sys.stderr)
sys.stderr.flush()

@app.route('/')
def home():
    return "Бот работает! <a href='/send_test'>Отправить тест</a>"

@app.route('/send_test')
def send_test():
    """Простой тест отправки"""
    result = send_message("🔧 Тест от бота на Railway")
    return f"Результат: {'✅ Успех' if result else '❌ Ошибка'}"

def send_message(text):
    """Отправка сообщения"""
    print(f"📤 Пытаюсь отправить: {text}", file=sys.stderr)
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        print(f"📡 Статус ответа: {response.status_code}", file=sys.stderr)
        print(f"📡 Ответ сервера: {response.text[:200]}", file=sys.stderr)
        
        if response.status_code == 200:
            print("✅ Сообщение отправлено успешно!", file=sys.stderr)
            return True
        else:
            print(f"❌ Ошибка Telegram API: {response.status_code}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"💥 Исключение при отправке: {e}", file=sys.stderr)
        return False

def bot_worker():
    """Фоновый процесс бота"""
    time.sleep(3)  # Ждем запуска Flask
    
    print("🤖 Запускаю фонового бота...", file=sys.stderr)
    
    # Тестовое сообщение при запуске
    send_message("🤖 Бот запущен на Railway!")
    
    print("✅ Бот работает в фоне", file=sys.stderr)
    
    # Просто держим процесс запущенным
    while True:
        time.sleep(60)

if __name__ == "__main__":
    # Запускаем бота в фоне
    threading.Thread(target=bot_worker, daemon=True).start()
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Запускаю Flask на порту {port}", file=sys.stderr)
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
