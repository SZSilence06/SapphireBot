from nonebot import on_command, CommandSession, permission, CQHttpError
from sapphirebot.utils.image_picker import ImagePicker
from sapphirebot.app import App

__plugin_name__ = '龙王'

g_image_picker = ImagePicker('dragon')

@on_command('dragon', only_to_me=False, permission=permission.GROUP)
async def dragon(session: CommandSession):
    # 随机选取一张图
    filename = g_image_picker.pick_one_image()
    # 向用户发送图片
    try:
        await session.send('[CQ:image,file=%s]' % filename, ignore_failure=False)
    except CQHttpError as e:
        App.get_instance().logger.error('dragon: %s', str(e))
        await session.send(str(e))