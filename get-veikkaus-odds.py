import requests
import json
from datetime import datetime
import os

LIVE_DATA_URL = 'https://www.veikkaus.fi/api/lwager/v2/live-games/events'
NHL_TEAMS_LIST_URL = 'https://statsapi.web.nhl.com/api/v1/teams'
ODDS_BY_EVENT = "https://www.veikkaus.fi/api/sport-open-games/v1/games/ebet/draws/by-event/"

def get_live_data():
    resp = requests.get("https://www.veikkaus.fi/api/lwager/v2/live-games/events")
    return(json.loads(resp.text))

def get_teams_list():
    teams_list = []
    resp = requests.get(NHL_TEAMS_LIST_URL)
    teams = json.loads(resp.text)
    
    for i in teams['teams']:
        teams_list.append(i['shortName'])
    return(teams_list)

def main():
    games = []

    with open(os.path.join('.','data', 'dailyInfo.json')) as input_data:
        daily_data = json.load(input_data)
    input_data.close()

    print(daily_data)
    
    games = []

    for game in daily_data['dailyInfo']['games']:
            resp = requests.get("{}{}".format(ODDS_BY_EVENT, game['veikkausGameId']['id']))
            veikkaus_game_odds = json.loads(resp.text)
            print(veikkaus_game_odds)
            game_dict = {
                'teams': {
                    'homeTeam': game['homeTeam'], 
                    'awayTeam': game['awayTeam']
                },
                'bets': []
            }
            for id in veikkaus_game_odds:
                print(id['rows'][0]['type'])
                if id['rows'][0]['type'] in ['1X2', '12']:
                    bet_odds = []
                    for odds in id['rows'][0]['competitors']:
                        bet_odds.append({
                            'name': odds['name'],
                            'odds': odds['odds']['odds']
                        })
                    game_dict['bets'].append({
                        'type': id['rows'][0]['type'],
                        'bets': bet_odds
                    })
            games.append(game_dict)

    #print(games)

    timestamp = datetime.now().timestamp()
    veikkaus_data = {
        "timestamp": timestamp,
        "games": games
    }

    
    with open(os.path.join(os.curdir, 'data', 'veikkaus_data.json'), 'w') as outputfile:
        json.dump(veikkaus_data, outputfile)
   
if __name__ == '__main__':
	main()