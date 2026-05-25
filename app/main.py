from fastapi import FastAPI, HTTPException
# [Revisión] Ver CHANGELOG_REVISION.md -> "app/main.py"
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.api.routes import (
    ticket,
    auth,
    devices,
    setup,
    users,
    dashboard,
    ticket_status,
    modules,
    inventory,
    invoice,
    finance,
)
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.core.config import settings

app = FastAPI(
    title="ProGesTec API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ALLOW_ALL_ORIGINS else settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(ticket.router)
app.include_router(devices.router)
app.include_router(setup.router)
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(ticket_status.router)
app.include_router(modules.router)
app.include_router(inventory.router)
app.include_router(invoice.router)
app.include_router(finance.router)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.mount(settings.MEDIA_URL, StaticFiles(directory=settings.MEDIA_ROOT), name="uploads")
