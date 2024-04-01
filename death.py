# coding=utf-8
import re

import minecraft_data_api as api
from mcdreforged.api.command import Literal
from mcdreforged.api.all import new_thread
from mcdreforged.api.rtext import RText, RTextList, RAction, RColor

PLUGIN_METADATA = {
    'id': 'death',
    'version': '0.0.1',
    'name': 'MCDR-death',
    'description': '一个处理死亡事件的插件，支持返回死亡点，死亡嘲讽等功能',
    'author': 'Kuroikage1732, Geniucker',
    'link': 'https://github.com',
    'dependencies': {
        'mcdreforged': '>=2.0.0',
        'minecraft_data_api': '*',
        'death_api': '*'
    }
}

#是否允许使用!!back
EN_BACK = 1

death_player = {}
dim_tran = {
    0: '§a主世界§f',
    -1: '§c地狱§f',
    1: '§6末地§f',
    'minecraft:overworld': '§a主世界§f',
    'minecraft:the_nether': '§c地狱§f',
    'minecraft:the_end': '§6末地§f'
}
tp_tran = {
    0: 'minecraft:overworld',
    -1: 'minecraft:the_nether',
    1: 'minecraft:overworld',
    'minecraft:overworld': 'minecraft:overworld',
    'minecraft:the_nether': 'minecraft:the_nether',
    'minecraft:the_end': 'minecraft:the_end'
}

@new_thread(PLUGIN_METADATA['id'])
def on_death(server, death_message: str):
    player = death_message.split( )[0]

    # irony
    for i in IRONIES:
        if re.search(i, death_message):
            server.tell(player, IRONIES[i])
            break

    pos = api.get_player_info(player, 'Pos')
    xyz = str(int(pos[0])) + ' ' + str(int(pos[1])) + ' ' + str(int(pos[2]))
    dim = api.get_player_info(player, 'Dimension')
    if EN_BACK == 1:
        death_player[player] = [xyz, dim]
        # msg = ('您刚刚在',dim_tran[dim] , ' ', xyz, ' 处死亡。发送 "!!back" 回到死亡点')
        msg = RTextList(
            RText(f'您刚刚在 {dim_tran[dim]} {xyz} 处死亡。发送 '),
            RText('!!back', color=RColor.green).c(RAction.suggest_command, '!!back'),
            RText(' 回到死亡点(命令可点击)')
        )
    else:
        msg = ('您刚刚在',dim_tran[dim] , ' ', xyz, ' 处死亡。')
    server.tell(player, msg)

# !!back 命令的回调
def back_callback(src):
    server = src.get_server()
    if src.is_player and src.player in death_player.keys():
        server.execute('execute in {} run tp {} {}'.format(tp_tran[death_player[src.player][1]], src.player, death_player[src.player][0]))
        server.tell(src.player, '已传送到死亡点')
        del death_player[src.player]
    else:
        server.tell(src.player, '未查询到死亡记录')

def kill_callback(src):
    server = src.get_server()
    if src.is_player:
        server.execute('kill {}'.format(src.player))

def on_player_left(server, player):
    if player in death_player.keys():
        del death_player[player]

def on_load(server, old_module):
    server.register_help_message('!!back', '显示与返回死亡点')
    server.register_help_message('!!kill', '自杀')
    server.register_command(
        Literal("!!back").runs(back_callback)
    )
    server.register_command(
        Literal("!!kill").runs(kill_callback)
    )
    server.register_event_listener('death_api.on_death_message', on_death)

IRONIES = {
    'shot by Skeleton': '就不能做个盾牌吗',
    'blown up by Creeper': '菜就多练，还能被苦力怕打到',
    'slain by Zombie': '不会吧不会吧，不会有人打不过僵尸吧',
    'starved to death': '啧啧啧，怎么穷到都饿死了',
    'fell from a high place': '你是怎么做到在允许飞行的服务器里摔死的',
    'was killed$': '你怎么又自杀了'
}
