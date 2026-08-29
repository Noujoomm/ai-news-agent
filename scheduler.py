# -*- coding: utf-8 -*-
"""جدولة يومية: يرسل النشرة كل يوم في الوقت المحدد في .env (DAILY_SEND_TIME).
خلّه شغال في الخلفية:
    python scheduler.py
"""
import time

import schedule

from ai_news_agent import config
from main import run_once

print(f"🕗 الجدولة شغالة — النشرة بترسل يوميًا الساعة {config.DAILY_SEND_TIME}")
schedule.every().day.at(config.DAILY_SEND_TIME).do(run_once)

# إرسال فوري أول مرة للتأكد إن كل شي تمام (احذف السطر لو ما تبغاه)
run_once()

while True:
    schedule.run_pending()
    time.sleep(30)
