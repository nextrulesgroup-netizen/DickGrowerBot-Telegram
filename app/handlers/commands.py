from __future__ import annotations

import re
from io import BytesIO
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import delete

from app.config import Settings
from app.core.container import container
from app.models.player_stats import PlayerStats
from app.repositories.chat import ChatRepository
from app.repositories.event import EventRepository
from app.repositories.import_log import ImportLogRepository
from app.repositories.pvp import PVPRepository
from app.repositories.stats import StatsRepository
from app.repositories.user import UserRepository
from app.services.event import EventService
from app.services.game import GameService
from app.services.importer import ImportService
from app.services.pvp import PVPService
from app.metrics.exporter import command_usage, error_counter

router = Router()


def _admin_check(user_id: int, settings: Settings) -> bool:
    return user_id in settings.admin_id_set


def _build_context(session):
    settings = container["settings"]
    redis_client = container["redis"]
    return {
        "settings": settings,
        "game": GameService(UserRepository(session), ChatRepository(session), StatsRepository(session), redis_client, settings),
        "event": EventService(EventRepository(session), StatsRepository(session), settings),
        "pvp": PVPService(PVPRepository(session), settings),
        "importer": ImportService(UserRepository(session), ImportLogRepository(session)),
    }


def _parse_mention(text: str) -> str | None:
    match = re.search(r"@([A-Za-z0-9_]+)", text)
    return match.group(1) if match else None


async def _resolve_opponent(session, message: Message) -> int | None:
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id
    mention = _parse_mention(message.text or "")
    if mention:
        user = await UserRepository(session).get_by_username(mention)
        if user:
            return user.telegram_id
    return None


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    bot = message.bot
    me = await bot.get_me()
    await message.answer(
        "Welcome to DickGrowerBot! Use /grow to grow your size, /fight to challenge a rival, and /top to compare stats.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Play in group", url=f"https://t.me/{me.username}?start=join")],
        ]),
    )


@router.message(Command("grow"))
async def grow_handler(message: Message) -> None:
    command_usage.labels(command="grow").inc()
    async with container["sessionmaker"]() as session:
        context = _build_context(session)
        await context["game"].register_chat(message)
        user = await context["game"].register_user(message)
        try:
            change, reason, total = await context["game"].grow(user, message.chat.id)
            verb = "grew" if change >= 0 else "shrunk"
            await message.answer(f"You {verb} {abs(change)} cm because of {reason}. Total size is now {total}.")
        except RuntimeError:
            await message.answer("You can only grow once every 24 hours. Come back tomorrow for another throwdown.")
        except Exception:
            error_counter.inc()
            await message.answer("Something went wrong while growing. Try again later.")
            raise


@router.message(Command("dick"))
@router.message(Command("size"))
@router.message(Command("stats"))
async def stats_handler(message: Message) -> None:
    command_usage.labels(command="stats").inc()
    async with container["sessionmaker"]() as session:
        context = _build_context(session)
        user = await context["game"].register_user(message)
        await message.answer(await context["game"].get_stats_text(user, message.chat.id))


@router.message(Command("top"))
async def top_handler(message: Message) -> None:
    command_usage.labels(command="top").inc()
    async with container["sessionmaker"]() as session:
        context = _build_context(session)
        if message.chat.type == "private":
            text = await context["game"].get_global_leaderboard()
        else:
            text = await context["game"].get_leaderboard(message.chat.id)
        await message.answer(text)


