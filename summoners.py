import json, re
from lcu_driver import Connector
from scraper import get_best_perks


class Summoner:
    def __init__(self, summonerId, cellId, assignedPosition=None):
        self.summonerId = summonerId
        self.displayName = None
        self.internalName = None
        self.puuid = None
        self.cellId = cellId
        self.assignedPosition = assignedPosition
        self.current = False

    def update_current(self):
        self.current = True

    def return_id(self):
        return self.summonerId

    def cellid(self):
        return self.cellId

    def current(self):
        return self.current

    def return_summoner_id(self):
        return self.summonerId


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

    def create_rune_key(self):
        f = open('dragontail-11.12.1/11.12.1/data/en_US/runesReforged.json', )
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
