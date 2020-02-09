from nba_api.stats.endpoints.boxscoretraditionalv2 import BoxScoreTraditionalV2
from nba_api.stats.endpoints.boxscoreadvancedv2 import BoxScoreAdvancedV2
from nba_api.stats.endpoints.leaguegamefinder import LeagueGameFinder
from nba_api.stats.static import teams
from datetime import datetime
from multiprocessing import Pool
from time import sleep
import pickle
import gzip
import sys

NUMBER_THREADS = 3

def chunks(lst, n):
    chunk_size = len(lst) // n
    lst = [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    if len(lst) % n != 0:
        extra = lst.pop(-1)
        lst[-1] += extra
    return lst

def get_game_ids(min_year):
    min_date = datetime(min_year, 1, 1)
    game_ids = []
    nba_teams = teams.get_teams()
    for team in nba_teams:
        if team['full_name'] != "New York Knicks":
            # continue
            pass
        print("FETCHING GAME IDS: ", team['full_name'])
        team_id = team['id']
        gamefinder = LeagueGameFinder(team_id_nullable=team_id)
        games = gamefinder.get_data_frames()[0]
        ids, dates = games['GAME_ID'], games['GAME_DATE']
        for i, game_id in enumerate(ids):
            date = datetime.strptime(dates[i], '%Y-%m-%d')
            if date > min_date:
                game_ids.append(game_id)
    return list(set(game_ids))
        
def get_game_boxscore(game_id):

    # Returns team stats and player stats
    b = BoxScoreTraditionalV2(game_id = game_id)
    b.load_response()
    team_stats, player_stats = b.team_stats.get_dict(), b.player_stats.get_dict()
    return team_stats, player_stats

def get_advanced_game_boxscore(game_id):

    # Returns team stats and player stats
    b = BoxScoreAdvancedV2(game_id = game_id)
    b.load_response()
    team_stats, player_stats = b.team_stats.get_dict(), b.player_stats.get_dict()
    return team_stats, player_stats

def data_to_dict(team_stats, player_stats):
    """

    GAME_ID
        team
            team_stats
            player_stats
                player_name

    :param team_stats_:
    :param player_stats:
    :return:
    """

    data = dict()
    team_headers = team_stats['headers']
    team_data = team_stats['data']
    player_headers = player_stats['headers']
    player_data = player_stats['data']
    game_id = team_data[0][team_headers.index("GAME_ID")]
    data[game_id] = dict()
    for team in team_data:
        team_name = team[team_headers.index("TEAM_NAME")]
        data[game_id][team_name] = dict()
        data[game_id][team_name]['team_stats'] = dict()
        data[game_id][team_name]['player_stats'] = dict()
        for i, element in enumerate(team):
            data[game_id][team_name]['team_stats'][team_headers[i]] = element
        for player in player_data:
            player_name = player[player_headers.index("PLAYER_NAME")]
            team_id = player[player_headers.index("TEAM_ID")]
            if team_id != data[game_id][team_name]['team_stats']['TEAM_ID']:
                continue
            data[game_id][team_name]['player_stats'][player_name] = dict()
            for i, element in enumerate(player):
                data[game_id][team_name]['player_stats'][player_name][player_headers[i]] = element

    return data

def fetch_data(game_ids):
    trad_data = []
    advanced_data = []
    index = 0
    while index < len(game_ids):
        i = game_ids[index]
        try:
            print("FETCHING GAME #: ", index + 1, " OUT OF ", len(game_ids))
            team_stats, player_stats = get_game_boxscore(i)
            trad_data.append(data_to_dict(team_stats, player_stats))
            team_stats, player_stats = get_advanced_game_boxscore(i)
            advanced_data.append(data_to_dict(team_stats, player_stats))
            index += 1
            sleep(3)
        except:
            print("TIMED OUT! Waiting...")
            sleep(900)
    return trad_data, advanced_data

if __name__ == "__main__":
    """     x = get_game_ids(2017)
    x = chunks(x, NUMBER_THREADS)
    p = Pool(NUMBER_THREADS)
    print("NUMBER THREADS: ", NUMBER_THREADS, " CHUNKS ", len(x))
    data = p.map(fetch_data, x)

    final_trad_data = dict()
    final_advanced_data = dict()
    for trad_data, advanced_data in data:
        for game in trad_data:
            for key in game:
                final_trad_data[key] = game[key]
        for game in advanced_data:
            for key in game:
                final_advanced_data[key] = game[key]
    """

    log_file = open("fetch_game_data.log","w")
    sys.stdout = log_file

    x = get_game_ids(2017)
    final_trad_data = dict()
    final_advanced_data = dict()
    trad_data, advanced_data = fetch_data(x)
    for game in trad_data:
        for key in game:
            final_trad_data[key] = game[key]
    for game in advanced_data:
        for key in game:
            final_advanced_data[key] = game[key]

    output = gzip.GzipFile("traditional_game_data.p.gzip", "wb")
    pickle.dump(final_trad_data, output, protocol=pickle.HIGHEST_PROTOCOL)
    output.close()

    output = gzip.GzipFile("advanced_game_data.p.gzip", "wb")
    pickle.dump(final_advanced_data, output, protocol=pickle.HIGHEST_PROTOCOL)
    output.close()

    log_file.close()