@router.message(Command("fight"))
async def fight_handler(message: Message) -> None:
    command_usage.labels(command="fight").inc()
    async with container["sessionmaker"]() as session:
        context = _build_context(session)
        opponent_id = await _resolve_opponent(session, message)
        if opponent_id is None or opponent_id == message.from_user.id:
            await message.answer("Please challenge another player using @username or by replying to their message.")
            return
        user = await UserRepository(session).get_by_telegram_id(message.from_user.id)
        if not user:
            user = await context["game"].register_user(message)
        opponent = await UserRepository(session).get_by_telegram_id(opponent_id)
        if not opponent:
            await message.answer("That rival does not have a record yet. Have them use /grow first.")
            return
        result, details = await context["pvp"].battle(message.from_user.id, opponent_id)
        if result == "draw":
            content = "The fight ended in a draw. Both fighters survive with bragging rights intact."
        elif result == "attacker":
            content = f"You won the fight! Power {details['attacker_power']} vs {details['defender_power']}"
        else:
            content = f"You lost this round. Power {details['attacker_power']} vs {details['defender_power']}"
        if details.get("critical"):
            content += " Critical hit!"
        await message.answer(content)


@router.message(Command("dotd"))
async def dotd_handler(message: Message) -> None:
    command_usage.labels(command="dotd").inc()
    async with container["sessionmaker"]() as session:
        context = _build_context(session)
        await message.answer(await context["event"].get_today_event(message.chat.id))


@router.message(Command("winner"))
async def winner_handler(message: Message) -> None:
    command_usage.labels(command="winner").inc()
    async with container["sessionmaker"]() as session:
        context = _build_context(session)
        await message.answer(await context["event"].get_today_event(message.chat.id))


@router.message(Command("admin"))
async def admin_handler(message: Message) -> None:
    settings = container["settings"]
    if not _admin_check(message.from_user.id, settings):
        await message.answer("Admin commands are restricted.")
        return
    await message.answer("Admin commands available: /config /reset /export /import")


@router.message(Command("config"))
async def config_handler(message: Message) -> None:
    settings = container["settings"]
    if not _admin_check(message.from_user.id, settings):
        await message.answer("Only administrators can view configuration.")
        return
    await message.answer(
        f"Growth range: {settings.growth_min}..{settings.growth_max}\n"
        f"Daily bonus: {settings.daily_bonus_min}..{settings.daily_bonus_max}\n"
        f"PvP cooldown: {settings.pvp_cooldown}s\n"
        f"Prometheus: {settings.enable_prometheus}\n"
    )


@router.message(Command("reset"))
async def reset_handler(message: Message) -> None:
    settings = container["settings"]
    command_usage.labels(command="reset").inc()
    if not _admin_check(message.from_user.id, settings):
        await message.answer("Only administrators can reset player stats.")
        return
    async with container["sessionmaker"]() as session:
        target_id = await _resolve_opponent(session, message)
        if not target_id:
            await message.answer("Reply to a player's message or mention them to reset their stats.")
            return
        await session.execute(delete(PlayerStats).where(PlayerStats.user_id == target_id))
        await session.commit()
        await message.answer("Player stats have been reset.")


@router.message(Command("export"))
async def export_handler(message: Message) -> None:
    settings = container["settings"]
    if not _admin_check(message.from_user.id, settings):
        await message.answer("Only administrators can export data.")
        return
    await message.answer("Export is available by backing up PostgreSQL. Use pg_dump or the monitoring exports integrated with this deployment.")


@router.message(Command("import"))
async def import_handler(message: Message) -> None:
    settings = container["settings"]
    if not _admin_check(message.from_user.id, settings):
        await message.answer("Only administrators can import data.")
        return
    if message.document and message.document.file_name:
        async with container["sessionmaker"]() as session:
            buffer = BytesIO()
            await message.document.download(destination=buffer)
            text = buffer.getvalue().decode("utf-8")
            context = _build_context(session)
            if message.document.file_name.endswith(".csv"):
                count = await context["importer"].import_csv("manual_csv", text)
            elif message.document.file_name.endswith(".json"):
                count = await context["importer"].import_json("manual_json", text)
            else:
                await message.answer("Only CSV and JSON import formats are supported.")
                return
            await message.answer(f"Imported {count} users from {message.document.file_name}.")
        return
    await message.answer("Send a CSV or JSON document containing telegram_id, username, full_name, and language.")
