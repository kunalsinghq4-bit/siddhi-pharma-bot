import os
import requests
from datetime import date, datetime, timedelta
from supabase import create_client

# ── CONFIG ──
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://kidmjxrkdcrpipdazosg.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtpZG1qeHJrZGNycGlwZGF6b3NnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ5NDE5NzksImV4cCI6MjA5MDUxNzk3OX0.IaMrF-MBMLQSlEoXDfRLd2KlpOvou_EcJwOTQuLj9lk")
FONNTE_TOKEN = os.environ.get("FONNTE_TOKEN", "zopJo8kdFTmQTVrcRbF5")

# ── INIT SUPABASE ──
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

def build_message(customer):
    if customer.get("custom_message"):
        return customer["custom_message"]
    name = customer["name"]
    medicine = customer.get("medicine") or "dawai"
    days = customer.get("reminder_days", 8)
    return (
        f"Namaste {name} ji! 🙏\n\n"
        f"Yeh *Siddhi Pharma, Patna* ki taraf se message hai. 💊\n\n"
        f"Aapki *{medicine}* ka stock khatam hone wala hai — "
        f"order kiye *{days} din* ho gaye hain!\n\n"
        f"Dose mat chhodein — abhi reorder karein! 🔔\n\n"
        f"➡️ Bas reply karein *\"ORDER\"* ya call karein:\n"
        f"📞 *099421 99901*\n"
        f"🚚 Ghar tak delivery — bilkul free!\n\n"
        f"— Siddhi Pharma | GM Road, Patna"
    )

def send_whatsapp(phone, message):
    phone = "".join(filter(str.isdigit, phone))
    if len(phone) == 10:
        phone = "91" + phone
    url = "https://api.fonnte.com/send"
    headers = {"Authorization": FONNTE_TOKEN}
    payload = {"target": phone, "message": message, "countryCode": "91"}
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        result = response.json()
        print(f"  Fonnte response: {result}")
        return result.get("status") == True or str(result.get("status")).lower() == "true"
    except Exception as e:
        print(f"  Fonnte error: {e}")
        return False

def get_due_customers():
    result = sb.table("reorder_customers").select("*").eq("paused", False).eq("sent_today", False).execute()
    customers = result.data or []
    due_today = []
    for c in customers:
        order_date = c.get("order_date")
        reminder_days = c.get("reminder_days", 8)
        if not order_date:
            continue
        od = datetime.strptime(order_date, "%Y-%m-%d").date()
        reminder_date = od + timedelta(days=reminder_days)
        if reminder_date <= date.today():
            due_today.append(c)
    return due_today

def mark_sent(customer_id):
    today = date.today().isoformat()
    sb.table("reorder_customers").update({"sent_today": True, "last_sent_date": today}).eq("id", customer_id).execute()

def run_bot():
    print(f"\n{'='*50}")
    print(f"🤖 Siddhi Pharma Bot — {date.today()}")
    print(f"{'='*50}")
    due_customers = get_due_customers()
    print(f"\n📋 Due customers aaj: {len(due_customers)}")
    if not due_customers:
        print("✅ Aaj koi reminder nahi — sab clear!")
        return
    sent = 0
    failed = 0
    for customer in due_customers:
        name = customer["name"]
        phone = customer["phone"]
        print(f"\n📱 Sending to: {name} ({phone})")
        message = build_message(customer)
        success = send_whatsapp(phone, message)
        if success:
            mark_sent(customer["id"])
            print(f"  ✅ Sent!")
            sent += 1
        else:
            print(f"  ❌ Failed!")
            failed += 1
    print(f"\n{'='*50}")
    print(f"📊 Summary: {sent} sent, {failed} failed")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    run_bot()
