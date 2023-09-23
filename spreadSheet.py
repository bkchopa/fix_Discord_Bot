import gspread
import os
import json
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
update_date = str()

async def reload():
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

    # 리스트를 역순으로 순회하면서 첫 번째로 나타나는 비지 않은 값을 찾습니다.

    # A열의 데이터를 읽어옴
    values_in_column_A = rowDatasSheet.col_values(1)

    # 각 팀의 마지막 게임 인덱스를 저장하는 딕셔너리 초기화
    team_indices = {}

    # A열의 데이터를 역순으로 검사
    for value in reversed(values_in_column_A):
        if not value:  # 빈 값은 건너뜀
            continue

        date, indices = value.split(" ")
        month, day = date.split('-')  # 날짜 정보 분리
        formatted_date = f"{month}월 {day}일"  # 변환된 형식
        team, game_index = indices.split("-")

        # 해당 팀의 마지막 게임 인덱스가 아직 저장되지 않았다면 저장
        if team not in team_indices:
            team_indices[team] = game_index

    # 저장된 데이터를 기반으로 원하는 문자열 형태로 변환
    result = " ".join([f"{team}-{team_indices[team]}" for team in sorted(team_indices.keys())])

    global update_date
    update_date = f"{formatted_date} {result}까지 반영"


