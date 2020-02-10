# coding=utf-8
from nonebot import on_command, CommandSession, permission, CQHttpError
from sapphirebot.app import App
from typing import Dict
import datetime
import hashlib

__plugin_name__ = 'RBQ指数'

@on_command('rbq', only_to_me=False, permission=permission.GROUP)
async def rbq(session: CommandSession):
    group_id = session.ctx.get('group_id')
    if group_id is None:
        return

    try:
        # 获取群成员列表
        members = await session.bot.get_group_member_list(group_id=group_id)
        member_dict = {}
        for member in members:
            user_id = member.get('user_id')
            if not user_id:
                continue
            if user_id == session.bot.config.BOT_QQ:
                # 是机器人自己
                continue

            member_dict[user_id] = member
            member.update({
                'rbq_score': compute_rbq_score(user_id)
            })

        # 按分数从高到低排序
        sorted_members = {k:v for k,v in sorted(member_dict.items(), 
            key=lambda item: item[1]['rbq_score'], reverse=True)}

        # 返回结果
        result = '今日群内RBQ指数为：\n'
        result += '-------------------------\n'

        for user_id, member in sorted_members.items():
            name = member['card']
            if not name:
                name = member['nickname']
            result += "{0:<{2}}\t{1}%\n".format(name, member['rbq_score'], 20 - len(name.encode('GBK')) + len(name))

        result += '-------------------------\n'
        result += '今日群友共用RBQ为 [CQ:at,qq=%d]' % next(iter(sorted_members.keys()))
        
        # 发送结果
        await session.send(result)

    except CQHttpError as e:
        App.get_instance().logger.error('rbq: %s', str(e))
        await session.send(str(e))

def compute_rbq_score(user_id: int):
    '''
    计算RBQ指数
    算法为将当天日期转换为字符串后，加上user_id来做哈希
    '''
    tzinfo = datetime.timezone(offset=datetime.timedelta(hours=8)) # 东八区
    today = datetime.datetime.now(tzinfo)
    today_string = today.strftime(r'%Y-%m-%d_')
    full_string = (today_string + str(user_id)).encode('utf-8')

    # 计算hash
    hash_hex = hashlib.md5(full_string).hexdigest()
    hash_value = int(hash_hex, 16)
    return hash_value % 101

# if __name__ == '__main__':
#     print(len('群主专属RBQ'.encode('utf-8')))
#     result = ''
#     sorted_members = {
#         'Clainie': 22,
#         '群主专属RBQ': 30,
#         'SZ_Silence06':27,
#         'SapphireBot_dev': 34
#     }
#     for name, score in sorted_members.items():
#         result += "{0:<{2}}\t{1}%\n".format(name, score, 25 - len(name.encode('utf-8')) + len(name))
#     print(result)
