from fastapi import HTTPException, Request

from config import API_KEY


async def verify_api_key(request: Request) -> None:
    if not API_KEY:
        raise HTTPException(status_code=503, detail="Service not configured")

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing credentials")

    scheme, _, token = auth_header.partition(" ")
    if not token or scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid credentials")
