from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.models import User
from app.utils.jwt_utils import create_access_token, get_password_hash, verify_password

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@auth_router.post("/register")
async def register_user(
    username: str, password: str, email: str, db: AsyncSession = Depends(get_db)
):

    existing_user = await db.execute(select(User).filter(User.username == username))
    if existing_user.fetchone():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = get_password_hash(password)

    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "User registered successfully", "user": new_user.username}


@auth_router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        f"SELECT * FROM users WHERE username='{form_data.username}'"
    )
    user = result.fetchone()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    return {"user": token}
