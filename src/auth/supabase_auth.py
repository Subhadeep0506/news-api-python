from supabase.client import Client, SupabaseAuthClient
from gotrue.errors import AuthWeakPasswordError, AuthApiError
from ..config.supabase_config import SupabaseConfig
from ..models.user import UserSignup, UserLogin
from ..errors.supabase_error import *


def signup_user(user: UserSignup, auth_service: SupabaseAuthClient):
    try:
        response = auth_service.sign_up(user.model_dump())
        return response
    except AuthWeakPasswordError as _:
        raise SupabaseWeakPasswordException(
            "Password is weak. Please use a stronger password."
        )
    except AuthApiError as e:
        raise SupabaseUserSignupException(f"Failed to signup user: {str(e)}")


def login_user(user: UserLogin, auth_service: SupabaseAuthClient):
    try:
        response = auth_service.sign_in_with_password(user.model_dump())
        return response
    except AuthApiError as e:
        raise SupabaseUserLoginException(f"Failed to login user: {str(e)}")


def logout_user(auth_service: SupabaseAuthClient):
    try:
        response = auth_service.sign_out()
        return response
    except AuthApiError as e:
        raise SupabaseUserLogoutException(f"Failed to logout user: {str(e)}")


def get_current_session(auth_service: SupabaseAuthClient):
    try:
        response = auth_service.get_session()
        return response
    except AuthApiError as e:
        raise SupabaseUserLoginException(f"Failed to get current session: {str(e)}")
