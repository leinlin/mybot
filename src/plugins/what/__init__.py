import re
from nonebot.plugin import PluginMetadata
from nonebot import on_keyword, on_command
from nonebot.params import CommandArg, EventPlainText, EventToMe
from nonebot.adapters.onebot.v11 import Message

from .data_source import get_content

__plugin_meta__ = PluginMetadata(
    name="百科",
    description="缩写查询、梗百科",
    usage=(
        "1. 百科 {keyword}，来源为nbnhhsh、小鸡词典、百度百科\n"
        "2. {keyword} 是啥/是什么，来源为nbnhhsh、小鸡词典\n"
        "3. 缩写 {keyword}，来源为nbnhhsh"
    ),
    extra={
        "example": "缩写 xswl\nxswl 是啥\n百科 洛天依",
    },
)


commands = {"是啥", "是什么", "是谁"}
what = on_keyword(commands, priority=14)
baike = on_command("baike", aliases={"what", "百科"}, block=True, priority=13)
nbnhhsh = on_command("nbnhhsh", aliases={"缩写"}, block=True, priority=13)


@what.handle()
async def _(msg: str = EventPlainText(), to_me: bool = EventToMe()):
    def split_command(msg):
        for command in commands:
            if command in msg:
                prefix, suffix = re.split(command, msg)
                return prefix, suffix
        return "", ""

    msg = msg.strip().strip(".>,?!。，（）()[]【】")
    prefix_words = ["这", "这个", "那", "那个", "你", "我", "他", "它"]
    suffix_words = ["意思", "梗", "玩意", "鬼"]
    prefix, suffix = split_command(msg)
    if (not prefix or prefix in prefix_words) or (
        suffix and suffix not in suffix_words
    ):
        what.block = False
        await what.finish()
    keyword = prefix

    if to_me:
        res = await get_content(keyword)
    else:
        res = await get_content(keyword, sources=["jiki", "nbnhhsh"])

    if res:
        what.block = True
        await what.finish(res)
    else:
        what.block = False
        await what.finish()


@baike.handle()
async def _(msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        await baike.finish()

    res = await get_content(keyword)
    if res:
        await baike.finish(res)
    else:
        await baike.finish("找不到相关的条目")


@nbnhhsh.handle()
async def _(msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        await nbnhhsh.finish()
    if not re.fullmatch(r"[a-zA-Z]+", keyword):
        await nbnhhsh.finish()

    res = await get_content(keyword, sources=["nbnhhsh"])
    if res:
        await nbnhhsh.finish(res)
    else:
        await nbnhhsh.finish("找不到相关的缩写")
