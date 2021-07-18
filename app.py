from lcu_driver import Connector
from summoners import Game
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read('config.ini')
client_info = config_object["CLIENT"]


def get_lockfile_for_linux():
    import os
    path = os.path.join(client_info['installation_path'], 'lockfile')
    if os.path.isfile(path):
        file = open(path, 'r')
        text = file.readline()
        file.close()
        return text
    return None


def app():
    if get_lockfile_for_linux() is None:
        connector = Connector()
    else:
        connector = Connector(str=get_lockfile_for_linux())
    game = Game()

    @connector.ready
    async def connect(connection):
        print('LCU connection ready')

    @connector.ws.register('/lol-champ-select/v1/session', event_types=('CREATE',))
    async def create_game(connection, event):
        await game.create_game(connection)
        game.get_op_gg_info()

        @connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
        async def updated_rune_page(connection2, event2):
            runes = game.get_runes(event2.data)
            if runes is not None:
                perks, primaryStyleId, subStyleId = runes
                await game.update_perks(connection2, perks, 'deepvision', primaryStyleId, subStyleId)

    @connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
    async def connection(connection, event):
        data = await event.json()
        print(data)

    @connector.close
    async def disconnect(connection):
        print('The client was closed')
        await connector.stop()

    connector.start()


if __name__ == '__main__':
    app()
