import requests
import time
import os
from datetime import datetime
import pytz
import schedule
import logging
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============ НАСТРОЙКИ ============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8225982359:AAFTkgY86NgkaeMcb8SUzee-n8kws-IYMZQ")
CHAT_ID = os.environ.get("CHAT_ID", "-1003679701875")
TIMEZONE = "Europe/Moscow"

# ⚠️ ДЛЯ ТЕСТА - через 1,2,3 минуты
MORNING_HOUR = 16      # текущий час
MORNING_MINUTE = 8     # через 1 минуту

DAY_HOUR = 16
DAY_MINUTE = 9         # через 2 минуты

EVENING_HOUR = 16
EVENING_MINUTE = 10    # через 3 минуты
# ===================================

def get_current_time():
    tz = pytz.timezone(TIMEZONE)
    return datetime.now(tz)

def send_telegram_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("❌ BOT_TOKEN или CHAT_ID не установлены")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        logger.info(f"📤 Отправка сообщения в Telegram...")
        response = requests.post(url, data=data, timeout=30)
        
        if response.status_code == 200:
            logger.info("✅ Сообщение отправлено успешно!")
            return True
        else:
            logger.error(f"❌ Ошибка {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"💥 Ошибка при отправке: {e}")
        return False

def morning():
    logger.info("Отправка утреннего напоминания")
    current_time = get_current_time()
    msg = f"""<b>⏰ УТРЕННЕЕ НАПОМИНАНИЕ</b>

<b>📋 НАЧАЛО РАБОЧЕГО ДНЯ</b>

Отправьте в чат:
<b>📅 Дата:</b> {current_time.strftime('%d.%m.%Y')}
<b>🏗 Объект:</b> (где работаете)
<b>👥 Сотрудники:</b> (список на объекте)
<b>📝 План работ:</b> (что будете делать)

⚠️ <b>За неоповещение - штраф</b>"""
    return send_telegram_message(msg)

def day():
    logger.info("Отправка дневного напоминания")
    msg = f"""<b>📸 ДНЕВНОЕ НАПОМИНАНИЕ</b>

<b>🎥 ФОТО/ВИДЕОФИКСАЦИЯ РАБОТ</b>

Отправляйте фото/видео с подписями

<b>Пример:</b>
«Откопана траншея 5 м»
«Установлено 5 фитингов»

⚠️ <b>Не забывайте фиксировать работу!</b>"""
    return send_telegram_message(msg)

def evening():
    logger.info("Отправка вечернего напоминания")
    msg = f"""<b>🌙 ВЕЧЕРНЕЕ НАПОМИНАНИЕ</b>

<b>✅ КОНЕЦ РАБОЧЕГО ДНЯ</b>

<b>Отправьте невыполненные работы:</b>

<b>Пример:</b>
Не выполнено:
1. Прокладка трубы (не хватило материалов)
2. Установка фитингов (не было в наличии)

Или: <b>«Все работы выполнены»</b>

⚠️ <b>Отчет должен быть сдан до вечера!</b>"""
    return send_telegram_message(msg)

def test():
    logger.info("Отправка тестового сообщения")
    current_time = get_current_time()
    msg = f"""<b>БОТ ЗАПУЩЕН!</b>

✅ <b>Работает на Railway!</b>

📅 <b>Дата:</b> {current_time.strftime('%d.%m.%Y')}
⏰ <b>Время:</b> {current_time.strftime('%H:%M:%S')}
🌍 <b>Часовой пояс:</b> {TIMEZONE}

⚡ <b>Тестовое сообщение</b>"""
    return send_telegram_message(msg)

def main():
    logger.info("="*50)
    logger.info("ЗАПУСК TELEGRAM БОТА")
    logger.info("="*50)
    
    # Проверка настроек
    logger.info(f"BOT_TOKEN: {'✅ Установлен' if BOT_TOKEN else '❌ Нет'}")
    logger.info(f"CHAT_ID: {'✅ Установлен' if CHAT_ID else '❌ Нет'}")
    
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("❌ ОШИБКА: Добавьте BOT_TOKEN и CHAT_ID в Railway Variables!")
        return
    
    # Тестовое сообщение
    logger.info("📤 Отправляю тестовое сообщение...")
    test()
    
    # Настройка расписания
    logger.info("⏰ Настройка расписания...")
    schedule.every().day.at(f"{MORNING_HOUR:02d}:{MORNING_MINUTE:02d}").do(morning)
    schedule.every().day.at(f"{DAY_HOUR:02d}:{DAY_MINUTE:02d}").do(day)
    schedule.every().day.at(f"{EVENING_HOUR:02d}:{EVENING_MINUTE:02d}").do(evening)
    
    logger.info(f"✅ Расписание:")
    logger.info(f"   • {MORNING_HOUR:02d}:{MORNING_MINUTE:02d} - Утренний отчет")
    logger.info(f"   • {DAY_HOUR:02d}:{DAY_MINUTE:02d} - Фото/видео")
    logger.info(f"   • {EVENING_HOUR:02d}:{EVENING_MINUTE:02d} - Вечерний отчет")
    
    logger.info("✅ Бот запущен и работает!")
    logger.info("="*50)
    
    # Основной цикл
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()

