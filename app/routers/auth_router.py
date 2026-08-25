from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user_schema import UserOut
from app.services.auth_service import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])
settings = get_settings()


@router.get("/github/login")
def github_login():
    url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.github_client_id}"
        f"&redirect_uri={settings.github_callback_url}"
        f"&scope=repo"
    )
    return {"authorize_url": url}


@router.get("/github/callback")
async def github_callback(code: str, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": settings.github_callback_url,
            },
        )
        token_data = token_res.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(400, "Failed to obtain access token from GitHub")

        user_res = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        gh_user = user_res.json()

    user = db.query(User).filter(User.github_id == str(gh_user["id"])).first()
    if user:
        user.access_token = access_token
        user.username = gh_user["login"]
    else:
        user = User(
            github_id=str(gh_user["id"]),
            username=gh_user["login"],
            access_token=access_token,
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    # The GitHub token stays server-side; the browser only gets a
    # short-lived session JWT. It's passed back as a query param rather
    # than an httpOnly cookie because the frontend may be hosted on a
    # different origin/scheme than this API (e.g. a deployed frontend
    # talking to a local backend during dev) - cross-site cookies require
    # SameSite=None+Secure, which needs an HTTPS backend. The frontend
    # reads this param once and stores it itself.
    session_token = create_access_token(user.id)
    return RedirectResponse(url=f"{settings.client_url}/?token={session_token}")


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
