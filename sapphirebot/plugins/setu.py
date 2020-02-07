from nonebot import on_command, CommandSession, permission
from sapphirebot.utils.image_picker import ImagePicker

__plugin_name__ = '涩图'

g_image_picker = ImagePicker('setu')

@on_command('setu', only_to_me=False)
async def setu(session: CommandSession):
    # 随机选取一张图
    filename = g_image_picker.pick_one_image()
    # 向用户发送图片
    await session.send('[CQ:image,file=%s]' % filename)