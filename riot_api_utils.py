import requests


RIOT_API_KEY = 'RGAPI-4e118ee8-8a09-44da-bc95-62a15b12aeda'
RIOT_API_URL_SUMMONER = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
RIOT_API_URL_CURRENT_GAME = "https://kr.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summoner_id}"

def get_summoner_info(summoner_name):
    response = requests.get(
        RIOT_API_URL_SUMMONER.format(summoner_name=summoner_name),
        headers={"X-Riot-Token": RIOT_API_KEY}
    )
    if response.status_code == 200:
        return response.json()
    return None

def get_current_game_info(summoner_id):
    response = requests.get(
        RIOT_API_URL_CURRENT_GAME.format(summoner_id=summoner_id),
        headers={"X-Riot-Token": RIOT_API_KEY}
    )
    if response.status_code == 200:
        return response.json()
    return None