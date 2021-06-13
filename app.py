from lcu_driver import Connector
from summoners import Game
from configparser import ConfigParser
import pprint as pp

config_object = ConfigParser()
config_object.read('config.ini')
client_info = config_object["CLIENT"]


def get_lockfile():
    import os
    path = os.path.join(client_info['installation_path'], 'lockfile')
    if os.path.isfile(path):
        file = open(path, 'r')
        text = file.readline()
        file.close()
        return text
    return None


connector = Connector(str=get_lockfile())
game = Game()


@connector.ready
async def connect(connection):
    print('LCU connection ready')


@connector.ws.register('/lol-champ-select/v1/session', event_types=('CREATE',))
async def create_game(connection, event):
    await game.create_game(connection)
    game.get_op_gg_info()

    @connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
    async def updated_rune_page(connection, event2):
        runes = game.get_runes(event2.data)
        if runes is not None:
            perks, primaryStyleId, subStyleId = runes
            await game.update_perks(connection, perks, 'deepvision', primaryStyleId, subStyleId)


@connector.close
async def disconnect(connection):
    print('The client was closed')
    await connector.stop()


connector.start()
