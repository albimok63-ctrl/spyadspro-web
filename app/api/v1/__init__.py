# API v1 package.

from fastapi import APIRouter

from . import auth
from . import health
from . import items
from . import scraper

router = APIRouter()

router.include_router(health.router)
router.include_router(items.router)
router.include_router(auth.router)
router.include_router(scraper.router)
