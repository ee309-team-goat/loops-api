"""
API routes aggregator - includes all domain routers.
"""

from fastapi import APIRouter

from app.api.auth import TAG_METADATA as auth_tag
from app.api.auth import router as auth_router
from app.api.cards import TAG_METADATA as cards_tag
from app.api.cards import router as cards_router
from app.api.decks import TAG_METADATA as decks_tag
from app.api.decks import router as decks_router
from app.api.profiles import TAG_METADATA as profiles_tag
from app.api.profiles import router as profiles_router
from app.api.progress import TAG_METADATA as progress_tag
from app.api.progress import router as progress_router
from app.api.quiz import TAG_METADATA as quiz_tag
from app.api.quiz import router as quiz_router
from app.api.stats import TAG_METADATA as stats_tag
from app.api.stats import router as stats_router
from app.api.study import TAG_METADATA as study_tag
from app.api.study import router as study_router

router = APIRouter()

# Collect all tag metadata for OpenAPI
OPENAPI_TAGS = [
    auth_tag,
    profiles_tag,
    cards_tag,
    progress_tag,
    decks_tag,
    stats_tag,
    study_tag,
    quiz_tag,
]

# Include domain routers
router.include_router(auth_router)
router.include_router(profiles_router)
router.include_router(cards_router)
router.include_router(progress_router)
router.include_router(decks_router)
router.include_router(stats_router)
router.include_router(study_router)
router.include_router(quiz_router)
