#!/usr/bin/env python3
import os
import sys
import requests
import time
import schedule
from datetime import datetime
import pytz
from flask import Flask
import threading

app = Flask(__name__)

# ============ НАСТРОЙКИ ============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8225982359:AAFTkgY86NgkaeMcb8SUzee-n8kws-IYMZQ")
CHAT_ID = os.environ.get("CHAT_ID", "-1003679701875")
TIMEZONE = "Europe/Moscow"

# ⚠️ ДЛЯ ТЕСТА - через 1-2-3 минуты

MORNING_HOUR = 09
MORNING_MINUTE = 1  # через 1 минуту

DAY_HOUR = 14
DAY_MINUTE = 1     # через 2 минуты

EVENING_HOUR = 19
EVENING_MINUTE = 1  # через 3 минуты
# ===================================

# Принудительный вывод в логи
print("="*50, file=sys.stderr)
print("🚀 ПРИЛОЖЕНИЕ ЗАПУСКАЕТСЯ", file=sys.stderr)
print(f"Токен: {'✅' if BOT_TOKEN else '❌'}", file=sys.stderr)
print(f"Chat ID: {'✅' if CHAT_ID else '❌'}", file=sys.stderr)
print("="*50, file=sys.stderr)
sys.stderr.flush()

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Telegram Bot</title></head>
    <body>
        <h1>Telegram Reminder Bot</h1>
        <p>Status: <span style="color: green;">✅ Running</span></p>
        <p>Bot Token: {}</p>
        <p>Chat ID: {}</p>
        <p><a href="/send_test">📤 Send Test Message</a></p>
        <p><a href="/health">❤️ Health Check</a></p>
    </body>
    </html>
    """.format("✅ Set" if BOT_TOKEN else "❌ Not set", 
               "✅ Set" if CHAT_ID else "❌ Not set")

@app.route('/health')
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}, 200

@app.route('/send_test')
def send_test():
    """Отправить тестовое сообщение"""
    result = send_telegram_message("🔧 Тестовое сообщение от бота на Railway!")
    return "✅ Тест отправлен!" if result else "❌ Ошибка отправки"

def send_telegram_message(text):
    """Отправка сообщения в Telegram"""
    if not BOT_TOKEN or not CHAT_ID:
        print(f"❌ Ошибка: BOT_TOKEN или CHAT_ID не установлены", file=sys.stderr)
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        print(f"📤 Отправляю сообщение в Telegram...", file=sys.stderr)
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Сообщение отправлено успешно!", file=sys.stderr)
            return True
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"💥 Ошибка при отправке: {e}", file=sys.stderr)
        return False

def send_morning():
    print(f"⏰ Отправляю утреннее напоминание...", file=sys.stderr)
    msg = f"""<b>⏰ УТРЕННЕЕ НАПОМИНАНИЕ</b>

<b>📋 НАЧАЛО РАБОЧЕГО ДНЯ</b>

Отправьте в чат:
<b>📅 Дата:</b> {datetime.now().strftime('%d.%m.%Y')}
<b>🏗 Объект:</b> (где работаете)
<b>👥 Сотрудники:</b> (список на объекте)
<b>📝 План работ:</b> (что будете делать)

⚠️ <b>За неоповещение - штраф</b>"""
    send_telegram_message(msg)

def send_day():
    print(f"📸 Отправляю дневное напоминание...", file=sys.stderr)
    msg = f"""<b>📸 ДНЕВНОЕ НАПОМИНАНИЕ</b>

<b>🎥 ФОТО/ВИДЕОФИКСАЦИЯ РАБОТ</b>

Отправляйте фото/видео с подписями

<b>Пример:</b>
«Откопана траншея 5 м»
«Установлено 5 фитингов»

⚠️ <b>Не забывайте фиксировать работу!</b>"""
    send_telegram_message(msg)

def send_evening():
    print(f"🌙 Отправляю вечернее напоминание...", file=sys.stderr)
    msg = f"""<b>🌙 ВЕЧЕРНЕЕ НАПОМИНАНИЕ</b>

<b>✅ КОНЕЦ РАБОЧЕГО ДНЯ</b>

<b>Отправьте невыполненные работы:</b>

<b>Пример:</b>
Не выполнено:
1. Прокладка трубы (не хватило материалов)
2. Установка фитингов (не было в наличии)

Или: <b>«Все работы выполнены»</b>"""
    send_telegram_message(msg)

def send_test_message():
    print(f"🔧 Отправляю тестовое сообщение...", file=sys.stderr)
    msg = f"""<b>🤖 БОТ ЗАПУЩЕН!</b>

✅ <b>Работает на Railway!</b>

📅 <b>Дата:</b> {datetime.now().strftime('%d.%m.%Y')}
⏰ <b>Время:</b> {datetime.now().strftime('%H:%M:%S')}
🌍 <b>Часовой пояс:</b> {TIMEZONE}

⚡ <b>Это тестовое сообщение</b>"""
    send_telegram_message(msg)

def start_bot():
    """Запуск бота в фоновом режиме"""
    print("🤖 ЗАПУСКАЮ ТЕЛЕГРАМ БОТА...", file=sys.stderr)
    sys.stderr.flush()
    
    # Проверка конфигурации
    if not BOT_TOKEN or BOT_TOKEN == "8225982359:AAFTkgY86NgkaeMcb8SUzee-n8kws-IYMZQ":
        print("❌ ОШИБКА: Не настроен BOT_TOKEN!", file=sys.stderr)
        return
    
    # Отправка тестового сообщения
    time.sleep(2)  # Ждем запуска Flask
    send_test_message()
    
    # Настройка расписания
    schedule.every().day.at(f"{MORNING_HOUR:02d}:{MORNING_MINUTE:02d}").do(send_morning)
    schedule.every().day.at(f"{DAY_HOUR:02d}:{DAY_MINUTE:02d}").do(send_day)
    schedule.every().day.at(f"{EVENING_HOUR:02d}:{EVENING_MINUTE:02d}").do(send_evening)
    
    print(f"⏰ Расписание настроено:", file=sys.stderr)
    print(f"   • {MORNING_HOUR:02d}:{MORNING_MINUTE:02d} - Утренний", file=sys.stderr)
    print(f"   • {DAY_HOUR:02d}:{DAY_MINUTE:02d} - Дневной", file=sys.stderr)
    print(f"   • {EVENING_HOUR:02d}:{EVENING_MINUTE:02d} - Вечерний", file=sys.stderr)
    print("✅ Бот запущен и работает!", file=sys.stderr)
    sys.stderr.flush()
    
    # Бесконечный цикл
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask сервер
    print(f"🌐 Запускаю Flask сервер...", file=sys.stderr)
    sys.stderr.flush()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

