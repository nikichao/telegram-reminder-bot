import requests
import time
import os
from datetime import datetime
import pytz
from flask import Flask
import threading

# ============ НАСТРОЙКИ ============
# Для Railway лучше использовать переменные окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8225982359:AAFTkgY86NgkaeMcb8SUzee-n8kws-IYMZQ")
CHAT_ID = os.environ.get("CHAT_ID", "-1003679701875")
TIMEZONE = "Europe/Moscow"

# ⚠️ ИЗМЕНИ ВРЕМЯ ЗДЕСЬ ⚠️
MORNING_HOUR = 15
MORNING_MINUTE = 0
DAY_HOUR = 15
DAY_MINUTE = 2
EVENING_HOUR = 15
EVENING_MINUTE = 4
# ===================================

# Flask приложение ДОЛЖНО быть создано ДО функций
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram Bot работает на Railway!"

@app.route('/health')
def health():
    return "OK", 200

@app.route('/test_bot')
def test_bot():
    test()
    return "Тестовое сообщение отправлено"

def get_current_time():
    """Получает текущее время с учетом часового пояса"""
    tz = pytz.timezone(TIMEZONE)
    return datetime.now(tz)

def send_msg(text):
    """Отправляет сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, data=data, timeout=10)
        if r.status_code == 200:
            current_time = get_current_time()
            print(f"[{current_time.strftime('%H:%M:%S')}] ✅ Сообщение отправлено")
            return True
        else:
            print(f"[{get_current_time().strftime('%H:%M:%S')}] ❌ Ошибка: {r.status_code}")
            print(f"Ответ сервера: {r.text}")
            return False
    except Exception as e:
        print(f"[{get_current_time().strftime('%H:%M:%S')}] ❌ Ошибка: {e}")
        return False

def morning():
    current_time = get_current_time()
    msg = f"""<b>⏰ УТРЕННЕЕ НАПОМИНАНИЕ</b>

<b>📋 НАЧАЛО РАБОЧЕГО ДНЯ</b>

Отправьте в чат:

<b>📅 Дата:
<b>🏗 Объект:
<b>👥 Сотрудники на объекте:
<b>📝 План работ:</b> (список планируемых работ на день)

⚠️ <b>За неоповещение - штраф</b>"""
    send_msg(msg)

def day():
    msg = f"""<b>📸 ДНЕВНОЕ НАПОМИНАНИЕ</b>

<b>🎥 ФОТО/ВИДЕОФИКСАЦИЯ РАБОТ</b>

Отправляйте фото/видео с подписями что сделали

<b>Пример:</b>
«Откопана траншея 5 м»
«Установлено 5 фитингов»

⚠️ <b>Не забывайте фиксировать работу</b>"""
    send_msg(msg)

def evening():
    msg = f"""<b>🌙 ВЕЧЕРНЕЕ НАПОМИНАНИЕ</b>

<b>✅ КОНЕЦ РАБОЧЕГО ДНЯ</b>

<b>Отправьте невыполненные работы:</b>

<b>Не выполнено (пример):</b>
1. Прокладка трубы (не хватило, заказали на [дд/мм] число)
2. Установка фитингов (не хватило, заказали на [дд/мм] число)

Или: <b>«Все работы выполнены»</b>

⚠️ <b>До {EVENING_HOUR:02d}:{EVENING_MINUTE+30:02d} отчет должен быть сдан!</b>"""
    send_msg(msg)

def test():
    current_time = get_current_time()
    msg = f"""<b>🤖 БОТ ЗАПУЩЕН!</b>

✅ <b>Напоминания будут:</b>
• {MORNING_HOUR:02d}:{MORNING_MINUTE:02d} - Утренний отчет
• {DAY_HOUR:02d}:{DAY_MINUTE:02d} - Фото/видео
• {EVENING_HOUR:02d}:{EVENING_MINUTE:02d} - Вечерний отчет

📅 <b>Сегодня:</b> {current_time.strftime('%d.%m.%Y')}
⏰ <b>Запуск:</b> {current_time.strftime('%H:%M:%S')}
🌍 <b>Часовой пояс:</b> {TIMEZONE}"""
    send_msg(msg)

def bot_main():
    """Основная функция бота"""
    print("="*50)
    print("🤖 ЗАПУСК БОТА НАПОМИНАНИЙ")
    print("="*50)
    
    current_time = get_current_time()
    print(f"🕐 Текущее время: {current_time.strftime('%H:%M:%S %d.%m.%Y')}")
    print(f"🌍 Часовой пояс: {TIMEZONE}")
    print(f"⏰ Расписание напоминаний:")
    print(f"   • {MORNING_HOUR:02d}:{MORNING_MINUTE:02d} - Утренний отчет")
    print(f"   • {DAY_HOUR:02d}:{DAY_MINUTE:02d} - Фото/видео отчет")
    print(f"   • {EVENING_HOUR:02d}:{EVENING_MINUTE:02d} - Вечерний отчет")
    print("="*50)
    
    # Проверка настроек
    if not BOT_TOKEN or not CHAT_ID:
        print("\n❌ ОШИБКА: Не указан BOT_TOKEN или CHAT_ID!")
        return
    
    print("\n📤 Отправляю тестовое сообщение...")
    test()
    
    print("\n✅ Бот запущен!")
    print(f"⏰ Следующее напоминание в {MORNING_HOUR:02d}:{MORNING_MINUTE:02d}")
    print("\n⛔ Для остановки бота остановите сервер")
    print("="*50)
    
    # Главный цикл
    last_minute = -1
    while True:
        now = get_current_time()
        hour = now.hour
        minute = now.minute
        
        # Утреннее
        if hour == MORNING_HOUR and minute == MORNING_MINUTE:
            print(f"\n[{now.strftime('%H:%M:%S')}] 📤 Отправляю утреннее напоминание...")
            morning()
            time.sleep(61)
        
        # Дневное
        elif hour == DAY_HOUR and minute == DAY_MINUTE:
            print(f"\n[{now.strftime('%H:%M:%S')}] 📤 Отправляю дневное напоминание...")
            day()
            time.sleep(61)
        
        # Вечернее
        elif hour == EVENING_HOUR and minute == EVENING_MINUTE:
            print(f"\n[{now.strftime('%H:%M:%S')}] 📤 Отправляю вечернее напоминание...")
            evening()
            time.sleep(61)
        
        # Выводим статус каждую минуту
        if minute != last_minute:
            print(f"[{now.strftime('%H:%M:%S')}] ⏳ Бот работает...")
            last_minute = minute
        
        time.sleep(1)

def run_flask():
    """Запускает Flask сервер"""
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Flask сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    print("🚀 Запуск Telegram бота...")
    
    # Проверяем и устанавливаем библиотеки если нужно
    try:
        import pytz
    except ImportError:
        print("📦 Установка библиотек...")
        import subprocess
        subprocess.check_call(["pip", "install", "pytz", "flask"])
        import pytz
        from flask import Flask
    
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=bot_main, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask сервер (основной поток)
    run_flask()
