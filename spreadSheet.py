import gspread
import os
import json
import re
from oauth2client.service_account import ServiceAccountCredentials
import time

MAX_RETRIES = 18
RETRY_WAIT_TIME = 10  # 10 seconds

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

SPREADSHEET_IDS_JSON = os.environ.get('SPREADSHEET_IDS_JSON', '{}')
SPREADSHEET_IDS = None
last_key = None
last_spreadsheet_id = None
try:
    SPREADSHEET_IDS = json.loads(SPREADSHEET_IDS_JSON)
except json.JSONDecodeError:
    SPREADSHEET_IDS = {}  # JSON 파싱에 실패하면 빈 딕셔너리를 사용합니다.

# 워크시트 선택
if SPREADSHEET_IDS:
    last_key = list(SPREADSHEET_IDS.keys())[-1]  # 딕셔너리의 마지막 키 가져오기
    last_spreadsheet_id = SPREADSHEET_IDS[last_key]
    rankingSheet = client.open_by_key(last_spreadsheet_id).worksheet("내전 순위")
else:
    last_spreadsheet_id = None  # SPREADSHEET_IDS가 빈 딕셔너리인 경우에 대비


# 데이터 읽기와 쓰기 예제
#print(worksheet.get_all_records())  # 모든 데이터 가져오기
#worksheet.update_cell(1, 1, "Hello World!")  # 1행 1열에 "Hello World!" 입력
player_info = {}
player_ranking = {}
update_date = ""
top_champions = {}

def get_most_champions_for_nickname(nickname, count=5):
    champs = top_champions.get(nickname, [])
    return champs[:count]

def get_monthly_data(nickname, target_month):
    """
    닉네임과 타겟 월을 기반으로 해당 월의 데이터만 추출
    """
    monthly_data = []
    if nickname in player_info:
        # 해당 닉네임의 모든 데이터를 확인하며 월이 일치하는 데이터만 추출
        for data in player_info[nickname]:
            if "YYMM" in data:
                if data["YYMM"] == target_month:
                    monthly_data.append(data)
    return monthly_data

LAST_READ_ROW = 0  # 마지막으로 읽은 행을 전역 변수로 저장
IS_FIRST_LOAD = True  # 첫 로드를 판별하는 플래그

async def reload():
    global update_date, LAST_READ_ROW, IS_FIRST_LOAD
    player_ranking.clear()
    top_champions.clear()
    print('시트 전체')
    if IS_FIRST_LOAD:  # 첫 로드 시 모든 시트 읽기
        player_info.clear()
        sheet_ids = SPREADSHEET_IDS.items()
    else:  # 첫 로드가 아니면 마지막 시트만 읽기
        sheet_ids = [list(SPREADSHEET_IDS.items())[-1]]

    for YYMM, spreadsheet_id in sheet_ids:
        spreadsheet = client.open_by_key(spreadsheet_id)
        rowDatasSheet = spreadsheet.worksheet("기입")
        all_data = {}
        last_row = LAST_READ_ROW

        for i in range(MAX_RETRIES):
            try:
                if IS_FIRST_LOAD:
                    print(f'{YYMM} 시트 불러오는 중')
                    all_data = rowDatasSheet.get_all_values()
                    print(f'{YYMM} 시트 불러오기 완')
                else:
                    start_row = LAST_READ_ROW + 1
                    end_row = rowDatasSheet.row_count
                    print(start_row, end_row)
                    range_str = f"A{start_row}:Z{end_row}"
                    all_data = rowDatasSheet.get(range_str)

                break
            except gspread.exceptions.APIError:
                time.sleep(RETRY_WAIT_TIME)
                continue
        print(f'{YYMM} 시트 데이터 파싱')

        for row in all_data:
            try:
                last_row += 1
                if len(row) < 17:
                    continue

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
                    {
                        "YYMM": YYMM,
                        "champion": champion,
                        "position": position,
                        "result": result,
                        "kill": kill,
                        "death": death,
                        "assist": assist
                    }
                )

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
                    {
                        "YYMM": YYMM,
                        "champion": champion,
                        "position": position,
                        "result": result,
                        "kill": kill,
                        "death": death,
                        "assist": assist
                    }
                )

                if list(SPREADSHEET_IDS.values())[-1] == spreadsheet_id:
                    LAST_READ_ROW = last_row
            except IndexError:
                print(f"Error with row {last_row}: {row}")



    print('랭킹')
    #랭킹
    all_values = {}
    for i in range(MAX_RETRIES):
        try:
            # 시트에 쓰기 시도
            all_values = rankingSheet.get_all_values()
            break
        except gspread.exceptions.APIError:  # 여기서 오류 유형을 확인하고 적절한 예외로 대체해야 합니다.
            time.sleep(RETRY_WAIT_TIME)  # 일정 시간 동안 대기
            continue  # 다시 시도

    # E열(등수), F열(닉네임), G열(점수)부터 시작하는 부분만 추출
    ranked_data = [{"nickname": row[5].lower(), "rank": row[4], "score": row[6]} for row in all_values[2:]]
    # 닉네임을 키로 하고, 등수와 점수를 값으로 하는 딕셔너리 생성
    for item in ranked_data:
        player_ranking[item["nickname"]] = {"rank": item["rank"], "score": item["score"]}

    print('날짜')

    #날짜
    values_in_column_A={}
    for i in range(MAX_RETRIES):
        try:
            # 시트에 쓰기 시도
            values_in_column_A = client.open_by_key(last_spreadsheet_id).worksheet("기입").col_values(1)
            break
        except gspread.exceptions.APIError:  # 여기서 오류 유형을 확인하고 적절한 예외로 대체해야 합니다.
            time.sleep(RETRY_WAIT_TIME)  # 일정 시간 동안 대기
            continue  # 다시 시도

    team_indices = {}
    latest_date = None

    for value in reversed(values_in_column_A):
        if not value:  # 빈 값은 건너뜀
            continue

        match = re.match(r"(\d+-\d+) (\d+)-(\d+)", value)
        if not match:  # 9-2 1-8 형식의 데이터만 처리
            continue

        date, team, game_index = match.groups()

        # 최신 날짜 업데이트
        if not latest_date:
            latest_date = date

        # 해당 날짜의 모든 팀의 게임 인덱스 저장
        if date == latest_date:
            if team not in team_indices:
                team_indices[team] = []
            team_indices[team].append(game_index)
        else:
            break  # 최신 날짜만 고려하므로 나머지는 처리할 필요 없음

    # 1, 2, 3 팀 중 기록되지 않은 팀의 게임 인덱스를 0-0으로 설정
    for team_num in ['1', '2', '3']:
        if team_num not in team_indices:
            team_indices[team_num] = ['0']

    # 가장 큰 게임 인덱스만 선택
    for team, indices in team_indices.items():
        team_indices[team] = max(indices, key=int)  # 숫자로 변환해서 비교

    # 월-일을 월 일 형식으로 변경
    latest_date = latest_date.replace("-", "월 ") + "일"

    # 저장된 데이터를 기반으로 원하는 문자열 형태로 변환
    result = ", ".join([f"{team}-{team_indices[team]}" for team in sorted(team_indices.keys())])

    update_date = f"{latest_date} {result}까지 반영"

    print('모스트 픽 불러오기')
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
        top_champions[nickname] = {}
        sorted_champs = sorted(champs_data.items(), key=lambda x: (-x[1]["games"], -x[1]["wins"] / x[1]["games"]))
        top_champions[nickname] = [
            (champ[0], champ[1]["wins"] / champ[1]["games"], champ[1]["games"]) for champ in sorted_champs[:10]
        ]

    IS_FIRST_LOAD = False  # 첫 로드가 끝나면 플래그를 False로 설정

