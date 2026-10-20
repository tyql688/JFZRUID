from typing import Literal, Annotated
from datetime import datetime

import httpx
from pydantic import Field, BaseModel, ConfigDict
from async_lru import alru_cache

NEWS_URL = "https://www.kritika.hk/news"
API_URL = "https://webapi.pxegame.com/kritika/webapi"
CACHE_SECONDS = 3600


class AnnouncementNotFoundError(Exception):
    pass


class Announcement(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int = Field(gt=0)
    title: str = Field(min_length=1)
    showtime: datetime
    typeid: int

    @property
    def url(self) -> str:
        return f"{NEWS_URL}/notice/{self.id}.html"


class NewsPage(BaseModel):
    items: list[Announcement] = Field(alias="list")
    all_pages: int = Field(alias="allPage", ge=1)


class AnnouncementDetail(Announcement):
    content: str = Field(min_length=1)


class NewsResponse(BaseModel):
    code: Literal[200]
    data: NewsPage


class DetailResponse(BaseModel):
    code: Literal[200]
    data: AnnouncementDetail | Annotated[list[None], Field(max_length=0)]


async def _request(endpoint: str, payload: dict[str, str | int]) -> bytes:
    async with httpx.AsyncClient(
        timeout=15.0,
        headers={
            "GameId": "101",
            "Origin": "https://www.kritika.hk",
            "Referer": f"{NEWS_URL}/notice",
        },
    ) as client:
        response = await client.post(
            f"{API_URL}/{endpoint}",
            json=payload,
        )
        response.raise_for_status()
    return response.content


@alru_cache(maxsize=1, ttl=CACHE_SECONDS)
async def fetch_announcements() -> tuple[Announcement, ...]:
    items: dict[int, Announcement] = {}
    page_number = 1
    while True:
        content = await _request(
            "newsListV2",
            {"page": page_number, "type": "72", "isDetail": 1, "pageSize": 50},
        )
        page = NewsResponse.model_validate_json(content).data
        items.update((item.id, item) for item in page.items)
        if page_number >= page.all_pages:
            break
        page_number += 1
    return tuple(sorted(items.values(), key=lambda item: (item.showtime, item.id), reverse=True))


@alru_cache(maxsize=32, ttl=CACHE_SECONDS)
async def fetch_detail(announcement_id: int) -> AnnouncementDetail:
    content = await _request("newsdetail", {"id": announcement_id})
    detail = DetailResponse.model_validate_json(content).data
    if isinstance(detail, list) or detail.typeid != 72:
        raise AnnouncementNotFoundError(f"未找到公告 {announcement_id}。")
    return detail
