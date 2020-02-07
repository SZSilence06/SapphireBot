from nonebot import on_command, on_natural_language, permission, NLPSession, IntentCommand
from typing import Dict
from dataclasses import dataclass
from datetime import datetime, timedelta

__plugin_name__ = '复读姬'

@dataclass
class LastMsgInfo(object):
    '''
    记录群聊中最近一次发言的信息
    '''
    user_id: int = 0   # 最近一次说话的用户
    msg: str = ""   # 最近一次说的话
    timestamp: datetime = None # 最近一次说话的时间戳
    repeat_time: int = 0  # 复读次数

g_group_last_msg : Dict[int, LastMsgInfo] = {}

@on_natural_language(only_to_me=False, permission=permission.GROUP)
async def do_repeat(session: NLPSession):
    # 获取群号
    group_id = session.ctx.get('group_id')
    if group_id is None:
        return
    
    # 获取用户id
    user_id = session.ctx.get('user_id')
    if user_id is None:
        return

    # 时间戳
    cur_time = datetime.now()
    #消息
    msg = session.msg

    last_msg = g_group_last_msg.get(group_id)

    # 更新最近一次消息信息
    cur_msg = LastMsgInfo(user_id=user_id, msg=msg, timestamp=cur_time, repeat_time=1)
    g_group_last_msg[group_id] = cur_msg

    if last_msg is None:
        return
    if last_msg.msg != msg:
        return
    cur_msg.repeat_time = last_msg.repeat_time + 1

    if last_msg.user_id == user_id:
        return
    if (last_msg.timestamp - cur_time) / timedelta(minutes=1) > 30:
        # 间隔超过30分钟的不跟读
        return 
    if cur_msg.repeat_time == 2:
        # 复读
        return IntentCommand(
            100.0,
            'echo',
            args={'message': msg}
        )
    
