import gspread
import os
import json
import re
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials

# 인증
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

#creds = Credentials.from_service_account_file("account.json", scopes=scope)
GOOGLE_CREDENTIALS = json.loads(os.environ['GOOGLE_CREDENTIALS'])
creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_CREDENTIALS, scope)
client = gspread.authorize(creds)


SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
spreadsheet = client.open_by_key(SPREADSHEET_ID)
# 워크시트 선택
rowDatasSheet = spreadsheet.worksheet("기입")
rankingSheet = spreadsheet.worksheet("내전 순위")
# 데이터 읽기와 쓰기 예제
#print(worksheet.get_all_records())  # 모든 데이터 가져오기
#worksheet.update_cell(1, 1, "Hello World!")  # 1행 1열에 "Hello World!" 입력
player_info = {}
player_ranking = {}
update_date = ""
top_champions = {}

async def reload():
    global update_date
    player_info.clear()
    player_ranking.clear()

    all_data = rowDatasSheet.get_all_values()
    all_data = all_data[::-1]  # all_data 리스트를 거꾸로 뒤집어서 처리
    for row in all_data:
        if not row[16]:
            continue

        position = row[1]
        nickname = row[2].lower()
        champion = row[3]
        result = row[4]
        kill = row[6]
        death = row[7]
        assist = row[8]



        if nickname not in player_info:
            player_info[nickname] = []

        player_info[nickname].append(
            {"champion": champion, "position": position, "result": result, "kill": kill, "death": death,
             "assist": assist})

        position = row[9]
        nickname = row[10].lower()
        champion = row[11]
        result = row[12]
        kill = row[14]
        death = row[15]
        assist = row[16]
        if nickname not in player_info:
            player_info[nickname] = []

        player_info[nickname].append(
            {"champion": champion, "position": position, "result": result, "kill": kill, "death": death,
             "assist": assist})

    #랭킹
    all_values = rankingSheet.get_all_values()
    # E열(등수), F열(닉네임), G열(점수)부터 시작하는 부분만 추출
    ranked_data = [{"nickname": row[5].lower(), "rank": row[4], "score": row[6]} for row in all_values[2:]]
    # 닉네임을 키로 하고, 등수와 점수를 값으로 하는 딕셔너리 생성
    for item in ranked_data:
        player_ranking[item["nickname"]] = {"rank": item["rank"], "score": item["score"]}


    #날짜
    values_in_column_A = rowDatasSheet.col_values(1)
    team_indices = {}
    latest_date = None

    for value in reversed(values_in_column_A):
        if not value:  # 빈 값은 건너뜀
            continue

        parts = value.split(" ")

        # 9-2 1-8 형식의 데이터만 처리
        if len(parts) != 2 or '-' not in parts[0] or '-' not in parts[1]:
            continue

        date, indices = parts
        team, game_index = indices.split("-")

        # 최신 날짜 업데이트
        if not latest_date:
            latest_date = date

        # 해당 날짜의 모든 팀의 게임 인덱스 저장
        if date == latest_date:
            team_indices[team] = game_index
        else:
            break  # 최신 날짜만 고려하므로 나머지는 처리할 필요 없음

    # 1, 2, 3 팀 중 기록되지 않은 팀의 게임 인덱스를 0-0으로 설정
    for team_num in ['1', '2', '3']:
        if team_num not in team_indices:
            team_indices[team_num] = '0'

    # 월-일을 월 일 형식으로 변경
    latest_date = latest_date.replace("-", "월 ") + "일"

    # 저장된 데이터를 기반으로 원하는 문자열 형태로 변환
    result = ", ".join([f"{team}-{team_indices[team]}" for team in sorted(team_indices.keys())])

    global update_date
    update_date = f"{latest_date} {result}까지 반영"






    # 각 플레이어별로 챔피언의 게임 및 승리 데이터를 저장
    champion_data = {}

    for nickname, games in player_info.items():
        champion_data[nickname] = {}

        for game in games:
            champion = game["champion"]
            result = game["result"]

            if champion not in champion_data[nickname]:
                champion_data[nickname][champion] = {"games": 0, "wins": 0}

            champion_data[nickname][champion]["games"] += 1
            if result == "승":
                champion_data[nickname][champion]["wins"] += 1

    # 각 플레이어별로 챔피언의 승률 및 게임 수를 기준으로 정렬


    for nickname, champs_data in champion_data.items():
        sorted_champs = sorted(champs_data.items(), key=lambda x: (-x[1]["wins"] / x[1]["games"], -x[1]["games"]))
        top_champions[nickname] = [
            (champ[0], champ[1]["wins"] / champ[1]["games"], champ[1]["games"], champ[1]["games"]) for champ in
            sorted_champs[:5]]

    # 결과 출력
    for nickname, champs in top_champions.items():
        print(f"{nickname}:")
        for champ, winrate, games, picks in champs:
            print(f"  {champ} - 승률: {winrate * 100:.2f}% ({games} 게임, {picks} 픽)")
        print()

def get_most5_champions_for_nickname(nickname):
    champs = top_champions.get(nickname, [])
    return champs

