from PIL import Image

from gsuid_core.sv import SV, get_plugin_available_prefix
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.help.utils import register_help
from gsuid_core.message_models import Button

from .get_help import ICON, get_help

sv_help = SV("JFZRUID帮助")


@sv_help.on_fullmatch(("帮助", "幫助"), block=True)
async def send_help(bot: Bot, ev: Event) -> None:
    prefix = get_plugin_available_prefix("JFZRUID")
    buttons = [
        [
            Button("公告列表", f"{prefix}公告列表", action=2),
            Button("最新公告", f"{prefix}公告", action=2),
        ]
    ]
    if ev.user_pm <= 3:
        buttons.append(
            [
                Button("订阅公告", f"{prefix}订阅公告", action=2, permisson=1),
                Button("取消订阅", f"{prefix}取消订阅公告", action=2, permisson=1),
                Button("清理缓存", f"{prefix}清理公告缓存", action=2, permisson=1),
            ]
        )
    await bot.send_option(await get_help(ev.user_pm), buttons)


register_help("JFZRUID", f"{get_plugin_available_prefix('JFZRUID')}帮助", Image.open(ICON))
