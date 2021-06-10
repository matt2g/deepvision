from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from lcu_driver import Connector
from urllib import parse


def get_lockfile():
    import os
    path = os.path.join('/home/matt/Games/league-of-legends/drive_c/Riot Games/League of Legends/', 'lockfile')
    if os.path.isfile(path):
        file = open(path, 'r')
        text = file.readline()
        file.close()
        return text
    return None


connector = Connector(str=get_lockfile())


@connector.ready
async def connect(connection):
    print('LCU API is ready to be used.')


@connector.ws.register('/lol-champ-select/v1/session', event_types=('CREATE',))
async def get_team_members(connection, event):
    summoner_ids = []
    summoner_names = []
    for i in event.data["myTeam"]:
        summoner_ids.append(i["summonerId"])
    params = {'ids': summoner_ids}
    request = '/lol-summoner/v2/summoner-names?' + parse.urlencode(params, False)
    summoner_names_json = await connection.request('get', request)
    for i in await summoner_names_json.json():
        summoner_names.append(i["displayName"])
    browser = Firefox()
    browser.get('https://na.op.gg/')
    search = browser.find_element_by_class_name('summoner-search-form__text')
    search.send_keys(', '.join(summoner_names))
    search.submit()


@connector.close
async def disconnect(connection):
    print('The client was closed')
    await connector.stop()


connector.start()
