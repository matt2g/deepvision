from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from lcu_driver import Connector
from urllib import parse
import json, os
from summoners import Summoner, Runepage


t = open('dragontail-11.12.1/11.12.1/data/en_US/champion.json', 'rb')
champ_data = json.load(t)
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
connector = Connector()


@connector.ready
async def connect(connection):
    print('LCU API is ready to be used.')


@connector.ws.register('/lol-champ-select/v1/session', event_types=('CREATE',))
async def get_team_members(connection, event):
    global summoners
    summoners = []
    summoner_ids = []
    summoner_names = []
    for i in event.data["myTeam"]:
        summoner_ids.append(i["summonerId"])
        summoners.append(Summoner(i["summonerId"], i['cellId'], i['assignedPosition']))
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
    current_summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    current_summoner_json = await current_summoner.json()
    current_id = current_summoner_json["summonerId"]

    for summoner in summoners:
        if summoner.return_summoner_id() == current_id:
            summoner.update_current()


@connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
async def get_selection(connection, event):
    global summoners
    current_summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    current_summoner_json = await current_summoner.json()
    current_id = current_summoner_json["summonerId"]
    for action in event.data['actions']:
        for summoner in summoners:
            if summoner.return_summoner_id() == current_id:
                for item in action:
                    if item['actorCellId'] == summoner.return_cellid() and item['isInProgress'] == False:
                        selected_champ_id = str(item['championId'])
                        selected_champ = champ_dict[selected_champ_id]
                        runepage = Runepage(selected_champ)
                        print(runepage.print_perks(), runepage.print_frag())
                        continue
    print('test')





@connector.close
async def disconnect(connection):
    print('The client was closed')
    await connector.stop()


connector.start()
