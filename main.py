#!/usr/bin/env python3
import os
import sys
import requests
import time
from datetime import datetime, timedelta
import pytz
from flask import Flask
import threading
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ============ НАСТРОЙКИ ============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8225982359:AAFTkgY86NgkaeMcb8SUzee-n8kws-IYMZQ")
CHAT_ID = os.environ.get("CHAT_ID", "-1003679701875")
TIMEZONE = "Europe/Moscow"

# ⚠️ УСТАНОВИТЕ ВРЕМЯ НАПОМИНАНИЙ
MORNING_HOUR = 10      
MORNING_MINUTE = 0

EVENING_HOUR = 19     
EVENING_MINUTE = 0
# ===================================

print("="*50, file=sys.stderr)
print("🚀 TELEGRAM BOT STARTING", file=sys.stderr)
print(f"⏰ Время напоминаний: {MORNING_HOUR:02d}:{MORNING_MINUTE:02d}, {EVENING_HOUR:02d}:{EVENING_MINUTE:02d}", file=sys.stderr)
print(f"🌍 Часовой пояс: {TIMEZONE}", file=sys.stderr)
print("="*50, file=sys.stderr)
sys.stderr.flush()

@app.route('/')
def home():
    now = datetime.now(pytz.timezone(TIMEZONE))
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Telegram Bot</title></head>
    <body>
        <h1>🤖 Telegram Reminder Bot</h1>
        <p>✅ <b>Работает на Railway</b></p>
        <p>⏰ <b>Текущее время ({TIMEZONE}): {now.strftime('%H:%M:%S')}</b></p>
        <p>📅 <b>Расписание:</b></p>
        <ul>
            <li>{MORNING_HOUR:02d}:{MORNING_MINUTE:02d} - Утренний отчет</li>
            <li>{EVENING_HOUR:02d}:{EVENING_MINUTE:02d} - Вечерний отчет</li>
        </ul>
        <p><a href="/send_test">📤 Тест</a> | <a href="/health">❤️ Здоровье</a> | <a href="/status">📊 Статус</a></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return "OK", 200

@app.route('/status')
def status():
    now = datetime.now(pytz.timezone(TIMEZONE))
    return {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": TIMEZONE,
        "schedule": {
            "morning": f"{MORNING_HOUR:02d}:{MORNING_MINUTE:02d}",
            "evening": f"{EVENING_HOUR:02d}:{EVENING_MINUTE:02d}"
        }
    }

@app.route('/send_test')
def send_test():
    send_telegram("🔧 Тест от бота")
    return "✅ Тест отправлен!"

@app.route('/send_morning')
def send_morning_manual():
    send_morning()
    return "✅ Утреннее напоминание отправлено!"

def send_telegram(text):
    """Простая отправка сообщения"""
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("❌ BOT_TOKEN или CHAT_ID не настроены")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Сообщение отправлено: {text[:50]}...")
            return True
        else:
            logger.error(f"❌ Ошибка Telegram API: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка отправки: {e}")
        return False

def send_morning():
    msg = f"""<b>⏰ УТРЕННЕЕ НАПОМИНАНИЕ</b>
    
<b>📋 НАЧАЛО РАБОЧЕГО ДНЯ</b>

Отправьте в чат:

<b>📅 Дата:</b>
<b>🏗 Объект:</b>
<b>👥 Сотрудники на объекте:</b>
<b>📝 План работ:</b> (список планируемых работ на день)

⚠️ <b>За неоповещение - штраф</b>"""
    
    return send_telegram(msg)

def send_evening():
    msg = f"""<b>🌙 ВЕЧЕРНЕЕ НАПОМИНАНИЕ</b>
    
<b>✅ КОНЕЦ РАБОЧЕГО ДНЯ</b>

<b>Отправьте невыполненные работы:</b>

<b>Не выполнено (пример):</b>
1. Прокладка трубы (не хватило, заказали на [дд/мм] число)
2. Установка фитингов (не хватило, заказали на [дд/мм] число)

Или: <b>«Все работы выполнены»</b>

⚠️ <b>За неоповещение - штраф</b>"""

    return send_telegram(msg)

def bot_worker():
    """Улучшенный фоновый процесс с проверкой времени"""
    time.sleep(3)
    logger.info("🤖 Бот запущен")
    
    # Тестовое сообщение
    send_telegram(f"🤖 Бот запущен!\n⏰ Часовой пояс: {TIMEZONE}\n📅 Расписание:\n• {MORNING_HOUR:02d}:{MORNING_MINUTE:02d} - Утренний\n• {EVENING_HOUR:02d}:{EVENING_MINUTE:02d} - Вечерний")
    
    last_check = {}
    
    while True:
        try:
            now = datetime.now(pytz.timezone(TIMEZONE))
            hour = now.hour
            minute = now.minute
            today = now.date()
            
            # Логируем текущее время раз в минуту для отладки
            if minute % 10 == 0:  # Каждые 10 минут
                logger.info(f"⏰ Текущее время: {hour:02d}:{minute:02d}")
            
            # Проверяем утреннее время
            morning_key = f"morning_{today}"
            if hour == MORNING_HOUR and minute == MORNING_MINUTE:
                if last_check.get(morning_key) != True:
                    logger.info(f"⏰ Отправляю утренний отчет {hour:02d}:{minute:02d}")
                    if send_morning():
                        last_check[morning_key] = True
                        logger.info("✅ Утренний отчет отправлен")
                    time.sleep(60)  # Ждем минуту чтобы не отправить повторно
            
            # Проверяем вечернее время
            evening_key = f"evening_{today}"
            if hour == EVENING_HOUR and minute == EVENING_MINUTE:
                if last_check.get(evening_key) != True:
                    logger.info(f"🌙 Отправляю вечерний отчет {hour:02d}:{minute:02d}")
                    if send_evening():
                        last_check[evening_key] = True
                        logger.info("✅ Вечерний отчет отправлен")
                    time.sleep(60)
            
            # Сбрасываем проверки в 00:01
            if hour == 0 and minute == 1:
                last_check = {}
                logger.info("🔄 Сброс отметок о отправке")
                time.sleep(60)
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"❌ Ошибка в боте: {e}")
            time.sleep(10)

if __name__ == "__main__":
    # Запускаем бота
    bot_thread = threading.Thread(target=bot_worker, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 Запуск Flask на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
