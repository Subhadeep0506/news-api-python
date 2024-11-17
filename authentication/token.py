from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Union

from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy import desc

from config.fastapi_config import FastAPIConfig
from core.auth.hash import decodeJWT
from models.token import Token


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=FastAPIConfig.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, FastAPIConfig.JWT_SECRET_KEY, FastAPIConfig.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=FastAPIConfig.REFRESH_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, FastAPIConfig.JWT_REFRESH_SECRET_KEY, FastAPIConfig.ALGORITHM
    )
    return encoded_jwt


def token_required(func):
    """Verifies the JWT token. Checks if user is loggedin."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        payload = decodeJWT(kwargs["dependencies"])
        user_id = payload["sub"]
        data = (
            kwargs["db"]
            .query(Token)
            .filter_by(
                user_id=user_id, access_token=kwargs["dependencies"], status=True
            )
            .order_by(desc(Token.created_date))
            .first()
        )
        if data:
            return func(*args, **kwargs)

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token."
            )

    return wrapper
