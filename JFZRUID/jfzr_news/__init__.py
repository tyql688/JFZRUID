import re
import asyncio

import httpx
from pydantic import ValidationError

from gsuid_core.sv import SV, get_plugin_available_prefix
from gsuid_core.aps import scheduler
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event, Message
from gsuid_core.subscribe import gs_subscribe
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.database.models import Subscribe

from .api import NEWS_URL, AnnouncementNotFoundError, fetch_detail, fetch_announcements
from .draw import render_list, render_detail

sv_news = SV("JFZRUID公告")
sv_cache = SV("JFZRUID公告缓存", pm=3)
sv_subscribe = SV("JFZRUID公告订阅", pm=3)

TOPIC = "[JFZRUID] 公告"
CHECK_MINUTES = 10
_LOCK = asyncio.Lock()


@sv_news.on_command("公告", block=True)
async def send_announcements(bot: Bot, ev: Event) -> None:
    argument = ev.text.strip()
    prefix = get_plugin_available_prefix("JFZRUID")
    if argument and argument != "列表" and re.fullmatch(r"[1-9][0-9]{0,9}", argument) is None:
        await bot.send(f"发送 {prefix}公告列表 查看 ID，发送 {prefix}公告1020 查看详情。")
        return

    try:
        if not argument or argument == "列表":
            announcements = await fetch_announcements()
            if not announcements:
                await bot.send(f"官网当前没有公告。\n{NEWS_URL}")
                return
            if argument == "列表":
                await bot.send(await convert_img(await render_list(announcements[:5], prefix)))
                return
            announcement_id = announcements[0].id
        else:
            announcement_id = int(argument)

        detail = await fetch_detail(announcement_id)
        image = await convert_img(await render_detail(detail))
    except AnnouncementNotFoundError as error:
        await bot.send(f"{error}\n发送 {prefix}公告列表 查看 ID。")
        return
    except httpx.HTTPError:
        await bot.send(f"疾风之刃公告请求失败，请稍后重试。\n官网：{NEWS_URL}")
        return
    except ValidationError:
        await bot.send(f"官网公告数据格式异常，暂时无法读取。\n官网：{NEWS_URL}")
        return

    await bot.send([Message("image", image), Message("text", f"原文：{detail.url}")])


@sv_cache.on_fullmatch("清理公告缓存", block=True)
async def clear_news_cache(bot: Bot, ev: Event) -> None:
    fetch_announcements.cache_clear()
    fetch_detail.cache_clear()
    render_list.cache_clear()
    render_detail.cache_clear()
    await bot.send("公告缓存已清理，下次查询会重新获取。")


async def _session_subscriptions(ev: Event) -> list[Subscribe]:
    subscriptions = await gs_subscribe.get_subscribe(TOPIC)
    return [
        sub
        for sub in subscriptions or ()
        if sub.bot_id == ev.bot_id and sub.group_id == ev.group_id and sub.WS_BOT_ID == ev.WS_BOT_ID
    ]


@sv_subscribe.on_fullmatch("订阅公告", block=True)
async def subscribe_news(bot: Bot, ev: Event) -> None:
    if ev.user_type != "group":
        await bot.send("请在群聊中订阅公告。")
        return
    async with _LOCK:
        if await _session_subscriptions(ev):
            await bot.send("本群已订阅疾风之刃公告。")
            return
        try:
            fetch_announcements.cache_invalidate()
            announcements = await fetch_announcements()
        except (httpx.HTTPError, ValidationError):
            await bot.send(f"暂时无法读取官网公告，订阅未开启，请稍后重试。\n{NEWS_URL}")
            return
        last_id = max((item.id for item in announcements), default=0)
        await gs_subscribe.add_subscribe("session", TOPIC, ev, extra_message=str(last_id))
    await bot.send(f"已订阅疾风之刃公告，每 {CHECK_MINUTES} 分钟检查一次，只推送新公告。")


@sv_subscribe.on_fullmatch(("取消订阅公告", "退订公告"), block=True)
async def unsubscribe_news(bot: Bot, ev: Event) -> None:
    if ev.user_type != "group":
        await bot.send("请在群聊中取消订阅公告。")
        return
    async with _LOCK:
        subscriptions = await _session_subscriptions(ev)
        for sub in subscriptions:
            await Subscribe.delete_row(id=sub.id)
    await bot.send("已取消疾风之刃公告订阅。" if subscriptions else "本群尚未订阅疾风之刃公告。")


@scheduler.scheduled_job("interval", minutes=CHECK_MINUTES, max_instances=1, coalesce=True)
async def check_news() -> None:
    async with _LOCK:
        subscriptions = await gs_subscribe.get_subscribe(TOPIC)
        if not subscriptions:
            return
        try:
            fetch_announcements.cache_invalidate()
            announcements = await fetch_announcements()
        except (httpx.HTTPError, ValidationError):
            logger.exception("[JFZRUID] 公告列表读取失败，本轮推送已停止")
            return
        announcement_ids = sorted(item.id for item in announcements)
        if not announcement_ids:
            return
        messages: dict[int, list[Message]] = {}
        for sub in subscriptions:
            if sub.extra_message is None:
                await Subscribe.update_data_by_data({"id": sub.id}, {"extra_message": str(announcement_ids[-1])})
                continue
            if not sub.extra_message.isascii() or not sub.extra_message.isdecimal():
                logger.error(f"[JFZRUID] 订阅 {sub.id} 的公告进度无效")
                continue
            last_id = int(sub.extra_message)
            try:
                for announcement_id in announcement_ids:
                    if announcement_id <= last_id:
                        continue
                    if announcement_id not in messages:
                        detail = await fetch_detail(announcement_id)
                        image = await convert_img(await render_detail(detail))
                        messages[announcement_id] = [
                            Message("image", image),
                            Message("text", f"疾风之刃新公告\n原文：{detail.url}"),
                        ]
                    if await sub.send(messages[announcement_id]) != 0:
                        break
                    await Subscribe.update_data_by_data({"id": sub.id}, {"extra_message": str(announcement_id)})
            except Exception:
                logger.exception(f"[JFZRUID] 订阅 {sub.id} 推送失败，保留进度供下轮重试")
