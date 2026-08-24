from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

from app.config import get_settings
from app.database import get_db
from app.models.user import User

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

    # In a real app: issue your own session/JWT here instead of returning
    # the raw GitHub token to the client.
    return {"user_id": user.id, "username": user.username}
