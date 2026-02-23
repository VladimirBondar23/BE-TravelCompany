"""
Basic auth dependency. When BASIC_AUTH_USER and BASIC_AUTH_PASSWORD are set,
all protected routes require HTTP Basic Auth.
"""
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from config import BASIC_AUTH_ENABLED, BASIC_AUTH_PASSWORD, BASIC_AUTH_USER

_security = HTTPBasic(auto_error=False)


def verify_basic_auth(
    credentials: HTTPBasicCredentials | None = Depends(_security),
) -> None:
    """Verify Basic auth credentials. No-op when basic auth is disabled."""
    if not BASIC_AUTH_ENABLED:
        return
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )
    if not (
        secrets.compare_digest(credentials.username.encode("utf-8"), BASIC_AUTH_USER.encode("utf-8"))
        and secrets.compare_digest(credentials.password.encode("utf-8"), BASIC_AUTH_PASSWORD.encode("utf-8"))
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
