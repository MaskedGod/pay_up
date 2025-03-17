from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.sql import text
from app.api.auth.auth import auth_router
from app.api.payments.payments import payments_router
from app.db.database import get_db

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(payments_router, prefix="/payments", tags=["payments"])


@app.get("/")
async def health_check(db=Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            return {"status": "healthy", "db_status": "reachable"}
        else:
            return {"status": "unhealthy", "db_status": "unexpected result"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "db_status": "unreachable", "error": str(e)},
        )
