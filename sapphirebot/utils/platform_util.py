# coding=utf-8
import platform

_system = platform.system()

def is_win():
    return _system == 'Windows'

def is_mac():
    return _system == 'Darwin'

def is_linux():
    return _system == 'Linux'