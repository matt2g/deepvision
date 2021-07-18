import pprint
import re
import requests
from bs4 import BeautifulSoup


def get_best_perks(champion, position=None):
    frag_image_urls = {
        '//opgg-static.akamaized.net/images/lol/perkShard/5008.png': 'adaptiveforce',
        '//opgg-static.akamaized.net/images/lol/perkShard/5002.png': 'armor',
        '//opgg-static.akamaized.net/images/lol/perkShard/5005.png': 'attackspeed',
        '//opgg-static.akamaized.net/images/lol/perkShard/5007.png': 'cdrscaling',
        '//opgg-static.akamaized.net/images/lol/perkShard/5001.png': 'healthscaling',
        '//opgg-static.akamaized.net/images/lol/perkShard/5003.png': 'magicres'
    }
    if position is not None:
        source = requests.get('https://na.op.gg/champion/' + champion.lower() + '/statistics/' + position).text
    else:
        source = requests.get('https://na.op.gg/champion/' + champion.lower()).text
    soup = BeautifulSoup(source, 'lxml')
    champion_overview_table = soup.find('table',
                                        class_='champion-overview__table champion-overview__table--rune tabItems')
    perk_table = champion_overview_table.find('td', class_='champion-overview__data')
    perks = []
    frags = []
    for div in perk_table.find_all('div', class_="perk-page__item--active"):
        for img in div.find_all('img', alt=True):
            perks.append(img['alt'])
    src_urls = []
    for img in perk_table.find_all('img', class_="active"):
        url = re.compile(r'.*\.png')
        src_urls.append(url.findall(img['src']))
    for urls in src_urls:
        frags.append(frag_image_urls[urls[0]])

    return perks, frags


def get_selected_champ_info(champion, summoner_name, summonerId):
    seasons_dict = {'17': "2021", '15': "2020", '13': "2019"}
    update_info = requests.post('https://na.op.gg/summoner/ajax/renew.json/', data={'summonerId': summonerId})
    if update_info == 200:
        print('Updated Summoner Info')
    seasons = ['17', '15', '13']
    total_wins = 0
    total_losses = 0
    reg_numbers = re.compile(r'\d+')
    print(f'Player: {summoner_name}')
    for season in seasons:
        info = requests.get('https://na.op.gg/summoner/champions/ajax/champions.rank/summonerId=' + summonerId +
                            '&season=' + season + '&').text
        soup = BeautifulSoup(info, 'lxml')
        body = soup.find('tbody', class_="Body")
        tags = body.find_all('tr', class_=["Row TopRanker", "Row"])
        print(f'Season {seasons_dict[season]}')
        for tag in tags:
            name = tag.find('td', class_="ChampionName Cell")
            if name['data-value'].lower() == champion.lower():
                wins = tag.find('div', class_="Text Left")
                print(wins.text if wins else "OW")
                if wins:
                    total_wins += int(reg_numbers.findall(wins.text)[0])
                losses = tag.find('div', class_="Text Right")
                print(losses.text if losses else "OL")
                if losses:
                    total_losses += int(reg_numbers.findall(losses.text)[0])
                print()
                break
    return total_wins, total_losses
