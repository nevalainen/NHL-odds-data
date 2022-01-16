import requests
import json
import pytz
from datetime import datetime, timedelta
import os

SCHEDULE_LINK = "/api/v1/schedule?"
TEAMS_LINK = "/api/v1/teams"
BASE_URL = "https://statsapi.web.nhl.com"
START_DATE = "startDate="
END_DATE = "endDate="

def main():

    daily_info = {
        'starting_time': '',
        'games': []
    }

    date = datetime.now(pytz.timezone('America/New_York')).strftime("%Y-%m-%d")
    print(date)
    next_day = (datetime.now(pytz.timezone('America/New_York')) + timedelta(days=1)).strftime("%Y-%m-%d")
    print(next_day)
    resp = requests.get("{}{}".format(BASE_URL, TEAMS_LINK))
    teams_list = json.loads(resp.text)
    teams_list_compact = {}
    for i in teams_list['teams']:
        teams_list_compact[i['id']] = i['shortName']

    resp = requests.get("{}{}{}{}&{}{}".format(
        BASE_URL,
        SCHEDULE_LINK,
        START_DATE,
        date,
        END_DATE,
        date
    ))

    games_today = json.loads(resp.text)

    for i in games_today['dates'][0]['games']:
        if i['status']['detailedState'] == "Scheduled":
            if daily_info['starting_time'] == '':
                daily_info['starting_time'] = i['gameDate']
            #print(i['gamePk'])
            daily_info['games'].append({
                'gamePk': i['gamePk'],
                'gameDate': i['gameDate'],
                'link': i['link'],
                'homeTeam': {
                    'fullName': i['teams']['home']['team']['name'],
                    'id': i['teams']['home']['team']['id'],
                    'shortName': teams_list_compact[i['teams']['home']['team']['id']]
                },
                'awayTeam': {
                    'fullName': i['teams']['away']['team']['name'],
                    'id': i['teams']['away']['team']['id'],
                    'shortName': teams_list_compact[i['teams']['away']['team']['id']]
                }
            })

    timestamp = datetime.now().timestamp()

    
    """
    with open(os.path.join('.', 'debug','veikkaus-twodays.json')) as input_data:
        veikkaus_data = json.load(input_data)
    input_data.close()
    """
    
    resp = requests.get("{}{}".format("https://www.veikkaus.fi/api/sport-codes/v1/fi/events/by-day/", date)) #Day format 2022-01-16
    veikkaus_data = json.load(resp.text)

    resp = requests.get("{}{}".format("https://www.veikkaus.fi/api/sport-codes/v1/fi/events/by-day/", next_day))
    veikkaus_data.append(json.load(resp.text))
    
    #print(veikkaus_data)
    for id in veikkaus_data:
        if 'sportId' in id:
            #Check that sportId = 3 (hockey), categoryId = 2 (NA) and tournamentId = 1 (NHL)
            if id['sportId'] == 3 and id['categoryId'] == 2 and id['tournamentId'] == 1:
                #print(id)
                #Check that starting time is not in the past, and during the next 24 hours (86400 seconds)
                if (id['date'] / 1000) - timestamp > 0 and (id['date'] / 1000) - timestamp < 86400:
                    #print(id)
                    print(id['teams'][0]['shortName'])
                    for game in daily_info['games']:
                        if game['homeTeam']['shortName'] == id['teams'][0]['shortName']:
                            game['veikkausGameId'] = {
                                'id': id['id'],
                                'external_id': id['externalId']
                            }

    timestamp = datetime.now().timestamp()
    veikkaus_data = {
        "timestamp": timestamp,
        "date": date,
        "dailyInfo": daily_info
    }
    
    if not os.path.exists(os.path.join(os.curdir, 'data')):
        os.mkdir(os.path.join(os.curdir, 'data'))
        
    with open(os.path.join(os.curdir, 'data', 'dailyInfo.json'), 'w') as outputfile:
        json.dump(veikkaus_data, outputfile)
    

if __name__ == '__main__':
	main()