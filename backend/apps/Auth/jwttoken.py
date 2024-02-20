from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """
    This method will get user jwt tokens.
    """

    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
