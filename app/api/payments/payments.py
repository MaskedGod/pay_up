from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.models import Payment
from app.api.partner.client import PayAdmitClient
from fastapi.security import OAuth2PasswordBearer

payments_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@payments_router.post("/create")
async def create_payment(
    amount: int,
    currency: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    client = PayAdmitClient()
    response = await client.initiate_payment(amount, currency)

    new_payment = Payment(user_id=1, amount=amount, currency=currency, status="pending")
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)

    return {
        "status": "Payment created",
        "payment_id": new_payment.id,
        "partner_response": response,
    }


@payments_router.post("/confirm")
async def confirm_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    client = PayAdmitClient()
    response = await client.confirm_payment(payment_id)

    payment = await db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = "confirmed"
    await db.commit()
    return {"status": "Payment confirmed", "partner_response": response}
