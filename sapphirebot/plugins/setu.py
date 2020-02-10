# coding=utf-8
from nonebot import on_command, CommandSession, permission, CQHttpError
from sapphirebot.utils.image_picker import ImagePicker
from sapphirebot.app import App

__plugin_name__ = '涩图'

g_image_picker = ImagePicker('setu')

@on_command('setu', only_to_me=False)
async def setu(session: CommandSession):
    # 随机选取一张图
    filename = g_image_picker.pick_one_image()
    # 向用户发送图片
    try:
        await session.send('[CQ:image,file=%s]' % filename, ignore_failure=False)
    except CQHttpError as e:
        App.get_instance().logger.error('setu: %s', str(e))
        await session.send(str(e))
