from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx

from app.config import get_settings
from app.database import get_db
from app.dependencies import SESSION_COOKIE_NAME, get_current_user
from app.models.user import User
from app.schemas.user_schema import UserOut
from app.services.auth_service import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])
settings = get_settings()

SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days, matches auth_service token expiry


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
    # short-lived session JWT in an httpOnly cookie.
    session_token = create_access_token(user.id)

    redirect = RedirectResponse(url=settings.client_url)
    redirect.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        max_age=SESSION_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        # "lax" + no explicit domain works as long as the frontend and API
        # share a registrable domain (e.g. localhost:5173 / localhost:8000,
        # or app.example.com / api.example.com). A frontend on a fully
        # different domain would need samesite="none" and secure=True.
        secure=settings.environment != "development",
    )
    return redirect


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"status": "logged_out"}
