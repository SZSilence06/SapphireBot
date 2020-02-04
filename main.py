# coding=utf-8
from sapphirebot.app import App
from sapphirebot.utils import platform_util
import sys
import os

def print_usage():
    print('''Usage: python3 main.py [start|stop|restart]
examples:
    python3 main.py                Run in foreground.
    python3 main.py start          Run as background service.
    python3 main.py stop           Stop the service.
    python3 main.py restart        Restart the service.'''
)

def start_bot():
    App.get_instance().run()

if __name__ == '__main__':
    if platform_util.is_win():
        start_bot()
    else:
        # use daemon process for macOS and Linux
        from thirdparty.python_daemon.daemon import Daemon
        class MyDaemon(Daemon):
            def __init__(self):
                root_dir = os.path.dirname(os.path.realpath(__file__))
                tmp_dir = os.path.join(root_dir, 'tmp')
                if not os.path.exists(tmp_dir):
                    os.mkdir(tmp_dir)
                super().__init__(pidfile=os.path.join(tmp_dir, 'bot.pid'))

            def run(self):
                start_bot()
       
        if len(sys.argv) == 1:
            start_bot()
        else:
            arg = sys.argv[1]
            if arg == 'start':
                MyDaemon().start()
            elif arg == 'stop':
                MyDaemon().stop()
            elif arg == 'restart':
                MyDaemon().restart()
            else:
                print('wrong argument!')
                print_usage()

