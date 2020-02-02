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
    # await session.send('[CQ:image,file=test.png]')
    # await session.send(filename)


# weather.args_parser 装饰器将函数声明为 weather 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
# @setu.args_parser
# async def _(session: CommandSession):
#     # 去掉消息首尾的空白符
#     stripped_arg = session.current_arg_text.strip()

#     if session.is_first_run:
#         # 该命令第一次运行（第一次进入命令会话）
#         if stripped_arg:
#             # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
#             # 例如用户可能发送了：天气 南京
#             session.state['city'] = stripped_arg
#         return

#     if not stripped_arg:
#         # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
#         # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
#         session.pause('要查询的城市名称不能为空呢，请重新输入')

#     # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
#     session.state[session.current_key] = stripped_arg