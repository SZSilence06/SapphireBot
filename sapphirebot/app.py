# coding=utf-8
import nonebot
import os
import logging
import importlib
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

        # configure logger
        self.logger = logging.getLogger('SapphireBot')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(
            fmt='[%(asctime)s - %(name)s] %(levelname)s : %(message)s'
        )) 
        self.logger.addHandler(stream_handler)

    def run(self):
        nonebot.init(self._get_config())
        nonebot.load_builtin_plugins()
        nonebot.load_plugins(
            os.path.join(os.path.dirname(__file__), 'plugins'),
            'sapphirebot.plugins'
        )

        self.bot = nonebot.get_bot()
        nonebot.run()

    def get_bot(self):
        return self.bot

    def _get_config(self):
        # default config
        config = importlib.import_module('sapphirebot.config')
        
        # 读取自定的配置并改写
        try:
            from sapphirebot.etc.conf_mode import CONFIG_MODULE
            custom_config = importlib.import_module(CONFIG_MODULE)
            for key, value in custom_config.__dict__.items():
                setattr(config, key, value)
        except ImportError:
            pass
        
        return config