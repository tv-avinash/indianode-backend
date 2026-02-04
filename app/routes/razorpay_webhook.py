import os
import hmac
import hashlib
import sqlite3
from fastapi import APIRouter, Request

router = APIRouter()

WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")
DB_PATH = "/home/supersu/indianode-backend/indianode.db"


def verify_signature(body: bytes, signature: str | None):
    if not signature:
        return False

    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


def upgrade_user(email: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET plan='pro' WHERE email=?",
        (email,)
    )

    conn.commit()
    conn.close()

    print("✅ USER UPGRADED:", email)


@router.post("/api/webhook/razorpay")
async def razorpay_webhook(request: Request):

    print("🔥 WEBHOOK HIT")

    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature")

    if not verify_signature(body, signature):
        print("❌ Invalid signature")
        return {"status": "invalid signature"}

    payload = await request.json()

    event = payload.get("event")
    print("EVENT:", event)

    try:
        # ======================================
        # subscription events
        # ======================================
        if event.startswith("subscription."):

            sub = payload["payload"]["subscription"]["entity"]
            email = sub.get("notes", {}).get("email")

            if email:
                upgrade_user(email)

        # ======================================
        # payment events (IMPORTANT)
        # ======================================
        elif event == "payment.captured":

            payment = payload["payload"]["payment"]["entity"]
            notes = payment.get("notes", {})
            email = notes.get("email")

            if email:
                upgrade_user(email)

    except Exception as e:
        print("Webhook error:", e)

    return {"status": "ok"}

