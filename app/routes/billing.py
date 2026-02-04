# app/routes/billing.py

import os
import sqlite3
import razorpay
from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

# =====================================================
# CONFIG
# =====================================================

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET")
PLAN_ID = os.getenv("RAZORPAY_PLAN_ID")

DB_PATH = "/home/supersu/indianode-backend/indianode.db"

print("========================================")
print("🚀 BILLING MODULE LOADED")
print("KEY:", RAZORPAY_KEY_ID)
print("PLAN:", PLAN_ID)
print("DB:", DB_PATH)
print("========================================")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET))


# =====================================================
# DB HELPER
# =====================================================

def get_conn():
    return sqlite3.connect(DB_PATH)


# =====================================================
# CUSTOMER (reuse or create)
# =====================================================

def get_or_create_customer(email: str):
    print("🔍 Checking customer for:", email)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT razorpay_customer_id FROM users WHERE email=?",
        (email,)
    )
    row = cur.fetchone()

    if row and row[0]:
        conn.close()
        print("✅ Reusing customer:", row[0])
        return row[0]

    print("🆕 Creating Razorpay customer")

    customer = client.customer.create({
        "email": email,
        "name": email.split("@")[0]
    })

    customer_id = customer["id"]

    cur.execute(
        "UPDATE users SET razorpay_customer_id=? WHERE email=?",
        (customer_id, email)
    )
    conn.commit()
    conn.close()

    print("✅ Customer created:", customer_id)

    return customer_id


# =====================================================
# CREATE SUBSCRIPTION
# =====================================================

@router.post("/api/billing/create-subscription")
async def create_subscription(request: Request):

    print("\n🔥 CREATE SUBSCRIPTION HIT")

    email = request.headers.get("x-user-email")

    if not email:
        raise HTTPException(status_code=400, detail="Missing email header")

    print("📧 Email:", email)

    try:
        customer_id = get_or_create_customer(email)

        # ⭐⭐⭐ CRITICAL FIX — SEND EMAIL IN NOTES ⭐⭐⭐
        payload = {
            "plan_id": PLAN_ID,
            "customer_id": customer_id,
            "customer_notify": 1,
            "total_count": 12,
            "notes": {
                "email": email
            }
        }

        print("🚀 Razorpay payload:", payload)

        sub = client.subscription.create(payload)

        print("🎯 Subscription created:", sub["id"])

        return {"subscription_id": sub["id"]}

    except Exception as e:
        print("❌ Razorpay error:", e)
        raise HTTPException(status_code=500, detail=str(e))

