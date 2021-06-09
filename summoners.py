import json
from lcu_driver import Connector


class Summoner:
    def __init__(self, summonerId):
        self.summonerId = summonerId
        self.displayName = None
        self.internalName = None
        self.puuid = None

    def initialize_summoner(self, connection):
        summoner_info = await connection.request('get', 'lol-summoner/v1/summoners/' + self.summonerId)
        summoner_json = await summoner_info.json()
        self.displayName = summoner_json["displayName"]
        self.internalName = summoner_json["internalName"]
        self.puuid = summoner_json["puuid"]
