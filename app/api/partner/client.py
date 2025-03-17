import httpx
from app.config.settings import settings
from fastapi import HTTPException


class PayAdmitClient:
    def __init__(self):
        self.api_url = settings.PAYADMIT_API_URL
        self.api_key = settings.API_KEY

    # Для всех запросов используем API_KEY
    async def initiate_payment(self, amount: int, currency: str):
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/payments",
                    headers=headers,
                    json={"amount": amount, "currency": currency},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code, detail="Error initiating payment"
            )

    async def confirm_payment(self, payment_id: int):
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/payments/{payment_id}/confirm", headers=headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code, detail="Error confirming payment"
            )