def find_empty_row(worksheet, index = 1):
    """해당 열에서 첫번째 빈 행의 번호를 반환"""
    all_values = worksheet.col_values(index)
    return len(all_values) + 1


def input_data_to_spreadsheet(data):

    spreadsheet_id = '10qFR8Nk29c0-pendLFn0fbU8mmm27ugYYa_VsES0Kao'
    sheet = client.open_by_key(spreadsheet_id).worksheet('시트1')

    #last_key = list(SPREADSHEET_IDS.keys())[-1]  # 딕셔너리의 마지막 키 가져오기
    #last_spreadsheet_id = SPREADSHEET_IDS[last_key]
    #sheet = client.open_by_key(last_spreadsheet_id).worksheet("기입")


    win_team = [player for player in data if player['win'] == 'Win']
    lose_team = [player for player in data if player['win'] == 'Lose']

    starting_row = find_empty_row(sheet, 2)

    with open("champion_id_name_map_korean.json", "r", encoding="utf-8") as f:
        champion_map = json.load(f)

    all_rows = []
    for win_player, lose_player in zip(win_team, lose_team):
        # 승리팀 데이터 생성
        values_for_win = [win_player['position'], convert_to_main_nick_using_sheet(win_player['nickname']), champion_map.get(win_player['champion'], "Unknown Champion"), "승", 1,
                          win_player['kills'], win_player['deaths'], win_player['assists']]

        # 패배팀 데이터 생성
        values_for_lose = [lose_player['position'], convert_to_main_nick_using_sheet(lose_player['nickname']), champion_map.get(lose_player['champion'], "Unknown Champion"), "패",
                           1, lose_player['kills'], lose_player['deaths'], lose_player['assists']]

        combined_row = values_for_win + values_for_lose
        all_rows.append(combined_row)

    # 한 번의 API 호출로 여러 줄을 업데이트
    range_name = f"B{starting_row}:Q{starting_row + len(all_rows) - 1}"
    sheet.update(range_name, all_rows)

mapping = {}
def create_mapping_from_sheet():
    sheet = client.open_by_key(last_spreadsheet_id).worksheet("부캐")
    print(last_spreadsheet_id)
    print("부캐시트 읽기")
    """Create a dictionary mapping from sub-character nickname to main character nickname using data from a Google Sheet."""
    data = sheet.get_all_values()  # Get all data from the sheet
    for row in data[1:]:  # Exclude header row
        main_nick = row[0]
        for sub_nick in row[1:]:
            if sub_nick:  # if not empty
                mapping[sub_nick] = main_nick

    print(mapping)

def convert_to_main_nick_using_sheet(nickname):
    """Convert a given nickname to its main nickname using a mapping dictionary."""
    return mapping.get(nickname, nickname)