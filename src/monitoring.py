from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.auth import decode_token

security = HTTPBearer()


def get_monitoring_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials.credentials)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("scope") != "monitoring":
        raise HTTPException(status_code=401, detail="Not a monitoring token")

    return payload