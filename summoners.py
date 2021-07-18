import json, re
from selenium.webdriver import Firefox
from scraper import get_best_perks, get_selected_champ_info

runes_dict = {}
champ_dict = {}


def create_dictionaries():
    with open('dragontail-11.12.1/11.12.1/data/en_US/runesReforged.json', 'rb') as f:
        rune_data = json.load(f)
    for tree in rune_data:
        for slots in tree['slots']:
            for runes in slots['runes']:
                key = runes['key'].lower()
                runes_dict[key] = [runes['id'], runes['icon'], tree['id']]
    with open('dragontail-11.12.1/11.12.1/data/en_US/champion.json', 'rb') as f:
        champ_data = json.load(f)
    for champ in champ_data['data']:
        champ_dict[champ_data['data'][champ]['key']] = champ


class Game:
    def __init__(self):
        create_dictionaries()
        self.myTeam = None
        self.mySummoner = None
        self.lockedIn = []
        self.got_runes = False

    async def create_game(self, connection):
        self.myTeam = await self.get_summoners(connection)
        self.mySummoner = await self.get_me(connection)
        self.lockedIn = []
        self.got_runes = False
        self.get_current_player()

    @staticmethod
    async def get_summoners(connection):
        summoners = []
        summoner_data = await connection.request('GET', '/lol-champ-select/v1/session')
        if summoner_data.status == 200:
            data = await summoner_data.json()
            for info in data['myTeam']:
                if info['summonerId'] != 0:
                    summoners.append(await Summoner.create_summoner(connection, info['summonerId'], info['cellId'],
                                                                    info['assignedPosition']))
            return summoners
        else:
            return

    @staticmethod
    async def get_me(connection):
        summoner = await connection.request('GET', '/lol-summoner/v1/current-summoner')
        if summoner.status == 200:
            data = await summoner.json()
            return await Summoner.create_summoner(connection, data["summonerId"])
        else:
            return

    def get_current_player(self):
        for summoner in self.myTeam:
            if summoner.return_summoner_id() == self.mySummoner.return_summoner_id():
                summoner.update_current()

    def monitor_game_status(self, event):
        for actions in event['actions']:
            for item in actions:
                for summoner in self.myTeam:
                    if item['actorCellId'] == summoner.return_cell_id() and item['completed'] and item['type'] == 'pick':
                        summoner.update_locked_in()
                        summoner.set_champion_id(item['championId'])
                        self.lockedIn.append(summoner)
                        self.myTeam.remove(summoner)
                        if summoner.return_current():
                            self.get_runes(summoner)

                        break
                    else:
                        pass

    def get_runes(self, summoner):
        self.got_runes = True
        runes = Runepage(summoner.return_champion_name())
        return runes.print_perks_ids()

    def get_op_gg_info(self):
        summoner_names = []
        for summoner in self.myTeam:
            summoner_names.append(summoner.return_display_name())
        browser = Firefox()
        browser.get('https://na.op.gg/')
        search = browser.find_element_by_class_name('summoner-search-form__text')
        search.send_keys(', '.join(summoner_names))
        search.submit()

    def return_my_team(self):
        return self.myTeam

    def return_my_summoner(self):
        return self.mySummoner

    async def update_perks(self, connection, perks: list, name, primaryStyleId, subStyleId):
        deepvision_page_id = await self.get_page_id(connection, name)
        page_amount, first_id = await self.get_page_amount(connection)
        if deepvision_page_id is not None:
            delete_page = await connection.request('delete', '/lol-perks/v1/pages/' + str(deepvision_page_id))

        if page_amount == 14 and deepvision_page_id is None:
            delete_page = await connection.request('delete', '/lol-perks/v1/pages/' + str(first_id))

        if perks is not None:
            updated_data = {
                "name": name,
                "current": True,
                "primaryStyleId": primaryStyleId,
                "selectedPerkIds": perks,
                "subStyleId": subStyleId,
            }
            rune_page = await connection.request('post', '/lol-perks/v1/pages', json=updated_data)
            if rune_page.status == 200:
                print(f'{name} rune page successfully updated!')
            else:
                print('Unknown problem, the rune page was not set.')

    @staticmethod
    async def get_page_id(connection, name):
        pages = await connection.request('get', '/lol-perks/v1/pages')
        pages_json = await pages.json()
        for page in pages_json:
            if page['name'] == name:
                return page['id']
        return

    @staticmethod
    async def get_page_amount(connection):
        page_sum = 0
        pages = await connection.request('get', '/lol-perks/v1/pages')
        pages_json = await pages.json()
        for page in pages_json:
            page_sum += 1
        return page_sum, pages_json[0]['id']


