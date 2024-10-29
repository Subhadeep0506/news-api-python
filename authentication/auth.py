from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from authentication.auth_bearer import JWTBearer
from authentication.token import create_access_token, create_refresh_token
from core.auth.hash import decodeJWT, get_hashed_password, verify_password
from core.auth.roles import Role
from models.token import Token
from models.user import User
from schemas.password import ChangePassword
from schemas.user import UserCreate, UserLogin
from authentication.token import token_required

def register_user(user: UserCreate, user_model: User, session):
    existing_user = session.query(User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    encrypted_password = get_hashed_password(user.password)
    new_user = user_model(
        username=user.username,
        email=user.email,
        password=encrypted_password,
        id=str(uuid4()),
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "user created successfully"}


def login_user(
    user: UserCreate, user_model: User, db: Session, request: UserLogin
):
    user = (
        db.query(User)
        .filter(or_(User.email == request.email, User.username == request.username))
        .first()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email/Username or Password",
        )
    hashed_pass = user.password
    if not verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email/Username or Password",
        )

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    token_db = Token(
        user_id=user.id, access_token=access, refresh_token=refresh, status=True
    )
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token": access,
        "refresh_token": refresh,
    }


def logout_user(dependencies: JWTBearer, db: Session):
    token = dependencies
    payload = decodeJWT(token)
    user_id = payload["sub"]
    token_record = db.query(Token).all()
    info = []
    for record in token_record:
        if (
            datetime.now(timezone.utc)
            - record.created_date.replace(tzinfo=timezone.utc)
        ).days > 1:
            info.append(record.user_id)
    if info:
        existing_token = db.query(Token).where(Token.user_id.in_(info)).delete()
        db.commit()

    existing_token = (
        db.query(Token)
        .filter(Token.user_id == user_id, Token.access_token == token)
        .order_by()
        .first()
    )
    if existing_token:
        existing_token.status = False
        db.add(existing_token)
        db.commit()
        db.refresh(existing_token)
    return {"message": "User logged out successfully!"}

@token_required
def change_password(request: ChangePassword, db: Session):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

    if not verify_password(request.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password"
        )

    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    db.commit()
    return {"message": "Password changed successfully"}

@token_required
def list_users(dependencies, db: Session):
    user_id = decodeJWT(dependencies)["sub"]
    user_info = db.query(User).filter(User.id == user_id).first()
    user_role = user_info.role
    if user_role == Role.ADMIN:
        users = db.query(User).all()
        for user in users:
            del user.password
        return {"users": users}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not Authorized"
        )
