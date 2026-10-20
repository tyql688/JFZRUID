from html import escape
from base64 import b64encode
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import httpx
from bs4 import Comment, BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from opencc import OpenCC
from async_lru import alru_cache

from gsuid_core.pool import to_thread
from gsuid_core.utils.html_render import render_html_to_bytes
from gsuid_core.utils.html_render.table_rewrite import rewrite_tables_for_takumi

from .api import NEWS_URL, CACHE_SECONDS, Announcement, AnnouncementDetail

_ROOT = Path(__file__).parent
_TEMPLATES = Environment(loader=FileSystemLoader(_ROOT.parent / "templates"), autoescape=True)
_CONVERTER = OpenCC("t2s")


def _simplify(text: str) -> str:
    result = _CONVERTER.convert(text)
    if not isinstance(result, str):
        raise TypeError("OpenCC 未返回文本。")
    return result


@to_thread
def _document(title: str, meta: str, content: str, footer: str) -> str:
    banner = b64encode((_ROOT / "texture2d/banner.jpg").read_bytes()).decode()
    logo = b64encode((_ROOT / "texture2d/logo.png").read_bytes()).decode()
    return _TEMPLATES.get_template("news.html.j2").render(
        title=title,
        meta=meta,
        content=content,
        footer=footer,
        banner=f"data:image/jpeg;base64,{banner}",
        logo=f"data:image/png;base64,{logo}",
    )


async def _render(title: str, meta: str, content: str, footer: str) -> bytes:
    html = await _document(title, meta, content, footer)
    return await render_html_to_bytes(html, max_width=840, default_font_size=24, image_format="png")


@alru_cache(maxsize=4, ttl=CACHE_SECONDS)
async def render_list(items: tuple[Announcement, ...], prefix: str) -> bytes:
    rows = "".join(
        '<div class="news-row">'
        f'<div class="row-meta"><span class="id">ID {item.id}</span>'
        f"<span>{item.showtime:%Y-%m-%d}</span></div>"
        f'<div class="row-title">{escape(_simplify(item.title))}</div>'
        f'<div class="command">{escape(prefix)}公告{item.id}</div></div>'
        for item in items
    )
    return await _render(
        "公告列表",
        f"最近 {len(items)} 条 · 官网公告",
        rows,
        f"{prefix}公告 查看最新详情  /  {prefix}公告ID 查看指定公告",
    )


async def _article_html(content: str) -> str:
    soup = BeautifulSoup(content, "html.parser")
    for tag in soup.select("script, style, iframe, object, embed, video, audio"):
        tag.decompose()
    async with httpx.AsyncClient(timeout=15.0) as client:
        for tag in soup.find_all(True):
            attrs = tag.attrs
            tag.attrs = {}
            if tag.name == "img":
                src = attrs["src"] if "src" in attrs else ""
                url = urljoin(NEWS_URL, src) if isinstance(src, str) else ""
                parsed = urlsplit(url)
                if parsed.scheme != "https" or parsed.hostname not in {"img.youxi290.com", "www.kritika.hk"}:
                    tag.replace_with(soup.new_string("【配图请查看原文】"))
                    continue
                response = await client.get(url)
                response.raise_for_status()
                media_type = response.headers["content-type"].split(";")[0]
                tag["src"] = f"data:{media_type};base64,{b64encode(response.content).decode()}"
            elif tag.name in {"td", "th"}:
                for attr in ("colspan", "rowspan"):
                    if attr in attrs:
                        value = attrs[attr]
                        if isinstance(value, str) and value.isdigit():
                            tag[attr] = value
            elif tag.name not in {
                "p",
                "div",
                "span",
                "strong",
                "b",
                "em",
                "i",
                "u",
                "s",
                "br",
                "hr",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "ul",
                "ol",
                "li",
                "blockquote",
                "table",
                "thead",
                "tbody",
                "tfoot",
                "tr",
                "a",
            }:
                tag.unwrap()
        for text in soup.find_all(string=True):
            if isinstance(text, Comment):
                text.extract()
            else:
                text.replace_with(_simplify(str(text)))
    return rewrite_tables_for_takumi(str(soup))


@alru_cache(maxsize=16, ttl=CACHE_SECONDS)
async def render_detail(detail: AnnouncementDetail) -> bytes:
    content = await _article_html(detail.content)
    return await _render(
        _simplify(detail.title),
        f"公告 ID {detail.id}  ·  {detail.showtime:%Y-%m-%d %H:%M}",
        f'<div class="article">{content}</div>',
        f"疾风之刃 · 官网公告  /  ID {detail.id}",
    )
