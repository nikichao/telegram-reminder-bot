import requests
import time
import os
import sys
from datetime import datetime
import pytz
from flask import Flask
import threading
import schedule

app = Flask(__name__)

# Настройка логирования
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============ НАСТРОЙКИ ============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")
TIMEZONE = "Europe/Moscow"

# ⚠️ ДЛЯ ТЕСТА - установите ближайшее время
current_time = datetime.now().strftime('%H:%M')
hour = int(current_time.split(':')[0])
minute = int(current_time.split(':')[1])

MORNING_HOUR = hour
MORNING_MINUTE = minute + 1  # через 1 минуту

DAY_HOUR = hour  
DAY_MINUTE = minute + 2      # через 2 минуты

EVENING_HOUR = hour
EVENING_MINUTE = minute + 3  # через 3 минуты
# ===================================

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Telegram Bot</title></head>
    <body>
        <h1>🤖 Telegram Bot</h1>
        <p>Статус: <span style="color: green;">✅ Работает</span></p>
        <p><a href="/send_test">📤 Отправить тестовое сообщение</a></p>
        <p><a href="/check_config">⚙️ Проверить настройки</a></p>
        <p><a href="/health">❤️ Health Check</a></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "healthy", "time": datetime.now().isoformat()}, 200

@app.route('/send_test')
def send_test():
    """Ручная отправка тестового сообщения"""
    logger.info("Запрос на отправку тестового сообщения")
    result = test()
    if result:
        return "✅ Тестовое сообщение отправлено в Telegram!"
    else:
        return "❌ Не удалось отправить сообщение. Проверьте логи."

@app.route('/check_config')
def check_config():
    """Проверка конфигурации"""
    config_info = {
        "bot_token_set": bool(BOT_TOKEN),
        "bot_token_length": len(BOT_TOKEN) if BOT_TOKEN else 0,
        "chat_id_set": bool(CHAT_ID),
        "chat_id": CHAT_ID,
        "timezone": TIMEZONE,
        "morning_time": f"{MORNING_HOUR:02d}:{MORNING_MINUTE:02d}",
        "day_time": f"{DAY_HOUR:02d}:{DAY_MINUTE:02d}",
        "evening_time": f"{EVENING_HOUR:02d}:{EVENING_MINUTE:02d}",
        "current_time": datetime.now().strftime('%H:%M:%S')
    }
    
    # Проверка токена через Telegram API
    if BOT_TOKEN:
        try:
            response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=10)
            config_info["bot_api_check"] = response.status_code
            config_info["bot_info"] = response.json() if response.status_code == 200 else "Ошибка"
        except Exception as e:
            config_info["bot_api_check"] = f"Ошибка: {e}"
    
    return config_info

def get_current_time():
    tz = pytz.timezone(TIMEZONE)
    return datetime.now(tz)

def send_telegram_message(text):
    """Отправляет сообщение в Telegram с подробным логированием"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не установлен")
        return False
    if not CHAT_ID:
        logger.error("❌ CHAT_ID не установлен")
        return False
    
    logger.info(f"Отправка сообщения в Telegram. Длина текста: {len(text)} символов")
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        logger.info(f"Отправка запроса к Telegram API. URL: {url.split('/bot')[0]}/bot***")
        response = requests.post(url, data=data, timeout=30)
        current_time = get_current_time().strftime('%H:%M:%S')
        
        if response.status_code == 200:
            logger.info(f"[{current_time}] ✅ Сообщение успешно отправлено")
            return True
        else:
            logger.error(f"[{current_time}] ❌ Ошибка Telegram API: {response.status_code}")
            logger.error(f"Ответ сервера: {response.text}")
            return False
    except requests.exceptions.Timeout:
        logger.error("⏰ Таймаут при отправке сообщения")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("🔌 Ошибка соединения с Telegram")
        return False
    except Exception as e:
        logger.error(f"💥 Неожиданная ошибка: {e}")
        return False

def morning():
    logger.info("Отправка утреннего напоминания")
    current_time = get_current_time()
    msg = f"""<b>⏰ УТРЕННЕЕ НАПОМИНАНИЕ ({MORNING_HOUR:02d}:{MORNING_MINUTE:02d})</b>

<b>📋 НАЧАЛО РАБОЧЕГО ДНЯ</b>
📅 Дата: {current_time.strftime('%d.%m.%Y')}

Отправьте в чат:
<b>🏗 Объект:</b> (где работаете)
<b>👥 Сотрудники на объекте:</b> (список)
<b>📝 План работ:</b> (что будете делать сегодня)

