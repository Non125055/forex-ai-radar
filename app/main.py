from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.background import BackgroundScheduler

import requests
import os

from app.scanner import scan_markets
from app.trade_manager import update_trade_status
from app.analytics import get_analytics
from app.diagnostics import get_diagnostics

app = FastAPI()

# -----------------------------------
# CORS
# -----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# SCHEDULER
# -----------------------------------

scheduler = BackgroundScheduler()

# -----------------------------------
# AUTOMATED SCAN LOOP
# -----------------------------------

def scheduled_scan():

    print("RUNNING AUTOMATED SCAN...")

    update_trade_status()

    signals = scan_markets()

    print("SCAN COMPLETE")

    for signal in signals:

        print(
            signal["pair"],
            signal["signal"],
            signal["setup_score"]
        )

# -----------------------------------
# STARTUP
# -----------------------------------

@app.on_event("startup")
def startup_event():

    print("STARTING SCHEDULER...")

    scheduler.add_job(
        scheduled_scan,
        "interval",
        minutes=5
    )

    scheduler.start()

    print("SCHEDULER STARTED")

# -----------------------------------
# SHUTDOWN
# -----------------------------------

@app.on_event("shutdown")
def shutdown_event():

    scheduler.shutdown()

# -----------------------------------
# ROOT
# -----------------------------------

@app.get("/")
def root():

    return {
        "message": "Forex AI Radar Backend Running"
    }

# -----------------------------------
# SIGNALS
# -----------------------------------

@app.get("/signals")
def get_signals():

    return scan_markets()

# -----------------------------------
# FORCE SCAN
# -----------------------------------

@app.get("/force-scan")
def force_scan():

    print("MANUAL FORCE SCAN")

    update_trade_status()

    signals = scan_markets()

    return {
        "message": "Manual scan complete",
        "signals": signals
    }

# -----------------------------------
# ANALYTICS
# -----------------------------------

@app.get("/analytics")
def analytics():

    return get_analytics()

# -----------------------------------
# DIAGNOSTICS
# -----------------------------------

@app.get("/diagnostics")
def diagnostics():

    return get_diagnostics()

# -----------------------------------
# TELEGRAM TEST
# -----------------------------------

@app.get("/test-telegram")
def test_telegram():

    token = os.getenv(
        "TELEGRAM_BOT_TOKEN"
    )

    chat_id = os.getenv(
        "TELEGRAM_CHAT_ID"
    )

    message = (
        "🚀 Railway Telegram "
        "Test Success"
    )

    url = (
        f"https://api.telegram.org/"
        f"bot{token}/sendMessage"
    )

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": message
        }
    )

    return {

        "status_code":
            response.status_code,

        "response":
            response.text
    }