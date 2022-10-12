#!/usr/bin/python

"""This file is part of Teamlock.
Teamlock is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Teamlock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Teamlock.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Olivier de Régis"
__credits__ = []
__license__ = "GPLv3"
__version__ = "3.0.0"
__maintainer__ = "Teamlock Project"
__email__ = "contact@teamlock.io"
__doc__ = ''

from fastapi.middleware.cors import CORSMiddleware
from starlette_context import middleware, plugins
from toolkits.mongo import connect_to_database
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, status, Depends
from apps.auth.tools import get_current_user
from fastapi_utils.tasks import repeat_every
from toolkits.migrations import Migrations
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from mongoengine import disconnect
from datetime import datetime
from settings import settings
import logging.config
import logging
import uvicorn

from apps.workspace.routers import router as workspace_router
from apps.config.routers import router as config_router
from apps.folder.routers import router as folder_router
from apps.auth.routers import router as auth_router
from apps.user.routers import router as user_router
from apps.secret.routers import router as secret_router

from apps.user.schema import AdminUserSchema, EditUserSchema
from apps.config.schema import ConfigSchema
from toolkits.utils import create_user_toolkits
from apps.workspace.models import Share
from apps.config.models import Config

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")

log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = '{"date": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
# log_config["formatters"]["default"]["fmt"] = '{"date": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'

templates = Jinja2Templates(directory="templates")

docs_url: str | None = "/docs" if settings.DEBUG else None

app = FastAPI(
    debug=settings.DEBUG,
    docs_url=docs_url,
    redoc_url=None
)

origins = ["*"]

app.add_middleware(
    middleware.ContextMiddleware,
    plugins=(
        plugins.ForwardedForPlugin(),
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cronjob to remove expired Shares (every day)
@app.on_event("startup")
@repeat_every(seconds=60*60*24)
def remove_expired_shares():
    shares = Share.objects(expire_at__lte=datetime.utcnow())
    if len(shares) > 0:
        logger.info(f"[EXPIRED SHARE] {len(shares)} has expired. Deleting them")
        shares.delete()

@app.on_event("startup")
async def startup() -> None:
    connect_to_database()


@app.on_event("shutdown")
async def shutdown() -> None:
    disconnect(alias="default")


if not settings.DEV_MODE:
    app.mount("/static", StaticFiles(directory="templates/static"), name="static")

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def main(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})



@app.get("/ping", tags=["Supervision"])
async def ping():
    return "pong"


@app.get(
    "/api/v1/version",
    tags=["Version"],
    dependencies=[Depends(get_current_user)]
)
async def version():
    return settings.VERSION


@app.post(
    "/install",
    tags=["Installation"],
    response_model=str,
    summary="Install TeamLock instance",
    description="Define Configuration and initialize Admin User"
)
async def install(config_schema: ConfigSchema, admin: AdminUserSchema) -> str:
    if Config.objects.count() > 0:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Teamlock already installed"
        )
    
    config: Config = Config(**config_schema.dict())

    if config.allow_self_registration:
        valid: bool = False
        for email in config.allowed_email_addresses:
            if admin.email.endswith(email):
                valid = True
        
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="INVALIDEMAIL"
            )

    config.save()

    user_def: EditUserSchema = EditUserSchema(
        email=admin.email,
        is_admin=True
    )

    try:
        return create_user_toolkits(user_def)
    except Exception as error:
        config.delete()
        raise error


app.include_router(auth_router, tags=["Authentication"], prefix="/api/v1/auth")
app.include_router(user_router, tags=["User"], prefix="/api/v1/user")
app.include_router(config_router, tags=["Configuration"], prefix="/api/v1/config")
app.include_router(workspace_router, tags=["Workspace"], prefix="/api/v1/workspace")
app.include_router(folder_router, tags=["Folder"], prefix="/api/v1/folder")
app.include_router(secret_router, tags=["Secret"], prefix="/api/v1/secret")


try:
    # Try importing PRO features
    from teamlock_pro.main import app as pro_app
    app.mount("/pro", pro_app)
except ImportError:
    if settings.DEV_MODE:
        raise


if __name__ == "__main__":
    Migrations()
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEV_MODE,
        log_config=log_config,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
