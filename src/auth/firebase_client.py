# import pyrebase

# from pyrebase.pyrebase import Firebase, Auth
# from ..config.firebase_config import FirebaseConfig
# from requests import HTTPError
# from ..errors.firebase_error import (
#     FirebaseUserAlreadyExistsException,
#     FirebaseUserInvalidCredentialsException,
#     FirebaseUserNotVerifiedException,
#     FirebaseVerifyUserMailNotSentException,
# )


# class FirebaseClient:
#     def __init__(self):
#         self.config = FirebaseConfig.get_config()
#         self.firebase: Firebase = None

#     def initialize_app(self):
#         if self.firebase is None:
#             self.firebase = pyrebase.initialize_app(self.config)

#     def user_login(self, email: str, password: str):
#         try:
#             auth = self.firebase.auth()  # type: Auth
#             user = auth.sign_in_with_email_and_password(email, password)
#             # if user["kind"] == "identitytoolkit#VerifyPasswordResponse":
#             #     raise FirebaseUserNotVerifiedException("User not verified.")
#             return user
#         except HTTPError as _:
#             raise FirebaseUserInvalidCredentialsException("Invalid user credentials.")

#     def user_signup(self, email: str, password: str):
#         try:
#             auth = self.firebase.auth()  # type: Auth
#             user = auth.create_user_with_email_and_password(email, password)
#             _resp = auth.send_email_verification(user["idToken"])
#             if _resp["kind"] == "identitytoolkit#GetOobConfirmationCodeResponse":
#                 return user
#             else:
#                 raise FirebaseVerifyUserMailNotSentException(
#                     "Verify user mail not sent."
#                 )
#         except HTTPError as _:
#             raise FirebaseUserAlreadyExistsException("User already exists.")

#     def get_user_information(self, auth: Auth, user: dict):
#         info = auth.get_account_info(user["idToken"])
#         return info

from firebase_admin import App, initialize_app
from firebase_admin.auth import create_user
import json
from ..config.firebase_config import FirebaseConfig
from requests import HTTPError
from ..errors.firebase_error import (
    FirebaseUserAlreadyExistsException,
    FirebaseUserInvalidCredentialsException,
    FirebaseUserNotVerifiedException,
    FirebaseVerifyUserMailNotSentException,
)


class FirebaseClient:
    def __init__(self):
        self.config = FirebaseConfig.get_config()
        self.firebase = None

    def initialize_app(self):
        if self.firebase is None:
            self.firebase = initialize_app(options=self.config)

    def user_signup(self, email: str, password: str, display_name: str):
        try:
            user = create_user(
                email=email, password=password, display_name=display_name
            )
            # if user["kind"] == "identitytoolkit#VerifyPasswordResponse":
            #     raise FirebaseUserNotVerifiedException("User not verified.")
            return user
        except HTTPError as _:
            raise FirebaseUserInvalidCredentialsException("Invalid user credentials.")
