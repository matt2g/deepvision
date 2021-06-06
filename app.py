from lcu_driver import Connector


def get_lockfile():
    import os
    path = os.path.join('/home/matt/Games/league-of-legends/drive_c/Riot Games/League of Legends/', 'lockfile')
    if os.path.isfile(path):
        file = open(path, 'r')
        text = file.readline()
        file.close()
        return text
    return None


connector = Connector(get_lockfile())


@connector.ready
async def connect(connection):
    print('LCU API is ready to be used.')


@connector.ws.register('/lol-summoner/v1/summoners/', event_types=('UPDATE',))
async def icon_changed(connection, event):
    print(f'The summoner {event.data["displayName"]} was updated.')


@connector.close
async def disconnect(connection):
    print('The client was closed')
    await connector.stop()


connector.start()

#test