⚠️ <b>За неоповещение - штрафные санкции</b>"""
    return send_telegram_message(msg)

def day():
    logger.info("Отправка дневного напоминания")
    msg = f"""<b>📸 ДНЕВНОЕ НАПОМИНАНИЕ ({DAY_HOUR:02d}:{DAY_MINUTE:02d})</b>

<b>🎥 ФОТО/ВИДЕОФИКСАЦИЯ РАБОТ</b>

Отправляйте фото/видео с подписями что сделали

<b>Пример:</b>
«Откопана траншея 5 м»
«Установлено 5 фитингов»

⚠️ <b>Не забывайте фиксировать работу!</b>"""
    return send_telegram_message(msg)

def evening():
    logger.info("Отправка вечернего напоминания")
    msg = f"""<b>🌙 ВЕЧЕРНЕЕ НАПОМИНАНИЕ ({EVENING_HOUR:02d}:{EVENING_MINUTE:02d})</b>

<b>✅ КОНЕЦ РАБОЧЕГО ДНЯ</b>

<b>Отправьте невыполненные работы:</b>

<b>Пример:</b>
Не выполнено:
1. Прокладка трубы (не хватило материалов)
2. Установка фитингов (не было в наличии)

Или: <b>«Все работы выполнены»</b>

⚠️ <b>Отчет должен быть сдан до {EVENING_HOUR:02d}:{EVENING_MINUTE+30:02d}!</b>"""
    return send_telegram_message(msg)

def test():
    logger.info("Отправка тестового сообщения")
    current_time = get_current_time()
    msg = f"""<b>🤖 ТЕСТОВОЕ СООБЩЕНИЕ</b>

✅ <b>Бот запущен и работает!</b>

📅 <b>Дата:</b> {current_time.strftime('%d.%m.%Y')}
⏰ <b>Время:</b> {current_time.strftime('%H:%M:%S')}
🌍 <b>Часовой пояс:</b> {TIMEZONE}

⚡ <b>Расписание напоминаний:</b>
• {MORNING_HOUR:02d}:{MORNING_MINUTE:02d} - Утренний отчет
• {DAY_HOUR:02d}:{DAY_MINUTE:02d} - Фото/видео отчет  
• {EVENING_HOUR:02d}:{EVENING_MINUTE:02d} - Вечерний отчет

💬 <b>Это тестовое сообщение от бота.</b>"""
    return send_telegram_message(msg)

def setup_schedule():
    """Настраивает расписание"""
    logger.info("Настройка расписания...")
    
    schedule.every().day.at(f"{MORNING_HOUR:02d}:{MORNING_MINUTE:02d}").do(morning)
    schedule.every().day.at(f"{DAY_HOUR:02d}:{DAY_MINUTE:02d}").do(day)
    schedule.every().day.at(f"{EVENING_HOUR:02d}:{EVENING_MINUTE:02d}").do(evening)
    
    logger.info(f"⏰ Расписание настроено:")
    logger.info(f"   • {MORNING_HOUR:02d}:{MORNING_MINUTE:02d} - Утренний отчет")
    logger.info(f"   • {DAY_HOUR:02d}:{DAY_MINUTE:02d} - Фото/видео")
    logger.info(f"   • {EVENING_HOUR:02d}:{EVENING_MINUTE:02d} - Вечерний отчет")

def start_bot():
    """Основная функция бота"""
    logger.info("="*50)
    logger.info("🤖 ЗАПУСК TELEGRAM БОТА")
    logger.info("="*50)
    
    # Проверка конфигурации
    logger.info(f"BOT_TOKEN установлен: {'✅' if BOT_TOKEN else '❌'}")
    logger.info(f"CHAT_ID установлен: {'✅' if CHAT_ID else '❌'}")
    
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("❌ ОШИБКА: Не установлены BOT_TOKEN или CHAT_ID!")
        logger.error("Добавьте в Railway Variables:")
        logger.error("  BOT_TOKEN = ваш_токен")
        logger.error("  CHAT_ID = ваш_chat_id")
        return
    
    # Отправка тестового сообщения
    logger.info("📤 Отправка тестового сообщения...")
    test_result = test()
    
    if test_result:
        logger.info("✅ Тестовое сообщение отправлено успешно")
    else:
        logger.error("❌ Не удалось отправить тестовое сообщение")
    
    # Настройка расписания
    setup_schedule()
    
    logger.info("✅ Бот запущен и работает")
    logger.info("⏰ Ожидание времени для отправки напоминаний...")
    logger.info("="*50)
    
    # Основной цикл
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Ошибка в основном цикле: {e}")
            time.sleep(60)

def run_flask():
    """Запуск Flask сервера"""
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🌐 Запуск Flask сервера на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask сервер в основном потоке
    run_flask()
