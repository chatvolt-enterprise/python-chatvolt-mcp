import os
from contextvars import ContextVar

from dotenv import load_dotenv

load_dotenv()

CHATVOLT_API_KEY = os.getenv("CHATVOLT_API_KEY")
CHATVOLT_BASE_URL = os.getenv("CHATVOLT_BASE_URL", "https://api.chatvolt.ai")
VOLTAPI_BASE_URL = os.getenv("VOLTAPI_BASE_URL")

_request_auth_token: ContextVar[str | None] = ContextVar("request_auth_token", default=None)


def set_request_auth_token(token: str | None) -> None:
    """Set the bearer token from the current HTTP request."""
    _request_auth_token.set(token)


def get_auth_token() -> str | None:
    """Get the bearer token. Priority: HTTP request token > CHATVOLT_API_KEY from env."""
    request_token = _request_auth_token.get()
    if request_token:
        return request_token
    return CHATVOLT_API_KEY


if not CHATVOLT_API_KEY:
    import warnings

    warnings.warn("CHATVOLT_API_KEY not found in environment variables.", stacklevel=2)
