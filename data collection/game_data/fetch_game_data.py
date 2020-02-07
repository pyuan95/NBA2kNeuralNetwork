from nba_api.stats.endpoints.boxscoretraditionalv2 import BoxScoreTraditionalV2
from nba_api.stats.endpoints.leaguegamefinder import LeagueGameFinder
from nba_api.stats.static import teams
from datetime import datetime

def get_game_ids(min_year):
    min_date = datetime(min_year, 1, 1)
    game_ids = []
    nba_teams = teams.get_teams()
    for team in nba_teams:
        print(team)
        team_id = team['id']
        gamefinder = LeagueGameFinder(team_id_nullable=team_id)
        games = gamefinder.get_data_frames()[0]
        ids, dates = games['GAME_ID'], games['GAME_DATE']
        for i, game_id in enumerate(ids):
            date = datetime.strptime(dates[i], '%Y-%m-%d')
            if date > min_date:
                print(date)
                game_ids.append(game_id)
    return game_ids
        
def get_game_boxscore(game_id):

    # Returns team stats and player stats
    b = BoxScoreTraditionalV2(game_id = game_id)
    b.load_response()
    return b.team_stats.get_dict(), b.player_stats.get_dict()


x = get_game_ids(2018)
print(x)