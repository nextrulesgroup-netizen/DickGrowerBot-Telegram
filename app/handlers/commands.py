from __future__ import annotations

import html
import re
from datetime import datetime
from io import BytesIO
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.i18n import gettext as _
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


def _format_user_mention(username: str | None, user_id: int) -> str:
    if username:
        return f"@{username}"
    return f"<a href='tg://user?id={user_id}'>User</a>"


def _parse_size_request(text: str) -> tuple[int | None, str | None]:
    parts = text.strip().split(maxsplit=2)
    if len(parts) < 2:
        return None, None
    amount_str = parts[1]
    if not amount_str.lstrip("+-").isdigit():
        return None, None
    amount = int(amount_str)
    details = parts[2].strip() if len(parts) > 2 else None
    return amount, details


async def _resolve_target_user(session, message: Message, text: str | None = None) -> int | None:
    if text:
        text = text.strip()
        if text.isdigit():
            return int(text)
        if text.startswith("@"):  # username
            user = await UserRepository(session).get_by_username(text.strip("@"))
            return user.telegram_id if user else None
    return await _resolve_opponent(session, message)


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    bot = message.bot
    me = await bot.get_me()
    await message.answer(
        _("welcome"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=_("play_in_group"), url=f"https://t.me/{me.username}?start=join")],
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
            verb = _("grew") if change >= 0 else _("shrunk")
            await message.answer(_("grow_success").format(verb=verb, change=abs(change), reason=reason, total=total))
        except RuntimeError:
            await message.answer(_("grow_cooldown"))
        except Exception:
            error_counter.inc()
            await message.answer(_("grow_error"))
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


@router.message(Command("buy"))
async def buy_handler(message: Message) -> None:
    command_usage.labels(command="buy").inc()
    settings = container["settings"]
    if not settings.admin_id_set:
        await message.answer(_("buy_owner_not_defined"))
        return

    amount, details = _parse_size_request(message.text or "")
    if amount is None or amount <= 0:
        await message.answer(_("buy_usage"))
        return

    async with container["sessionmaker"]() as session:
        context = _build_context(session)
        await context["game"].register_user(message)
        await context["game"].register_chat(message)

        mention = _format_user_mention(message.from_user.username, message.from_user.id)
        note = html.escape(details) if details else _("buy_note_no_details")
        sample_target = f"@{message.from_user.username}" if message.from_user.username else str(message.from_user.id)
        owner_text = _( "buy_owner_text" ).format(mention=mention, user_id=message.from_user.id, amount=amount, note=note, target=sample_target)

        sent_count = 0
        for admin_id in settings.admin_id_set:
            try:
                await message.bot.send_message(admin_id, owner_text)
                sent_count += 1
            except TelegramBadRequest:
                continue
            except Exception:
                continue

        if sent_count > 0:
            await message.answer(_("buy_sent"))
        else:
            await message.answer(_("buy_failed"))


@router.message(Command("owner"))
async def owner_handler(message: Message) -> None:
    settings = container["settings"]
    if not settings.admin_id_set:
        await message.answer(_("owner_not_defined"))
        return

    lines = []
    async with container["sessionmaker"]() as session:
        for admin_id in settings.admin_id_set:
            user = await UserRepository(session).get_by_telegram_id(admin_id)
            if user and user.username:
                lines.append(f"@{user.username} ({admin_id})")
            else:
                lines.append(f"<a href='tg://user?id={admin_id}'>{_('owner_not_defined')}</a> ({admin_id})")

    await message.answer(_("owner_list_title").format(list='\n'.join(lines)))


