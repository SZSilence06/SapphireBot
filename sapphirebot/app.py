# coding=utf-8
import nonebot
import os
import sapphirebot.config as config
from sapphirebot.utils.singleton import singleton

@singleton
class App(object):
    def __init__(self):
        self.bot = None 

    def run(self):
        nonebot.init(config)
        nonebot.load_builtin_plugins()
        nonebot.load_plugins(
            os.path.join(os.path.dirname(__file__), 'plugins'),
            'sapphirebot.plugins'
        )

        self.bot = nonebot.get_bot()
        nonebot.run()

    def get_bot(self):
        return self.bot