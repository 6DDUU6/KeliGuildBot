# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging, BotAPI
from botpy.message import Message
from botpy.types.message import Embed, EmbedField
from botpy.ext.command_util import Commands
from botpy.ext.cog_yaml import read
from botpy.types.message import Reference, MarkdownPayload, MessageMarkdownParams
from botpy.errors import AuthenticationFailedError
from query import GetUidInfo
from redis_manager import redisManager

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()


async def is_admin(api: BotAPI, message: Message):
    try:
        if "2" in message.member.roles or "4" in message.member.roles:
            return True
    except Exception as e:
        pass
    await api.post_message(channel_id=message.channel_id, content="荣誉骑士哥哥/姐姐,你好像没有频道管理权限哦~可莉还不能帮你", msg_id=message.id)
    return False


async def is_channel_admin(api: BotAPI, message: Message):
    try:
        if "2" in message.member.roles or "4" in message.member.roles or "5" in message.member.roles:
            return True
    except Exception as e:
        pass
    await api.post_message(channel_id=message.channel_id, content="荣誉骑士哥哥/姐姐,你好像没有频道管理或子频道管理权限哦~可莉还不能帮你", msg_id=message.id)
    return False


def handle_return(data, head_url):
    if "error" in data:
        return "发生错误:" + data["error"]
    params = []
    # params.append(MessageMarkdownParams(key = "uidinfo", values = [data["playerInfo"]["nickname"] + " " + str(data["playerInfo"]["level"]) + "级"]))
    # params.append(MessageMarkdownParams(key = "imgsize", values = "[head #100px #100px]"))
    # params.append(MessageMarkdownParams(key = "imgurl", values = "head_url"))
    # params.append(MessageMarkdownParams(key = "uidinfo2", values = "成就 " + str(data["playerInfo"]["finishAchievementNum"]) + " 深渊" + str(data["playerInfo"]["towerFloorIndex"]) + "-" + str(data["playerInfo"]["towerLevelIndex"])))
    params.append(MessageMarkdownParams(key = "uidinfo3", values = "这里还没写"))
    md = MarkdownPayload(custom_template_id = "102020010_1663659611", params = params)
    return md


@Commands("推送直播")
async def push(api: BotAPI, message: Message, params=None):
    if not await is_channel_admin(api, message):
        return True
    # TODO: 检验是否为直播子频道
    redis = redisManager()
    parent_id = await redis.get_value(message.guild_id + "_push_parent_id")
    if parent_id is None:
        await api.post_message(channel_id=message.channel_id, content="先要设置推送分组才可以推送~", msg_id=message.id)
        return True
    parent_id = parent_id.decode('utf-8')
    position = await redis.increase_value(message.guild_id + "_position_push")
    if position < 10:
        position = 10
        await redis.set_key(message.guild_id + "_position_push", 10)
    try:
        await api.update_channel(channel_id=message.channel_id, parent_id=parent_id, position=position)
    except AuthenticationFailedError:
        await api.post_message(channel_id=message.channel_id, content="请求移动分组失败(修改子频道接口为私域api),需要在本机器人的私域频道进行操作(沙箱频道id:4294280837,私域灰度频道id:4294958380)", msg_id=message.id)
        return True
    await api.post_message(channel_id=message.channel_id, content="可莉已经帮你把子频道移动到推送分组啦<emoji:338>", msg_id=message.id)
    return True


@Commands("取消推送")
async def unpush(api: BotAPI, message: Message, params=None):
    if not await is_channel_admin(api, message):
        return True
    # TODO: 检验是否为直播子频道
    redis = redisManager()
    parent_id = await redis.get_value(message.guild_id + "_privite_parent_id")
    if parent_id is None:
        await api.post_message(channel_id=message.channel_id, content="先要设置专属分组才可以移动~", msg_id=message.id)
        return True
    parent_id = parent_id.decode('utf-8')
    position = await redis.increase_value(message.guild_id + "_position_privite")
    if position < 30:
        position = 30
        await redis.set_key(message.guild_id + "_position_privite", 30)
    try:
        await api.update_channel(channel_id=message.channel_id, parent_id=parent_id, position=position)
    except AuthenticationFailedError:
        await api.post_message(channel_id=message.channel_id, content="请求移动分组失败(修改子频道接口为私域api),需要在本机器人的私域频道进行操作(沙箱频道id:4294280837,私域灰度频道id:4294958380)", msg_id=message.id)
        return True
    await api.post_message(channel_id=message.channel_id, content="荣誉骑士哥哥/姐姐这次直播辛苦啦<emoji:332>可莉已经帮你把子频道移回专属分组了", msg_id=message.id)
    return True


@Commands("设置推送分组")
async def setPushParent(api: BotAPI, message: Message, params=None):
    if not await is_admin(api, message):
        return True
    redis = redisManager()
    parent_id = await redis.get_value(message.guild_id + "_push_parent_id")
    if parent_id is not None and params != "-f":
        await api.post_message(channel_id=message.channel_id,
                               content="可莉已经记住了一个推送分组啦,再记的话可莉要背不下来了", msg_id=message.id)
        return True
    ret = await api.get_channel(channel_id=message.channel_id)
    parent_id = ret["parent_id"]
    await redis.set_key(message.guild_id + "_push_parent_id", parent_id)
    await api.post_message(channel_id=message.channel_id,
                           content="已成功设置当前分组为推送分组,推送直播的时候可莉会把子频道移动到这个分组哦~", msg_id=message.id)
    return True


@Commands("设置专属分组")
async def setPriviteParent(api: BotAPI, message: Message, params=None):
    if not await is_admin(api, message):
        return True
    redis = redisManager()
    parent_id = await redis.get_value(message.guild_id + "_privite_parent_id")
    if parent_id is not None and params != "-f":
        await api.post_message(channel_id=message.channel_id,
                               content="可莉已经记住了一个专属分组啦,再记的话可莉要背不下来了", msg_id=message.id)
        return True
    ret = await api.get_channel(channel_id=message.channel_id)
    parent_id = ret["parent_id"]
    await redis.set_key(message.guild_id + "_privite_parent_id", parent_id)
    await api.post_message(channel_id=message.channel_id,
                           content="已成功设置当前分组为专属分组,不直播的时候可莉会把子频道移动到这个分组哦~", msg_id=message.id)
    return True


@Commands("info")
async def getUid(api: BotAPI, message: Message, params=None):
    if not await is_admin(api, message):
        return True
    ret = await GetUidInfo(params)
    content = handle_return(ret, message.author.avatar)
    if isinstance(content, str):
        await api.post_message(channel_id=message.channel_id,
                           content=content,
                           message_reference=Reference(message_id=message.id),
                           msg_id=message.id)
    else:
        print(content)
        await api.post_message(channel_id=message.channel_id,
                           markdown=content)
    return True


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_message_create(self, message: Message, params=None):
        try:
            _log.info("收到消息: " + message.content)
        except TypeError:
            return
        # 注册指令handler
        handlers = [
            getUid,
            setPushParent,
            setPriviteParent,
            push,
            unpush,
        ]
        for handler in handlers:
            if await handler(api=self.api, message=message):
                return


if __name__ == "__main__":
    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], token=test_config["token"])
