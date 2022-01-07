import requests
import json
from datetime import datetime
import os

LIVE_DATA_URL = 'https://www.veikkaus.fi/api/lwager/v2/live-games/events'
NHL_TEAMS_LIST_URL = 'https://statsapi.web.nhl.com/api/v1/teams'


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
    
    with open('live-fixed.json') as input_data:
        live_data = json.load(input_data)
    input_data.close()

    #Uncomment to get real data
    #live_data = get_live_data()

    teams = get_teams_list()
    
    for id in live_data:
        if 'sportId' in id:
            if id['sportId'] == "3":

                #Team names would be in more compact format in id['shortName'], but there seems to be some
                #inconsistency in values (e.g. "Washington" was "Washingto")
                game_teams = (
                    id['name'].split(" - ")[0].split(": ")[1],
                    id['name'].split(" - ")[1]
                )
                print(game_teams)
                if game_teams[0] in teams and game_teams[1] in teams:
                    
                    id['homeTeam'] = game_teams[0]
                    id['awayTeam'] = game_teams[1]
                    games.append(id)

    #print(games)
    timestamp = datetime.now().timestamp()
    veikkaus_data = {
        "timestamp": timestamp,
        "games": games
    }
    
    with open(os.path.join(os.curdir, 'data', 'games.json'), 'w') as outputfile:
        json.dump(veikkaus_data, outputfile)

if __name__ == '__main__':
	main()