import uvicorn
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from authentication import auth
from authentication.auth_bearer import JWTBearer
from database.database import Base, SessionLocal, engine
from models.user import User
from schemas.password import ChangePassword
from schemas.token import TokenSchema
from schemas.user import UserCreate, UserLogin

Base.metadata.create_all(engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello from FastAPI"}


@app.post("/register")
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    return auth.register_user(user=user, user_model=User, session=session)


@app.post("/login", response_model=TokenSchema)
def login(request: UserLogin, session: Session = Depends(get_session)):
    return auth.login_user(user=request, user_model=User, db=session, request=request)


@app.post("/logout")
def logout(dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)):
    return auth.logout_user(dependencies=dependencies, db=session)


@app.get("/users")
def get_users(
    dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)
):
    return auth.list_users(dependencies=dependencies, db=session)


@app.post("/change-password")
def change_password(
    request: ChangePassword,
    dependencies=Depends(JWTBearer()),
    session: Session = Depends(get_session),
):
    return auth.change_password(request=request, db=session)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8089, reload=True)
