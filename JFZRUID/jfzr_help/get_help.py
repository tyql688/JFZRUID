from pathlib import Path

from PIL import Image
from msgspec.json import decode

from gsuid_core.sv import get_plugin_available_prefix
from gsuid_core.pool import to_thread
from gsuid_core.help.model import PluginHelp
from gsuid_core.help.draw_new_plugin_help import get_new_help

from ..version import JFZRUID_version

ICON = Path(__file__).parents[2] / "ICON.png"
HELP_DATA = Path(__file__).parent / "help.json"
TEXT_PATH = Path(__file__).parent / "texture2d"
ICON_PATH = Path(__file__).parent / "icon_path"
plugin_help = decode(HELP_DATA.read_bytes(), type=dict[str, PluginHelp])


@to_thread
def _load_image(path: Path, size: tuple[int, int] | None = None) -> Image.Image:
    with Image.open(path) as image:
        return image.resize(size) if size else image.convert("RGBA")


async def get_help(pm: int) -> bytes | str:
    return await get_new_help(
        plugin_name="JFZRUID",
        plugin_info={f"v{JFZRUID_version}": "#bc3b27"},
        plugin_icon=await _load_image(ICON),
        plugin_help=plugin_help,
        plugin_prefix=get_plugin_available_prefix("JFZRUID"),
        help_mode="dark",
        banner_bg=await _load_image(TEXT_PATH / "banner_bg.png", (1545, 515)),
        banner_sub_text="疾风之刃 · 公告查询与订阅",
        help_bg=await _load_image(TEXT_PATH / "bg.png"),
        cag_bg=await _load_image(TEXT_PATH / "cag_bg.png", (1545, 100)),
        item_bg=await _load_image(TEXT_PATH / "item.png", (490, 175)),
        icon_path=ICON_PATH,
        banner_title_color=(255, 244, 229),
        banner_sub_color=(230, 211, 199),
        cag_title_color=(255, 171, 103),
        cag_sub_color=(220, 208, 200),
        plugin_icon_size=196,
        enable_cache=False,
        column=3,
        pm=pm,
    )
