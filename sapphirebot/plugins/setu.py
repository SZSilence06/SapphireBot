from nonebot import on_command, CommandSession, permission, get_bot
import os
import random

__plugin_name__ = '涩图'

class ImagePicker(object):
    def __init__(self):
        self.cq_dir = get_bot().config.CQ_DIR
        self.img_dir = os.path.join(self.cq_dir, 'data', 'image')
        self.setu_dir = os.path.join(self.img_dir, 'setu')
        self.images = []

        self.load_images()

    def load_images(self):
        for root, dirs, filenames in os.walk(self.setu_dir):
            for f in filenames:
                full_path = os.path.join(root, f)
                self.images.append(os.path.relpath(full_path, self.img_dir))

    def pick_one_image(self):
        return random.choice(self.images)

g_image_picker = ImagePicker()

@on_command('setu', only_to_me=False)
async def setu(session: CommandSession):
    # 随机选取一张图
    filename = g_image_picker.pick_one_image()
    # 向用户发送图片
    await session.send('[CQ:image,file=%s]' % filename)