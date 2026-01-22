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

# ⚠️ УСТАНОВИТЕ ВРЕМЯ НАПОМИНАНИЙ
MORNING_HOUR = 9      # 9:01 утра
MORNING_MINUTE = 1

DAY_HOUR = 14         # 14:01 дня
DAY_MINUTE = 1

EVENING_HOUR = 19     # 19:01 вечера
EVENING_MINUTE = 1
# ===================================

# Принудительный вывод в логи
print("="*50, file=sys.stderr)
print("🚀 ПРИЛОЖЕНИЕ ЗАПУСКАЕТСЯ", file=sys.stderr)
print(f"Токен: {'✅' if BOT_TOKEN else '❌'}", file=sys.stderr)
print(f"Chat ID: {'✅' if CHAT_ID else '❌'}", file=sys.stderr)
print(f"Часовой пояс: {TIMEZONE}", file=sys.stderr)
print(f"Расписание: {MORNING_HOUR:02d}:{MORNING_MINUTE:02d}, {DAY_HOUR:02d}:{DAY_MINUTE:02d}, {EVENING_HOUR:02d}:{EVENING_MINUTE:02d}", file=sys.stderr)
print("="*50, file=sys.stderr)
sys.stderr.flush()

@app.route('/')
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Telegram Reminder Bot</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .status {{ background: #4CAF50; color: white; padding: 10px; border-radius: 5px; }}
            .schedule {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .btn {{ display: inline-block; background: #2196F3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; }}
        </style>
    </head>
    <body>
        <h1>🤖 Telegram Reminder Bot</h1>
        
        <div class="status">
            ✅ Статус: <b>Работает на Railway</b>
        </div>
        
        <div class="schedule">
            <h3>⏰ Расписание напоминаний:</h3>
            <ul>
                <li><b>{MORNING_HOUR:02d}:{MORNING_MINUTE:02d}</b> - Утренний отчет</li>
                <li><b>{DAY_HOUR:02d}:{DAY_MINUTE:02d}</b> - Фото/видео отчет</li>
                <li><b>{EVENING_HOUR:02d}:{EVENING_MINUTE:02d}</b> - Вечерний отчет</li>
            </ul>
            
            <p><b>Часовой пояс:</b> {TIMEZONE}</p>
            <p><b>Текущее время:</b> {datetime.now(pytz.timezone(TIMEZONE)).strftime('%H:%M:%S')}</p>
        </div>
        
        <p>
            <a class="btn" href="/send_test">📤 Отправить тестовое сообщение</a>
            <a class="btn" href="/send_morning_now">⏰ Отправить утреннее напоминание сейчас</a>
            <a class="btn" href="/health">❤️ Проверить здоровье системы</a>
        </p>
        
        <p><b>Инструкция для сотрудников:</b></p>
        <ul>
            <li>В <b>{MORNING_HOUR:02d}:{MORNING_MINUTE:02d}</b> - отправьте отчет о начале дня</li>
            <li>В <b>{DAY_HOUR:02d}:{DAY_MINUTE:02d}</b> - отправьте фото/видео работ</li>
            <li>В <b>{EVENING_HOUR:02d}:{EVENING_MINUTE:02d}</b> - отправьте отчет о конце дня</li>
        </ul>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}, 200

@app.route('/send_test')
def send_test():
    """Отправить тестовое сообщение"""
    result = send_telegram_message("🔧 Тестовое сообщение от бота на Railway!")
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Тест отправлен</title></head>
    <body>
        <h1>✅ Тестовое сообщение отправлено!</h1>
        <p>Проверьте Telegram группу.</p>
        <p><a href="/">← Назад</a></p>
    </body>
    </html>
    """

@app.route('/send_morning_now')
def send_morning_now():
    """Отправить утреннее напоминание сейчас"""
    send_morning()
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Напоминание отправлено</title></head>
    <body>
        <h1>⏰ Утреннее напоминание отправлено!</h1>
        <p>Проверьте Telegram группу.</p>
        <p><a href="/">← Назад</a></p>
    </body>
    </html>
    """

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
            print(f"❌ Ошибка {response.status_code}: {response.text[:100]}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"💥 Ошибка при отправке: {e}", file=sys.stderr)
        return False

def send_morning():
    current_time = datetime.now(pytz.timezone(TIMEZONE))
    print(f"⏰ Отправляю утреннее напоминание...", file=sys.stderr)
    msg = f"""<b>⏰ УТРЕННЕЕ НАПОМИНАНИЕ ({MORNING_HOUR:02d}:{MORNING_MINUTE:02d})</b>

<b>📋 НАЧАЛО РАБОЧЕГО ДНЯ</b>
📅 <b>Дата:</b> {current_time.strftime('%d.%m.%Y')}

<b>Отправьте в чат:</b>
🏗 <b>Объект:</b> (где работаете)
👥 <b>Сотрудники:</b> (список на объекте)
📝 <b>План работ:</b> (что будете делать сегодня)

⚠️ <b>За неоповещение - штрафные санкции</b>"""
    return send_telegram_message(msg)

def send_day():
    current_time = datetime.now(pytz.timezone(TIMEZONE))
    print(f"📸 Отправляю дневное напоминание...", file=sys.stderr)
    msg = f"""<b>📸 ДНЕВНОЕ НАПОМИНАНИЕ ({DAY_HOUR:02d}:{DAY_MINUTE:02d})</b>

<b>🎥 ФОТО/ВИДЕОФИКСАЦИЯ ВЫПОЛНЕННЫХ РАБОТ</b>
📅 <b>Дата:</b> {current_time.strftime('%d.%m.%Y')}

<b>Отправляйте в чат:</b>
• Фото выполненных работ
• Видео процесса работы
• С подписью что сделано

<b>Пример подписи:</b>
«Смонтирована электропроводка в комнате 3»
«Установлено 5 розеток в коридоре»

⚠️ <b>Фиксируйте каждую крупную выполненную работу!</b>"""
    return send_telegram_message(msg)

def send_evening():
    current_time = datetime.now(pytz.timezone(TIMEZONE))
    print(f"🌙 Отправляю вечернее напоминание...", file=sys.stderr)
    msg = f"""<b>🌙 ВЕЧЕРНЕЕ НАПОМИНАНИЕ ({EVENING_HOUR:02d}:{EVENING_MINUTE:02d})</b>

<b>✅ КОНЕЦ РАБОЧЕГО ДНЯ</b>
📅 <b>Дата:</b> {current_time.strftime('%d.%m.%Y')}

<b>Отправьте невыполненные работы:</b>

<b>📋 Пример отчета:</b>
«Не выполнено:
1. Прокладка кабеля в комнате 4 (не завезли материалы)
2. Установка 2-х выключателей (не было в наличии)»

<b>Или:</b>
«✅ Все работы выполнены по плану»

⚠️ <b>Отчет должен быть сдан до {EVENING_HOUR:02d}:{EVENING_MINUTE+30:02d}!</b>"""
    return send_telegram_message(msg)

def send_test_message():
    current_time = datetime.now(pytz.timezone(TIMEZONE))
    print(f"🔧 Отправляю тестовое сообщение...", file=sys.stderr)
    msg = f"""<b>🤖 БОТ ЗАПУЩЕН НА RAILWAY!</b>

✅ <b>Система работает исправно</b>

📅 <b>Дата:</b> {current_time.strftime('%d.%m.%Y')}
⏰ <b>Время:</b> {current_time.strftime('%H:%M:%S')}
🌍 <b>Часовой пояс:</b> {TIMEZONE}

⚡ <b>Расписание напоминаний:</b>
• {MORNING_HOUR:02d}:{MORNING_MINUTE:02d} - Утренний отчет
• {DAY_HOUR:02d}:{DAY_MINUTE:02d} - Фото/видео отчет
• {EVENING_HOUR:02d}:{EVENING_MINUTE:02d} - Вечерний отчет

💬 <b>Это тестовое сообщение для проверки связи</b>"""
    return send_telegram_message(msg)

def start_bot():
    """Запуск бота в фоновом режиме"""
    print("🤖 ЗАПУСКАЮ ТЕЛЕГРАМ БОТА...", file=sys.stderr)
    sys.stderr.flush()
    
    # Проверка конфигурации
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ ОШИБКА: Не настроены BOT_TOKEN или CHAT_ID!", file=sys.stderr)
        return
    
    # Отправка тестового сообщения
    time.sleep(3)  # Ждем запуска Flask
    print("📤 Отправляю тестовое сообщение при запуске...", file=sys.stderr)
    send_test_message()
    
    # Настройка расписания
    print(f"⏰ Настраиваю расписание...", file=sys.stderr)
    schedule.every().day.at(f"{MORNING_HOUR:02d}:{MORNING_MINUTE:02d}").do(send_morning)
    schedule.every().day.at(f"{DAY_HOUR:02d}:{DAY_MINUTE:02d}").do(send_day)
    schedule.every().day.at(f"{EVENING_HOUR:02d}:{EVENING_MINUTE:02d}").do(send_evening)
    
    print(f"✅ Расписание настроено:", file=sys.stderr)
    print(f"   • {MORNING_HOUR:02d}:{MORNING_MINUTE:02d} - Утренний отчет", file=sys.stderr)
    print(f"   • {DAY_HOUR:02d}:{DAY_MINUTE:02d} - Фото/видео отчет", file=sys.stderr)
    print(f"   • {EVENING_HOUR:02d}:{EVENING_MINUTE:02d} - Вечерний отчет", file=sys.stderr)
    print("✅ Бот запущен и работает!", file=sys.stderr)
    sys.stderr.flush()
    
    # Бесконечный цикл
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Ошибка в основном цикле: {e}", file=sys.stderr)
            time.sleep(60)

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask сервер
    print(f"🌐 Запускаю Flask сервер...", file=sys.stderr)
    sys.stderr.flush()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
