#!/usr/bin/env python3
import os
import sys
import requests
import time
from datetime import datetime
import pytz
from flask import Flask
import threading

app = Flask(__name__)

# ============ НАСТРОЙКИ ============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8225982359:AAFTkgY86NgkaeMcb8SUzee-n8kws-IYMZQ")
CHAT_ID = os.environ.get("CHAT_ID", "-1003679701875")
TIMEZONE = "Europe/Moscow"

# ⚠️ УСТАНОВИТЕ ВРЕМЯ НАПОМИНАНИЙ
MORNING_HOUR = 10      
MORNING_MINUTE = 36

DAY_HOUR = 10         
DAY_MINUTE = 37

EVENING_HOUR = 10     
EVENING_MINUTE = 38
# ===================================

print("="*50, file=sys.stderr)
print("🚀 TELEGRAM BOT STARTING", file=sys.stderr)
print("="*50, file=sys.stderr)
sys.stderr.flush()

@app.route('/')
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Telegram Bot</title></head>
    <body>
        <h1>🤖 Telegram Reminder Bot</h1>
        <p>✅ <b>Работает на Railway</b></p>
        <p>⏰ <b>Расписание:</b></p>
        <ul>
            <li>{MORNING_HOUR:02d}:{MORNING_MINUTE:02d} - Утренний отчет</li>
            <li>{DAY_HOUR:02d}:{DAY_MINUTE:02d} - Фото/видео отчет</li>
            <li>{EVENING_HOUR:02d}:{EVENING_MINUTE:02d} - Вечерний отчет</li>
        </ul>
        <p><a href="/send_test">📤 Тест</a> | <a href="/health">❤️ Здоровье</a></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return "OK", 200

@app.route('/send_test')
def send_test():
    send_telegram("🔧 Тест от бота")
    return "✅ Тест отправлен!"

def send_telegram(text):
    """Простая отправка сообщения"""
    if not BOT_TOKEN or not CHAT_ID:
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except:
        return False

def send_morning():
    msg = f"""<b>⏰ УТРЕННЕЕ НАПОМИНАНИЕ</b>
    
<b>📋 НАЧАЛО РАБОЧЕГО ДНЯ</b>

Отправьте в чат:

<b>📅 Дата:
<b>🏗 Объект:
<b>👥 Сотрудники на объекте:
<b>📝 План работ:</b> (список планируемых работ на день)

⚠️ <b>За неоповещение - штраф</b>"""
    
    send_telegram(msg)

def send_day():
    msg = f"""<b>📸 ДНЕВНОЕ НАПОМИНАНИЕ</b>
    
<b>🎥 ФОТО/ВИДЕОФИКСАЦИЯ РАБОТ</b>

Отправляйте фото/видео с подписями что сделали

<b>Пример:</b>
«Откопана траншея 5 м»
«Установлено 5 фитингов»

⚠️ <b>Не забывайте фиксировать работу</b>"""
    
    send_telegram(msg)

def send_evening():
    msg = f"""<b>🌙 ВЕЧЕРНЕЕ НАПОМИНАНИЕ</b>
    
<b>✅ КОНЕЦ РАБОЧЕГО ДНЯ</b>

<b>Отправьте невыполненные работы:</b>

<b>Не выполнено (пример):</b>
1. Прокладка трубы (не хватило, заказали на [дд/мм] число)
2. Установка фитингов (не хватило, заказали на [дд/мм] число)

Или: <b>«Все работы выполнены»</b>"""
    
    send_telegram(msg)

def bot_worker():
    """Фоновый процесс с проверкой времени"""
    time.sleep(3)
    print("🤖 Бот запущен", file=sys.stderr)
    
    # Тестовое сообщение
    send_telegram("🤖 Бот запущен!")
    
    print(f"⏰ Ожидание времени: {MORNING_HOUR:02d}:{MORNING_MINUTE:02d}, {DAY_HOUR:02d}:{DAY_MINUTE:02d}, {EVENING_HOUR:02d}:{EVENING_MINUTE:02d}", file=sys.stderr)
    
    last_check = {}
    
    while True:
        now = datetime.now(pytz.timezone(TIMEZONE))
        hour = now.hour
        minute = now.minute
        
        # Проверяем утреннее время
        if hour == MORNING_HOUR and minute == MORNING_MINUTE:
            if last_check.get('morning') != now.date():
                print(f"⏰ Время утреннего отчета {hour:02d}:{minute:02d}", file=sys.stderr)
                send_morning()
                last_check['morning'] = now.date()
                time.sleep(61)  # Ждем минуту
        
        # Проверяем дневное время
        elif hour == DAY_HOUR and minute == DAY_MINUTE:
            if last_check.get('day') != now.date():
                print(f"📸 Время дневного отчета {hour:02d}:{minute:02d}", file=sys.stderr)
                send_day()
                last_check['day'] = now.date()
                time.sleep(61)
        
        # Проверяем вечернее время
        elif hour == EVENING_HOUR and minute == EVENING_MINUTE:
            if last_check.get('evening') != now.date():
                print(f"🌙 Время вечернего отчета {hour:02d}:{minute:02d}", file=sys.stderr)
                send_evening()
                last_check['evening'] = now.date()
                time.sleep(61)
        
        # Сбрасываем проверки в 00:01
        if hour == 0 and minute == 1:
            last_check = {}
            time.sleep(61)
        
        time.sleep(1)

if __name__ == "__main__":
    # Запускаем бота
    threading.Thread(target=bot_worker, daemon=True).start()
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)


