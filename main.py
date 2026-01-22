import os
import sys
import requests
from flask import Flask
import atexit
import time
import schedule
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)

# ============ НАСТРОЙКИ ============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8225982359:AAFTkgY86NgkaeMcb8SUzee-n8kws-IYMZQ")
CHAT_ID = os.environ.get("CHAT_ID", "-1003679701875")

print("="*60, file=sys.stderr)
print("🚀 TELEGRAM BOT STARTING", file=sys.stderr)
print("="*60, file=sys.stderr)
print(f"BOT_TOKEN: {'✅ SET' if BOT_TOKEN else '❌ NOT SET'}", file=sys.stderr)
print(f"CHAT_ID: {CHAT_ID if CHAT_ID else '❌ NOT SET'}", file=sys.stderr)
print(f"TIME: {datetime.now().strftime('%H:%M:%S')}", file=sys.stderr)
print("="*60, file=sys.stderr)
sys.stderr.flush()

# ============ TELEGRAM FUNCTIONS ============
def send_telegram_message(text):
    """Send message to Telegram"""
    if not BOT_TOKEN or not CHAT_ID:
        print(f"❌ ERROR: Missing BOT_TOKEN or CHAT_ID", file=sys.stderr)
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        print(f"📤 SENDING TO TELEGRAM: {text[:50]}...", file=sys.stderr)
        response = requests.post(url, data=data, timeout=30)
        
        print(f"📡 RESPONSE STATUS: {response.status_code}", file=sys.stderr)
        print(f"📡 RESPONSE BODY: {response.text[:200]}", file=sys.stderr)
        
        if response.status_code == 200:
            print("✅ MESSAGE SENT SUCCESSFULLY!", file=sys.stderr)
            return True
        else:
            print(f"❌ TELEGRAM API ERROR: {response.status_code}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"💥 EXCEPTION: {e}", file=sys.stderr)
        return False

# ============ SCHEDULED TASKS ============
def send_morning():
    print("⏰ Executing MORNING task", file=sys.stderr)
    send_telegram_message("⏰ <b>УТРЕННЕЕ НАПОМИНАНИЕ</b>\n\nОтправьте отчет о начале дня!")

def send_day():
    print("📸 Executing DAY task", file=sys.stderr)
    send_telegram_message("📸 <b>ДНЕВНОЕ НАПОМИНАНИЕ</b>\n\nОтправьте фото/видео работ!")

def send_evening():
    print("🌙 Executing EVENING task", file=sys.stderr)
    send_telegram_message("🌙 <b>ВЕЧЕРНЕЕ НАПОМИНАНИЕ</b>\n\nОтправьте отчет о конце дня!")

def send_test():
    print("🔧 Executing TEST task", file=sys.stderr)
    send_telegram_message("🤖 <b>ТЕСТОВОЕ СООБЩЕНИЕ</b>\n\nБот работает на Railway!")

# ============ FLASK ROUTES ============
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Telegram Bot</title></head>
    <body>
        <h1>🤖 Telegram Reminder Bot</h1>
        <p>Status: <span style="color: green;">✅ Running</span></p>
        <p><a href="/send_test">📤 Send Test Message Now</a></p>
        <p><a href="/health">❤️ Health Check</a></p>
        <p><a href="/schedule">⏰ View Schedule</a></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}, 200

@app.route('/send_test')
def send_test_route():
    """Manual test endpoint"""
    send_test()
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Test Sent</title></head>
    <body>
        <h1>✅ Test Message Sent!</h1>
        <p>Check your Telegram group.</p>
        <p><a href="/">← Back</a></p>
    </body>
    </html>
    """

@app.route('/schedule')
def schedule_route():
    """View current schedule"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Schedule</title></head>
    <body>
        <h1>⏰ Bot Schedule</h1>
        <p><b>Current Time:</b> {datetime.now().strftime('%H:%M:%S')}</p>
        <p><b>Configured Times:</b></p>
        <ul>
            <li>10:00 - Morning Report</li>
            <li>14:00 - Photo/Video Report</li>
            <li>19:00 - Evening Report</li>
        </ul>
        <p><a href="/">← Back</a></p>
    </body>
    </html>
    """

# ============ INITIALIZATION ============
def init_scheduler():
    """Initialize the scheduler"""
    print("⏰ INITIALIZING SCHEDULER...", file=sys.stderr)
    
    scheduler = BackgroundScheduler()
    
    # Add scheduled jobs (for testing - every 5 minutes)
    scheduler.add_job(send_morning, 'cron', hour=10, minute=0)
    scheduler.add_job(send_day, 'cron', hour=14, minute=0)
    scheduler.add_job(send_evening, 'cron', hour=19, minute=0)
    
    # Also add a test job for every 5 minutes
    scheduler.add_job(send_test, 'cron', minute='*/5')
    
    scheduler.start()
    print("✅ SCHEDULER STARTED", file=sys.stderr)
    
    # Send initial test message
    print("🔧 SENDING INITIAL TEST...", file=sys.stderr)
    send_test()
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler

# ============ MAIN ============
if __name__ == "__main__":
    # Initialize scheduler
    scheduler = init_scheduler()
    
    # Start Flask app
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 STARTING FLASK ON PORT {port}", file=sys.stderr)
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
