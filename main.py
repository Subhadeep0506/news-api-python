import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from authentication import auth
from authentication.auth_bearer import JWTBearer
from database.database import Base, SessionLocal, engine
from models.user import User
from schemas.password import ChangePassword
from schemas.token import TokenSchema
from schemas.user import UserCreate, UserLogin, UserUpdate

Base.metadata.create_all(engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Hello from FastAPI"}


@app.post("/register")
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    return auth.register_user(user=user, user_model=User, session=session)


@app.post("/login", response_model=TokenSchema)
def login(request: UserLogin, session: Session = Depends(get_session)):
    return auth.login_user(db=session, request=request)


@app.get("/me/info")
def get_user_info(
    dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)
):
    return auth.get_user_info(dependencies=dependencies, db=session)


@app.post("/me/logout")
def logout(dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)):
    return auth.logout_user(dependencies=dependencies, db=session)


@app.get("/users")
def get_users(
    dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)
):
    return auth.list_users(dependencies=dependencies, db=session)


@app.post("/me/change-password")
def change_password(
    request: ChangePassword,
    dependencies=Depends(JWTBearer()),
    session: Session = Depends(get_session),
):
    return auth.change_password(request=request, dependencies=dependencies, db=session)


@app.put("/me/update")
def update_user_info(
    user_update: UserUpdate,
    dependencies=Depends(JWTBearer()),
    session: Session = Depends(get_session),
):
    return auth.update_user(
        user_update,
        dependencies=dependencies,
        db=session,
    )


@app.delete("/me/delete")
def delete_user(
    dependencies=Depends(JWTBearer()),
    session: Session = Depends(get_session),
):
    return auth.delete_user(
        dependencies=dependencies,
        db=session,
    )


@app.delete("/delete/{user_id}")
def delete_user_by_id(
    user_id: str,
    dependencies=Depends(JWTBearer()),
    session: Session = Depends(get_session),
):
    return auth.delete_user_by_id(
        user_id=user_id,
        dependencies=dependencies,
        db=session,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8089, reload=True)
