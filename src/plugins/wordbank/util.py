import re
from nonebot.adapters.cqhttp import MessageEvent


def parse_user(msg: str, nickname: str) -> str:
    return re.sub(r'/user', nickname, msg)


def parse_at_user(msg: str, sender_id: int) -> str:
    return re.sub(r'/atuser', f"[CQ:at,qq={sender_id}]", msg)


def parse(msg: str, event: MessageEvent) -> str:
    nickname = event.sender.card or event.sender.nickname
    sender_id = event.sender.user_id
    return parse_at_user(parse_user(msg, nickname), sender_id)
