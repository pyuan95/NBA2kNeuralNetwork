from nba_api.stats.endpoints.boxscoretraditionalv2 import BoxScoreTraditionalV2
from nba_api.stats.endpoints.leaguegamefinder import LeagueGameFinder
from nba_api.stats.static import teams
from datetime import datetime

def get_game_ids(min_year):
    min_date = datetime(min_year, 1, 1)
    game_ids = []
    nba_teams = teams.get_teams()
    for team in nba_teams:
        if team['abbreviation'] != "NYK":
            continue
        print(team)
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
            team_id = player[player_headers.index("TEAM_ABBREVIATION")]
            if team_id != data[game_id][team_name]['team_stats']['TEAM_ID']:
                continue
            data[game_id][team_name]['player_stats'][player_name] = dict()
            for i, element in enumerate(player):
                data[game_id][team_name]['player_stats'][player_name][player_headers[i]] = element

    return data

x = get_game_ids(2018)
x = x[0]
print(get_game_boxscore(x)[0])