@router.message(Command("addsize"))
async def addsize_handler(message: Message) -> None:
    command_usage.labels(command="addsize").inc()
    settings = container["settings"]
    if not _admin_check(message.from_user.id, settings):
        await message.answer(_("addsize_no_admin"))
        return

    text = (message.text or "").strip()
    parts = text.split(maxsplit=3)
    if len(parts) < 3 or not parts[2].lstrip("+-").isdigit():
        await message.answer(_("addsize_usage"))
        return

    target_text = parts[1]
    amount = int(parts[2])
    reason = parts[3].strip() if len(parts) > 3 else "Manual size update"

    if amount == 0:
        await message.answer(_("addsize_amount_zero"))
        return

    async with container["sessionmaker"]() as session:
        target_id = await _resolve_target_user(session, message, target_text)
        if target_id is None:
            await message.answer(_("addsize_user_not_found"))
            return

        user_repo = UserRepository(session)
        target_user = await user_repo.get_by_telegram_id(target_id)
        if not target_user:
            target_user = await user_repo.create_or_update(target_id, None, None, settings.default_language)

        chat_id = target_id if message.chat.type == "private" else message.chat.id
        stats_repo = StatsRepository(session)
        stats = await stats_repo.add_growth(target_user.id, chat_id, amount, f"Manual admin add: {reason}", datetime.utcnow())
        await session.commit()

    target_mention = _format_user_mention(target_user.username, target_id)
    await message.answer(_("addsize_success").format(amount=amount, target=target_mention, total=stats.total_size))
    try:
        await message.bot.send_message(
            target_id,
            _("addsize_notify_target").format(amount=amount, reason=reason)
        )
    except Exception:
        pass


@router.message(Command("fight"))
async def fight_handler(message: Message) -> None:
    command_usage.labels(command="fight").inc()
    async with container["sessionmaker"]() as session:
        context = _build_context(session)
        opponent_id = await _resolve_opponent(session, message)
        if opponent_id is None or opponent_id == message.from_user.id:
            await message.answer(_("fight_challenge_error"))
            return
        user = await UserRepository(session).get_by_telegram_id(message.from_user.id)
        if not user:
            user = await context["game"].register_user(message)
        opponent = await UserRepository(session).get_by_telegram_id(opponent_id)
        if not opponent:
            await message.answer(_("fight_no_record"))
            return
        result, details = await context["pvp"].battle(message.from_user.id, opponent_id)
        if result == "draw":
            content = _("fight_draw")
        elif result == "attacker":
            content = _("fight_win").format(attacker_power=details['attacker_power'], defender_power=details['defender_power'])
        else:
            content = _("fight_lose").format(attacker_power=details['attacker_power'], defender_power=details['defender_power'])
        if details.get("critical"):
            content += _("fight_critical")
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
        await message.answer(_("admin_restricted"))
        return
    await message.answer(_("admin_commands_available"))


@router.message(Command("config"))
async def config_handler(message: Message) -> None:
    settings = container["settings"]
    if not _admin_check(message.from_user.id, settings):
        await message.answer(_("config_only_admin"))
        return
    await message.answer(
        _("config_text").format(min=settings.growth_min, max=settings.growth_max, dbmin=settings.daily_bonus_min, dbmax=settings.daily_bonus_max, pvp=settings.pvp_cooldown, prom=settings.enable_prometheus)
    )


@router.message(Command("reset"))
async def reset_handler(message: Message) -> None:
    settings = container["settings"]
    command_usage.labels(command="reset").inc()
    if not _admin_check(message.from_user.id, settings):
        await message.answer(_("reset_only_admin"))
        return
    async with container["sessionmaker"]() as session:
        target_id = await _resolve_opponent(session, message)
        if not target_id:
            await message.answer(_("reset_no_target"))
            return
        await session.execute(delete(PlayerStats).where(PlayerStats.user_id == target_id))
        await session.commit()
        await message.answer(_("reset_success"))


@router.message(Command("export"))
async def export_handler(message: Message) -> None:
    settings = container["settings"]
    if not _admin_check(message.from_user.id, settings):
        await message.answer(_("export_only_admin"))
        return
    await message.answer(_("export_only_admin"))


@router.message(Command("import"))
async def import_handler(message: Message) -> None:
    settings = container["settings"]
    if not _admin_check(message.from_user.id, settings):
        await message.answer(_("import_only_admin"))
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
                await message.answer(_("import_only_formats"))
                return
            await message.answer(_("import_success").format(count=count, filename=message.document.file_name))
        return
    await message.answer(_("import_prompt"))
