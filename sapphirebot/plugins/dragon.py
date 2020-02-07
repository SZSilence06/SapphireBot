from nonebot import on_command, CommandSession, permission
from sapphirebot.utils.image_picker import ImagePicker

__plugin_name__ = '龙王'

g_image_picker = ImagePicker('dragon')

@on_command('dragon', only_to_me=False, permission=permission.GROUP)
async def dragon(session: CommandSession):
    # 随机选取一张图
    filename = g_image_picker.pick_one_image()
    # 向用户发送图片
    await session.send('[CQ:image,file=%s]' % filename)