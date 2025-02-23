import httpx
import feedparser
from typing import List
from urllib.parse import quote

from nonebot.log import logger

from .rss_class import RSS


async def get_rss_info(url: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=20)
            result = resp.text
        return feedparser.parse(result)
    except Exception as e:
        logger.warning(f"Error in get_rss_info({url}): {e}")
        return {}


async def update_rss_info(rss: RSS) -> bool:
    info = await get_rss_info(rss.url)
    if not info:
        return False
    rss.title = info["feed"].get("title", "")
    rss.link = info["feed"].get("link", "")
    try:
        rss.logo = info["feed"]["image"]["href"]
    except:
        rss.logo = (
            f"https://ui-avatars.com/api/?background=random&name={quote(rss.title)}"
        )
    rss.rights = info["feed"].get("rights", "")
    return True


async def update_rss(rss: RSS) -> List[dict]:
    info = await get_rss_info(rss.url)
    if not info:
        return []
    new_entries = []
    entries = info.get("entries")
    if not entries:
        return []
    for entry in entries[::-1]:
        try:
            time = RSS.parse_time(entry["published_parsed"])
            if time <= rss.last_update:
                continue
            title = entry["title"]
            summary = entry["summary"]
            link = entry["link"]
            authors = []
            tags = []
            try:
                for author in entry["authors"]:
                    authors.append(author["name"])
                for tag in entry["tags"]:
                    tags.append(tag["term"])
            except:
                pass
            new_entries.append(
                {
                    "time": time.strftime("%c"),
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "author": ", ".join(authors),
                    "tags": ", ".join(tags),
                }
            )
        except:
            continue
    try:
        newest_time = RSS.parse_time(entries[0]["published_parsed"])
        if newest_time > rss.last_update:
            rss.last_update = newest_time
    except:
        rss.last_update = RSS.time_now()
    return new_entries
