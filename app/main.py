from fastapi import FastAPI
from app.modules.users.router import router as users_router
from app.modules.auth.router import router as auth_router
from app.modules.predictive_toxicity import router as pt_router


app = FastAPI(title="FastAPI Backend")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(pt_router)

