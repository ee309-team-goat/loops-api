"""
API routes aggregator - includes all domain routers.
"""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.cards import router as cards_router
from app.api.decks import router as decks_router
from app.api.progress import router as progress_router
from app.api.stats import router as stats_router
from app.api.users import router as users_router

router = APIRouter()

# Include domain routers
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(cards_router)
router.include_router(progress_router)
router.include_router(decks_router)
router.include_router(stats_router)
