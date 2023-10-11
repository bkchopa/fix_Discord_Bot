import requests
import aiohttp

summoner_dict = {}

RIOT_API_KEY = 'RGAPI-4e118ee8-8a09-44da-bc95-62a15b12aeda'
RIOT_API_URL_SUMMONER = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
RIOT_API_URL_CURRENT_GAME = "https://kr.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summoner_id}"

async def update_summoner_id_dict(nickname_list):
    for nickname in nickname_list:
        summoner_info = await get_summoner_info(nickname)
        if summoner_info:
            summoner_dict[nickname] = summoner_info
            
    print(summoner_dict)
async def get_summoner_info(summoner_name):
    # 저장된 정보가 있다면 API 호출 없이 바로 반환
    if summoner_name in summoner_dict:
        return summoner_dict[summoner_name]

    # API 호출
    async with aiohttp.ClientSession() as session:
        async with session.get(
                RIOT_API_URL_SUMMONER.format(summoner_name=summoner_name),
                headers={"X-Riot-Token": RIOT_API_KEY}
        ) as response:
            if response.status == 200:
                summoner_info = await response.json()
                # API 호출 결과를 딕셔너리에 저장
                summoner_dict[summoner_name] = summoner_info
                return summoner_info
    return None


async def get_current_game_info(summoner_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            RIOT_API_URL_CURRENT_GAME.format(summoner_id=summoner_id),
            headers={"X-Riot-Token": RIOT_API_KEY}
        ) as response:
            if response.status == 200:
                return await response.json()
    return None

async def get_game_info(summoner_name):
    summoner_info = await get_summoner_info(summoner_name)
    if summoner_info:
        summoner_id = summoner_info["id"]
        return await get_current_game_info(summoner_id)
    return None