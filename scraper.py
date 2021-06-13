from bs4 import BeautifulSoup
import requests, re


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
