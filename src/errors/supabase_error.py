class SupabaseAppInitializationException(Exception):
    pass


class SupabaseUserInvalidCredentialsException(Exception):
    pass


class SupabaseUserAlreadyExistsException(Exception):
    pass


class SupabaseUserNotVerifiedException(Exception):
    pass


class SupabaseVerifyUserMailNotSentException(Exception):
    pass
