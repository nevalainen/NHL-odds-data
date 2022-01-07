import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

DATE = '2022-01-04'

MONEYPUCK_DATE_URL = 'https://moneypuck.com/moneypuck/dates/'

def get_daily_data():
    with open(os.path.join(os.curdir, 'data', 'dailyInfo.json')) as input_data:
        live_data = json.load(input_data)
    input_data.close()

    return(live_data)

def main():
    daily_data = get_daily_data()
    print(daily_data)
    date_to_url = daily_data['date'].replace("-", "")
    games = []

    page = requests.get("{}{}.htm".format(MONEYPUCK_DATE_URL, date_to_url))
    soup = BeautifulSoup(page.content, 'html.parser')
    print("{}{}".format(MONEYPUCK_DATE_URL, date_to_url))
    tr_all = soup.find_all('tr')
    for game in daily_data['dailyInfo']['games']:

        for tr in tr_all:
            if tr.find('img') is not None:
                if tr.find_all('img', alt = game['awayTeam']['fullName'].upper()):      
                    #print("{} win odds: {}".format(game['awayTeam']['fullName'], tr.find('h2').text.replace(" ", "")))
                    game_h2 = tr.find_all('h2')
                    games.append({
                        'homeTeam': {
                            'fullName': game['homeTeam']['fullName'],
                            'win_odds_perc': float(game_h2[1].text.translate(str.maketrans('', '', ' \n\t\r'))[:-1])
                        },
                        'awayTeam': {
                            'fullName': game['awayTeam']['fullName'],
                            'win_odds_perc': float(game_h2[0].text.translate(str.maketrans('', '', ' \n\t\r'))[:-1])
                        }
                    })

    timestamp = datetime.now().timestamp()
    moneypuck_data = {
            "timestamp": timestamp,
            "games": games
        }
    with open(os.path.join(os.curdir, 'data', 'moneypuck_data.json'), 'w') as outputfile:
        json.dump(moneypuck_data, outputfile)


if __name__ == '__main__':
	main()