# coding=utf-8
import nonebot
import os
import sapphirebot.config as config
import logging
from datetime import datetime
from sapphirebot.utils.singleton import singleton

@singleton
class App(object):
    def __init__(self):
        self.bot = None 
        self.root_dir = os.path.abspath(os.path.join(os.path.realpath(__file__), '../..'))
        self.log_dir = os.path.join(self.root_dir, 'log')
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)

        time_now = datetime.now()
        log_file = os.path.join(self.log_dir, time_now.strftime(r'%Y-%m-%d_%H%M%S.log'))
        logging.basicConfig(filename=log_file)

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