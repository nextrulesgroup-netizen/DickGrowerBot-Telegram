from aiogram import Router

from app.handlers.commands import router as commands_router
from app.handlers.inline import router as inline_router

router = Router()
router.include_router(commands_router)
router.include_router(inline_router)
