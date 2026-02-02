from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")
