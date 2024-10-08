import uvicorn

from supabase.client import Client, SupabaseAuthClient
from fastapi import FastAPI, Depends, HTTPException
from src.auth.supabase_auth import (
    signup_user,
    login_user,
    get_current_session,
    logout_user,
)
from src.core.supabase.supabase_client import SupabaseClient
from src.models.user import UserSignup, UserLogin
from src.errors.supabase_error import *

app = FastAPI()
supabase_client: Client = SupabaseClient()


def get_auth_client():
    return supabase_client.auth


@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}


@app.post("/signup")
def signup(
    user: UserSignup, auth_service: SupabaseAuthClient = Depends(get_auth_client)
):
    try:
        response = signup_user(user, auth_service)
        return {"message": response}
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


@app.post("/login")
def signup(
    user: UserLogin, auth_service: SupabaseAuthClient = Depends(get_auth_client)
):
    try:
        response = login_user(user, auth_service)
        return {"message": response}
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


@app.get("/logout")
def latest_session(auth_service: SupabaseAuthClient = Depends(get_auth_client)):
    try:
        response = logout_user(auth_service)
        return {"message": response}
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


@app.get("/relogin")
def latest_session(auth_service: SupabaseAuthClient = Depends(get_auth_client)):
    try:
        response = get_current_session(auth_service)
        return {"message": response}
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8089)
