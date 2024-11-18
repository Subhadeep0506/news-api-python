from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from authentication.auth_bearer import JWTBearer
from authentication.token import (
    create_access_token,
    create_refresh_token,
    token_required,
)
from core.auth.hash import decodeJWT, get_hashed_password, verify_password
from core.auth.roles import Role
from models.token import Token
from models.user import User
from schemas.password import ChangePassword
from schemas.user import UserCreate, UserLogin, UserUpdate


def register_user(user: UserCreate, user_model: User, session: Session):
    try:
        existing_user = (
            session.query(User)
            .filter(or_(User.email == user.email, User.username == user.username))
            .first()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user info. An exception occured: {e}",
        )
    if existing_user:
        raise HTTPException(
            status_code=400, detail="Email/Username already registered."
        )
    encrypted_password = get_hashed_password(user.password)
    new_user = user_model(
        username=user.username,
        email=user.email,
        password=encrypted_password,
        id=str(uuid4()),
        role=user.role if user.role else Role.USER,
        first_name=user.first_name if user.first_name else "",
        last_name=user.last_name if user.last_name else "",
    )
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"message": "User created successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user info. An exception occured: {e}",
        )


def login_user(
    db: Session,
    request: UserLogin,
):
    try:
        user = (
            db.query(User)
            .filter(or_(User.email == request.email, User.username == request.username))
            .first()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user info. An exception occured: {e}",
        )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email/Username or Password.",
        )
    hashed_pass = user.password
    if not verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email/Username or Password.",
        )

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    token_db = Token(
        user_id=user.id, access_token=access, refresh_token=refresh, status=True
    )
    try:
        db.add(token_db)
        db.commit()
        db.refresh(token_db)
        return {
            "access_token": access,
            "refresh_token": refresh,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to login user info. An exception occured: {e}",
        )


@token_required
def get_user_info(dependencies, db: Session):
    user_id = decodeJWT(dependencies)["sub"]
    try:
        user_info = db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user info. An exception occured: {e}",
        )
    if user_info:
        del user_info.password
        return user_info
    else:
        return HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")


@token_required
def logout_user(dependencies: JWTBearer, db: Session):
    token = dependencies
    payload = decodeJWT(token)
    user_id = payload["sub"]
    try:
        token_record = db.query(Token).all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to logout user. An exception occured: {e}",
        )
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
    try:
        if existing_token:
            existing_token.status = False
            db.add(existing_token)
            db.commit()
            db.refresh(existing_token)
        return {"message": "User logged out successfully!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to logout user info. An exception occured: {e}",
        )


@token_required
def change_password(request: ChangePassword, dependencies, db: Session):
    user_id = decodeJWT(dependencies)["sub"]
    try:
        user = db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user info. An exception occured: {e}",
        )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found."
        )

    if not verify_password(request.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password."
        )

    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    try:
        db.commit()
        return {"message": "Password changed successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user password. An exception occured: {e}",
        )


@token_required
def list_users(dependencies, db: Session):
    user_id = decodeJWT(dependencies)["sub"]
    try:
        user_info = db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user info. An exception occured: {e}",
        )
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email/Username or Password.",
        )
    user_role = user_info.role

    if user_role == Role.ADMIN:
        users = db.query(User).all()
        for user in users:
            del user.password
        return {"users": users}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not Authorized."
        )


@token_required
def update_user(user_update: UserUpdate, dependencies, db: Session):
    user_id = decodeJWT(dependencies)["sub"]
    try:
        user_info = db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user info. An exception occured: {e}",
        )
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email/Username or Password.",
        )
    if user_update.first_name:
        user_info.first_name = user_update.first_name
    if user_update.last_name:
        user_info.last_name = user_update.last_name
    if user_update.role:
        user_info.role = user_update.role
    try:
        db.commit()
        db.refresh(user_info)
        return {"message": "User updated successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user info. An exception occured: {e}",
        )


@token_required
def delete_user(dependencies, db: Session):
    try:
        user_id = decodeJWT(dependencies)["sub"]
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )
        db.delete(user)
        db.commit()
        return {"message": "User  deleted successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user. An exception occured: {e}",
        )


@token_required
def delete_user_by_id(user_id: str, dependencies, db: Session):
    requester_id = decodeJWT(dependencies)["sub"]
    try:
        requester = db.query(User).filter(User.id == requester_id).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user info. An exception occured: {e}",
        )
    if requester is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requester not found."
        )
    if requester.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete users",
        )
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if user_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    try:
        db.delete(user_to_delete)
        db.commit()
        return {"message": "User deleted successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user. An exception occured: {e}",
        )
