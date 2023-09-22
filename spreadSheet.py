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
worksheet = spreadsheet.worksheet("기입")

# 데이터 읽기와 쓰기 예제
#print(worksheet.get_all_records())  # 모든 데이터 가져오기
#worksheet.update_cell(1, 1, "Hello World!")  # 1행 1열에 "Hello World!" 입력

async def reload():
    all_data = worksheet.get_all_values()
    all_data = all_data[::-1]  # all_data 리스트를 거꾸로 뒤집어서 처리
    for row in all_data:
        position = row[1]
        nickname = row[2]
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
        nickname = row[10]
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



    print('시트 읽어오기 완료')

player_info = {}
reload()


