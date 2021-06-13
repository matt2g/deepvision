from lcu_driver import Connector
from urllib import parse
import json, os
from summoners import Summoner, Runepage, Game

with open('dragontail-11.12.1/11.12.1/data/en_US/champion.json', 'rb') as f:
    champ_data = json.load(f)
    champ_dict = {}

for champ in champ_data['data']:
    champ_dict[champ_data['data'][champ]['key']] = champ


def get_lockfile():
    import os
    path = os.path.join('/home/matt/Games/league-of-legends/drive_c/Riot Games/League of Legends/', 'lockfile')
    if os.path.isfile(path):
        file = open(path, 'r')
        text = file.readline()
        file.close()
        return text
    return None


summoners = []
connector = Connector(str=get_lockfile())
game = Game()


@connector.ready
async def connect(connection):
    print('LCU connection ready')


@connector.ws.register('/lol-champ-select/v1/session', event_types=('CREATE',))
async def create_game(connection, event):
    await game.create_game(connection)
    # await game.get_op_gg_info()

@connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
async def get_selection(connection, event):
    print(event.data)

@connector.close
async def disconnect(connection):
    print('The client was closed')
    await connector.stop()


connector.start()
