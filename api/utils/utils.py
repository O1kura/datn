from api.models.token import SlidingToken


def get_tokens_for_user(user, lifetime=None):
    token = SlidingToken.for_user(user, lifetime)
    return str(token)