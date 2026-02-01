from fastapi import FastAPI
from app.modules.users.router import router as users_router
from app.modules.auth.router import router as auth_router
from app.modules.agri_logic.router import router as agri_logic_router
from app.modules.ews.router import router as ews_router

app = FastAPI(title="FastAPI Backend")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(agri_logic_router)  # Prefix is already defined in router.py
app.include_router(ews_router)  # Prefix is already defined in router.py