class Summoner:
    def __init__(self, connection, summonerId, cellId=None, assignedPosition=None):
        self.champ_dict = champ_dict
        self.summonerId = summonerId
        self.cellId = cellId
        self.assignedPosition = assignedPosition
        self.displayName = None
        self.internalName = None
        self.puuid = None
        self.current = False
        self.lockedIn = False
        self.championId = None
        self.champion = None

    @classmethod
    async def create_summoner(cls, connection, summonerId, cellId=None, assignedPosition=None):
        summoner = cls(connection, summonerId, cellId, assignedPosition)
        await summoner.get_summoner_info(connection)
        return summoner

    async def get_summoner_info(self, connection):
        summoner = await connection.request('GET', '/lol-summoner/v1/summoners/' + str(self.summonerId))
        data = await summoner.json()
        self.displayName = data['displayName']
        self.internalName = data['internalName']
        self.puuid = data['puuid']

    def update_locked_in(self):
        if self.lockedIn is False:
            self.lockedIn = True
        else:
            self.lockedIn = False

    def return_locked_in(self):
        return self.lockedIn

    def update_current(self):
        if self.current is False:
            self.current = True
        else:
            self.current = False

    def set_assignedPosition(self, assignedPosition):
        self.assignedPosition = assignedPosition

    def return_assignedPosition(self):
        return self.assignedPosition

    def set_cell_id(self, cellId):
        self.cellId = cellId

    def return_cell_id(self):
        return self.cellId

    def return_current(self):
        return self.current

    def return_summoner_id(self):
        return self.summonerId

    def return_display_name(self):
        return self.displayName

    def return_puuid(self):
        return self.puuid

    def set_champion_id(self, championId):
        self.championId = str(championId)
        self.champion = self.champ_dict[self.championId]

    def return_champion_name(self):
        return str(self.champion.lower())


class Runepage:
    def __init__(self, champion, position=None):
        self.champion = champion
        self.position = position
        self.perks = []
        self.frags = []
        self.get_best_rune_page()

    def get_best_rune_page(self):
        perks, frags = get_best_perks(self.champion, self.position)
        for perk in perks:
            self.perks.append(Perk(perk))
        for frag in frags:
            self.frags.append(Frag(frag))

    def print_perks(self):
        perk_names = []
        for perk in self.perks:
            perk_names.append(perk.print_perk_name())
        return perk_names

    def print_perks_ids(self):
        primaryStyleId = ''
        subStyleId = ''
        perk_names = []
        for n, perk in enumerate(self.perks):
            if n == 0:
                primaryStyleId = perk.tree_id
            if n == 4:
                subStyleId = perk.tree_id
            perk_names.append(perk.print_perk_id())
        for frag in self.frags:
            perk_names.append(frag.print_frag_id())
        return perk_names, primaryStyleId, subStyleId

    def print_frag(self):
        frag_names = []
        for frag in self.frags:
            frag_names.append(frag.print_frag_name())
        return frag_names

    def perks(self):
        return self.perks


class Perk:
    def __init__(self, perk):
        self.rune_key = runes_dict
        self.perk = perk
        self.tree_id = None
        self.id = self.get_perk_id()
        self.img_url = self.get_img()

    def get_perk_id(self):
        name = "".join(re.findall(r'[a-zA-Z]+', self.perk))
        self.id = self.rune_key[name.lower()][0]
        self.perk = name.lower()
        self.tree_id = self.rune_key[name.lower()][2]
        return self.id

    def get_img(self):
        root = 'dragontail-11.12.1/img'
        self.img_url = root + self.rune_key[self.perk][1]
        return self.img_url

    def print_perk_name(self):
        return self.perk

    def print_perk_id(self):
        return self.id


class Frag:
    def __init__(self, frag):
        self.frag = frag.lower()
        self.frag_dict = {
            'adaptiveforce': 5008,
            'armor': 5002,
            'attackspeed': 5005,
            'cdrscaling': 5007,
            'healthscaling': 5001,
            'magicres': 5003,
        }
        self.frag_id = self.frag_dict[frag.lower()]

    def print_frag_name(self):
        return self.frag

    def print_frag_id(self):
        return self.frag_id
