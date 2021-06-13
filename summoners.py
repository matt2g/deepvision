import json, re
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from lcu_driver import Connector
import aiohttp
from scraper import get_best_perks


class Game:
    def __init__(self):
        self.myTeam = None
        self.me = None
        self.lockedIn = False

    async def create_game(self, connection):
        self.myTeam = await self.get_summoners(connection)
        self.me = await self.get_me(connection)

    @staticmethod
    async def get_summoners(connection):
        summoners = []
        summoner_data = await connection.request('GET', '/lol-champ-select/v1/session')
        if summoner_data.status == 200:
            data = await summoner_data.json()
            for info in data['myTeam']:
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

    def determine_progress(self, event):
        for actions in event:
            if actions['actorCellId'] == self.me.return_cell_id() and not actions['isInProgress']:
                self.update_locked_in()
        else:
            pass

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
    
    def update_locked_in(self):
        if self.lockedIn is False:
            self.lockedIn = True
        else:
            self.lockedIn = False


class Summoner:
    def __init__(self, connection, summonerId, cellId=None, assignedPosition=None):
        self.summonerId = summonerId
        self.cellId = cellId
        self.assignedPosition = assignedPosition
        self.displayName = None
        self.internalName = None
        self.puuid = None
        self.current = False

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

    def update_current(self):
        if self.current is False:
            self.current = True
        else:
            self.current = False

    def return_cell_id(self):
        return int(self.cellId)

    def return_current(self):
        return self.current

    def return_summoner_id(self):
        return self.summonerId

    def return_display_name(self):
        return self.displayName

    def return_puuid(self):
        return self.puuid


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
        perk_names = []
        for perk in self.perks:
            perk_names.append(perk.print_perk_id())
        return perk_names

    def print_frag(self):
        frag_names = []
        for frag in self.frags:
            frag_names.append(frag.print_frag())
        return frag_names

    def perks(self):
        return self.perks


class Perk:
    def __init__(self, perk):
        self.rune_key = self.create_rune_key()
        self.perk = perk
        self.id = self.get_perk_id()
        self.img_url = self.get_img()

    @staticmethod
    def create_rune_key():
        with open('dragontail-11.12.1/11.12.1/data/en_US/runesReforged.json', 'rb') as f:
            rune_data = json.load(f)
            runes_dict = {}
        for tree in rune_data:
            for slots in tree['slots']:
                for runes in slots['runes']:
                    key = runes['key'].lower()
                    runes_dict[key] = [runes['id'], runes['icon']]
        return runes_dict

    def get_perk_id(self):
        name = "".join(re.findall(r'[a-zA-Z]+', self.perk))
        self.id = self.rune_key[name.lower()][0]
        self.perk = name.lower()
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

    def print_frag(self):
        return self.frag
