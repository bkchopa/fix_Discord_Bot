import sys

import discord
import os
import json
from discord.ext import commands, tasks
import datetime
from datetime import datetime
import random
import asyncio
import spreadSheet
from common import team1_list, team2_list, team3_list, team_lists
import common
import re

import riot_api_utils  # 앞서 생성한 riot_api_utils.py를 사용
from threading import Thread
import threading
from flask import Flask,request,jsonify
from auction_commands import AuctionCommands
import signal


intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

bot.add_cog(AuctionCommands(bot))
bot.load_extension("player_statistics")

macpanList = dict()
maxTeam = 3
waitList = list()
test = "927502689913430057"


async def sendToChannel(message: str, id: int = 890160605246414848):
    channel = bot.get_channel(id)
    await channel.send(message)
@tasks.loop(hours=1)
async def resetList():
    await spreadSheet.reload() #1시간마다 한번씩 시트 읽어오기
    #채널 이름 바꾸기
    channel = bot.get_channel(1154474032310259733)
    if channel:  # Check if channel exists
        if channel.permissions_for(channel.guild.me).manage_channels:
            new_name = f"FixGG {spreadSheet.update_date}"
            safe_name = new_name.replace(' ', '_')
            await channel.edit(name=safe_name)

    spreadSheet.update_date
    hour = datetime.now().hour
    if hour is 22:
        ch = bot.get_channel(890160605246414848)
        await ch.send("명단 리셋합니다!")
        waitList.clear()
        await printlist(ch)



async def printlist(ctx: discord.ext.commands.context.Context):
    ret = "대기인원: "
    idx = 1
    for name in waitList:
        ret += str(idx)
        idx += 1
        ret += '. '
        ret += name
        ret += " "
    await ctx.send(ret)

    if len(waitList) == 0:
        await ctx.send('현재 대기 없음')


async def not_here(ctx: discord.ext.commands.context.Context):
    await ctx.send("대기순번체크 채널을 이용해주세요! 메세지는 4초 뒤 삭제됩니다")
    await asyncio.sleep(4)
    await ctx.channel.purge(limit=2)

@bot.event
async def on_ready():
    global waitList
    waitList = []  # waitList 초기화

    print(f"봇={bot.user.name}로 연결중")
    print('연결이 완료되었습니다.')
    ch = bot.get_channel(890160605246414848)
    i = 1
    while i <= maxTeam:
        macpanList[i] = 0
        i += 1

    #닉네임 - summonerID 저장
    for guild in bot.guilds:
        nickname_list = [member.nick.split('/')[0] for member in guild.members if member.nick]
        await riot_api_utils.update_summoner_id_dict(nickname_list)

    #await ch.send("내전 봇 재시작(약 24시간마다 자동재시작)")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("내전 명단관리 열심히"))

    bot_messages = await ch.history(limit=100).flatten()
    bot_messages = [msg for msg in bot_messages if msg.author == bot.user]
    #await ch.send("재시작전 대기인원을 불러옵니다...")
    for bot_msg in bot_messages:
        if bot_msg.content.startswith("대기인원:"):
            text = bot_msg.content.replace("대기인원:", "").strip()
            # 정규 표현식 패턴으로 번호와 뒤이어 오는 문자열(닉네임)을 찾습니다.
            pattern = re.compile(r'\d+\.\s+([^\d]+(?:\s+[^\d]+)*)')
            matches = pattern.findall(text)

            for match in matches:
                waitList.append(match.strip())  # 공백을 제거하고 waitList에 추가

            #await printlist(ch)
            break

    if not resetList.is_running():
        print('시트 불러오기 시작')
        resetList.start()




async def update_macpan_list(team: str, count: str, ctx=None):

    try:
        count_int = int(count[0])
        team_int = int(team[0])
    except ValueError:
        if ctx:
            await ctx.send('잘못된 입력')
        return

    if team_int not in [1, 2, 3] or count_int < 0:
        if ctx:
            await ctx.send('잘못된 입력')
        return

    global team_data

    if team_lists[team]["alert_sent"] == "Idle":
        team_lists[team]["alert_sent"] = "Ready"


    macpanList[team_int] = count_int

    retStr = f"막판  1팀 {macpanList[1]}명   2팀 {macpanList[2]}명   3팀 {macpanList[3]}명"
    await bot.change_presence(activity=discord.Game(retStr))

@bot.command()
async def 막판(ctx, team: str, count: str, *, text=None):
    await update_macpan_list(team, count, ctx)



@bot.command(aliases=["check", "췤", "첵", "쳌", "채크", "ㅊㅋ","cz","CZ","Cz","cZ"])
async def 체크(ctx, *, text=None):
    if ctx.channel.id != 890160605246414848:
        await not_here(ctx)
        return
    print('체크 :')
    if text is None:
        nickname = ctx.message.author.nick
        arr = nickname.split('/')
        if arr[0] not in waitList:
            print(arr[0])
            waitList.append(arr[0])
        await printlist(ctx)
        return
    if text == '!대기':
        return
    if text == '예+비':
        waitList.append('예비신랑입니다')
        waitList.append('비슈비슈')
        await printlist(ctx)
        return
    if text not in waitList:
        print(text)
        waitList.append(text)

    await printlist(ctx)


@bot.command()
async def 양보(ctx, * ,text):
    if ctx.channel.id != 890160605246414848:
        await not_here(ctx)
        return
    print('양보 :')
    print(text)
    if text in waitList:
        waitList.remove(text)

    waitList.insert(0, text)

@bot.command(aliases=["취", "ㅊㅅ", "ct", "CT", "부취", "범취"])
async def 취소(ctx, *, text=None):
    if ctx.channel.id != 890160605246414848:
        await not_here(ctx)
        return

    # 닉네임 기반 제거
    if text is None:
        nickname = ctx.message.author.nick.split('/')[0]
        if nickname in waitList:
            waitList.remove(nickname)
        await printlist(ctx)
        return

    # 특정 인덱스 제거
    try:
        index = int(text) - 1
        if 0 <= index < len(waitList):
            del waitList[index]
        await printlist(ctx)
        return
    except ValueError:
        pass  # 숫자 변환에 실패하면 계속 진행

    # 여러 인덱스 제거
    if ',' in text:
        indices = sorted([int(i) - 1 for i in text.split(',') if i.isdigit()], reverse=True)
        for index in indices:
            if 0 <= index < len(waitList):
                del waitList[index]
        await printlist(ctx)
        return

    # 범위 기반 제거
    if '~' in text:
        start, _, end = text.partition('~')
        start_idx = int(start) - 1
        end_idx = int(end) - 1
        for index in range(end_idx, start_idx - 1, -1):  # 역순으로 삭제 (인덱스 오류 방지)
            if 0 <= index < len(waitList):
                del waitList[index]
        await printlist(ctx)
        return

    # 닉네임 기반 제거
    if text in waitList:
        waitList.remove(text)
        await printlist(ctx)
        return

    # 그 외의 경우
    await ctx.send('잘못된 입력')



@bot.command(aliases=["ㄷㄱ","er","ER"])
async def 대기(ctx, text=None):
    if ctx.channel.id != 890160605246414848:
        await not_here(ctx)
        return
    print('대기요청')
    ch = bot.get_channel(927502689913430057)
    if text is not None:
        await ctx.send('대기말고 체크 해주세요 ^^')
        return

    await printlist(ctx)


@bot.command()
async def 새치기(ctx, text1, text2):
    index = int(text1) - 1
    if index < 0 or index >= len(waitList):
        await ctx.send('없는 번호')
    if text2 in waitList:
        waitList.remove(text2)

    waitList.insert(index, text2)


@bot.command(aliases=["팀취", "ㅌㅊ"])
async def 팀취소(ctx, teamNum):
    try:
        num = int(teamNum)
    except ValueError:
        await ctx.send('잘못 된 입력')
        return

    if num > 4 or num <= 0:
        return

    if num == 1:
        ch = bot.get_channel(int(common.team1))
    elif num == 2:
        ch = bot.get_channel(int(common.team2))
    elif num == 3:
        ch = bot.get_channel(int(common.team3))
    elif num == 4:
        ch = bot.get_channel(int(common.team4))

    for member in ch.members:
        #if member.voice.self_mute:
            #continue
        nickname = member.nick
        realNick = nickname.split('/')[0]

        if realNick in waitList:
            waitList.remove(realNick)

    await printlist(ctx)


@bot.command(aliases=["ㅌㅃ"])
async def 팀뽑(ctx, teamNum):
    if ctx.channel.id != 890160605246414848:
        await not_here(ctx)
        return
    try:
        num = int(teamNum)
    except ValueError:
        await ctx.send('잘못 된 입력')
        return

    if num > 3 or num <= 0:
        return

    if num == 1:
        ch = bot.get_channel(int(common.team1))
    elif num == 2:
        ch = bot.get_channel(int(common.team2))
    elif num == 3:
        ch = bot.get_channel(int(common.team3))

    if len(ch.members) == 0:
        return

    ranNum = random.randrange(0, len(ch.members))

    test2 = ch.members[ranNum]

    await ctx.send(str(num) + "팀 팀뽑 할사람 : " + test2.nick)


@bot.command(aliases=["랜덤뽑기", "사다리"])
async def 랜뽑(ctx, text):
    arr = text.split(',')
    if len(arr) == 0:
        return
    ranNum = random.randrange(0, len(arr))
    await ctx.send('당첨자는~ ' + arr[ranNum] + '!')


@bot.command(name="1팀")
async def team1_command(ctx, *, args):
    await process_alternate_format(ctx, "1팀", args)

@bot.command(name="2팀")
async def team2_command(ctx, *, args):
    await process_alternate_format(ctx, "2팀", args)

@bot.command(name="3팀")
async def team3_command(ctx, *, args):
    await process_alternate_format(ctx, "3팀", args)

async def process_alternate_format(ctx, team: str, args: str):
    parts = args.split()
    if len(parts) < 2 or parts[0] != "막판":
        await ctx.send('잘못된 입력')
        return
    await update_macpan_list(team, parts[1], ctx)

@bot.command(aliases=["ㄽ"])
async def 리셋(ctx):
    if ctx.channel.id != 890160605246414848:
        await not_here(ctx)
        return
    waitList.clear()
    await printlist(ctx)

@bot.command()
async def 복구(ctx, *, text=None):
    if text is None:
        return
    waitList.clear()
    start = int()
    end = int()
    i = 1
    while True:
        start = text.find(str(i) + '.')
        end = text.find(str(i+1) + '.')
        if start == -1:
            return

        if end == -1:
            end = len(text) + 1

        nickName = text[start + 3:end - 1]
        waitList.append(nickName)
        i += 1

def parse_indices(index_str):
    if '~' in index_str:
        start, end = map(int, index_str.split('~'))
        return list(range(start - 1, end))
    elif ',' in index_str:
        return [int(i) - 1 for i in index_str.split(',')]
    else:
        return [int(index_str) - 1]


def generate_mentions(members, indices):
    mentions = []

    for idx in indices:
        if idx < 0 or idx >= len(waitList):
            continue
        waiting = waitList[idx]
        for member in members:
            if member.nick:
                realNick = member.nick.split('/')[0]
                if waiting == realNick:
                    mentions.append(f"<@{member.id}>")
                    break
    return ' '.join(mentions)
def process_mention_command(ctx, index_str, additional_text=None):
    indices = parse_indices(index_str)
    if not indices:
        raise ValueError("잘못된 번호 입력")

    mention_str = generate_mentions(ctx.guild.members, indices)
    if not mention_str:
        raise ValueError("멘션할 사용자를 찾을 수 없습니다.")

    if additional_text:
        mention_str += " " + additional_text

    return mention_str

@bot.command(aliases=["멘션", "ㅁㅅ", "at"])
async def 맨션(ctx, index, *, text=None):
    try:
        mention_str = process_mention_command(ctx, index, text)
        await ctx.send(mention_str)
    except ValueError as e:
        await ctx.send(str(e))


async def get_user_count(channel_id):
    channel = bot.get_channel(channel_id)
    if channel:
        return len(channel.members)
    return 0


async def get_total_user_count_in_channels(channel_ids, count_only_mic_users=False):
    total_user_count = 0
    for channel_id in channel_ids:
        channel = bot.get_channel(channel_id)
        if channel:
            for member in channel.members:
                if count_only_mic_users:
                    # 마이크를 끈 멤버는 카운트하지 않습니다.
                    voice_state = member.voice
                    if voice_state and not voice_state.self_mute:
                        total_user_count += 1
                else:
                    # 모든 멤버를 카운트합니다.
                    total_user_count += 1
    return total_user_count

@bot.event
async def on_voice_state_update(member, before, after):
    # 나갈 때
    if before.channel:
        for team_name, team_data in team_lists.items():
            if before.channel.id in team_data["ids"]:
                total_user_count_in_team = await get_total_user_count_in_channels(team_data["ids"][1:], True)
                total_user_count_in_lobby = await get_total_user_count_in_channels([team_data["ids"][0]])

                total_user_count = total_user_count_in_team + total_user_count_in_lobby
                # 로비 인원이 팀룸의 인원보다 많은 경우
                if total_user_count_in_lobby > total_user_count_in_team and team_data["alert_sent"] == "Started":
                    await update_macpan_list(team_name, '0명')
                    team_data["alert_sent"] = "Idle"  # Reset the flag when lobby has more members
                # 전체 인원(로비 + 팀룸)이 4명 이하로 남아 있는 경우
                elif total_user_count <= 4 and team_data["alert_sent"] == "Started":
                    await update_macpan_list(team_name, '0명')
                    team_data["alert_sent"] = "Idle"  # Reset the flag when total user count is less than or equal to 4
                # 룸의 인원이 로비의 인원보다 많고, 이전에 알림을 보낸 적이 없는 경우
                elif total_user_count_in_lobby != 0 and total_user_count_in_team > total_user_count_in_lobby and team_data["alert_sent"] !="Started" and macpanList[int(team_name[0])] == 0:
                    if team_data["alert_sent"] == "Idle":
                        # Get a random member from the room and send a mention
                        room_channel = bot.get_channel(team_data["ids"][1])  # Assuming id[1] is a team room
                        if room_channel and room_channel.members:
                            member_to_mention = random.choice(room_channel.members)
                            print(member_to_mention.name)
                            await sendToChannel(f"{member_to_mention.mention} 막판 체크 해주세요!")
                        room_channel2 = bot.get_channel(team_data["ids"][2])  # Assuming id[2] is a team room
                        if room_channel2 and room_channel2.members:
                            member_to_mention = random.choice(room_channel2.members)
                            print(member_to_mention.name)
                            await sendToChannel(f"{member_to_mention.mention} 막판 체크 해주세요!")

                    team_data["alert_sent"] = "Started"


                break  # 리스트 중 하나에서 일치하는 ID를 찾았다면 추가 탐색 중단





@bot.command()
async def 유저(ctx, *, summoner_name: str):
    # Riot API를 이용하여 소환사의 정보를 가져오기
    summoner_info = riot_api_utils.get_summoner_info(summoner_name)

    if not summoner_info:
        await ctx.send("소환사를 찾을 수 없습니다.")
        return

    summoner_id = summoner_info['id']

    # 현재 게임 정보를 가져오기
    current_game_info = riot_api_utils.get_current_game_info(summoner_id)
    if not current_game_info:
        await ctx.send("소환사가 게임 중이 아닙니다.")
        return

    # 챔피언 ID-이름 매핑 정보를 불러오기
    with open("champion_id_name_map_korean.json", "r", encoding="utf-8") as f:
        champion_map = json.load(f)

    # 게임 정보 중에서 팀 정보, 챔피언 정보 등을 추출하여 메시지로 보내기
    for participant in current_game_info['participants']:
        if participant['summonerId'] == summoner_id:
            champion_id = participant['championId']
            team_id = participant['teamId']
            break

    # 챔피언 ID를 사용하여 챔피언의 이름을 가져오기
    champion_name = champion_map.get(str(champion_id), "Unknown Champion")

    await ctx.send(f"{summoner_name}님은 현재 {team_id}팀에서 {champion_name}으로 게임 중입니다.")

gameIDList = list()
@bot.command()
async def 채테(ctx, channel_id: int = None):
    global gameIDList
    gameIDList.append(channel_id)

@bot.command()
async def 채널(ctx, channel_id: int = None):
    # 채널 설정
    if channel_id:
        channel = bot.get_channel(channel_id)
    else:
        channel = ctx.author.voice.channel if ctx.author.voice else None

    if channel and isinstance(channel, discord.VoiceChannel):
        members = channel.members

        # 챔피언 ID를 챔피언 이름으로 맵핑하는 딕셔너리를 불러옴
        with open("champion_id_name_map_korean.json", "r", encoding='utf-8') as f:
            champ_id_to_name = json.load(f)

        game_info_dict = {}
        known_game_ids = set()

        for member in members:
            summoner_name = member.nick.split('/')[0]
            game_info = await riot_api_utils.get_game_info(summoner_name)

            if not game_info:
                continue  # 게임 정보가 없는 경우, 무시하고 계속 진행

            game_id = game_info['gameId']
            if game_id in known_game_ids:
                continue  # 이미 처리된 게임 ID인 경우, 무시하고 계속 진행

            # 이 summoner_name에 대한 게임 정보를 딕셔너리에 저장
            game_info_dict[summoner_name] = game_info

            # 이 게임에 동일하게 참여 중인 다른 사용자를 찾습니다.
            same_game_members = [
                s_name for s_name, s_game_info in game_info_dict.items()
                if s_game_info['gameId'] == game_id
            ]

            if len(same_game_members) >= 1:  # 조건을 만족하는지 확인
                print(f"{len(same_game_members)}명의 사용자가 게임 (ID: {game_id})에 참여하고 있습니다.")
                known_game_ids.add(game_id)  # 이 게임 ID는 처리 완료로 마킹합니다.

                if game_id not in gameIDList:
                    gameIDList.append(game_id)

                # 게임 참여자 정보 출력 등 원하는 로직을 여기에 추가합니다.
                #for participant in game_info['participants']:
                    #p_name = participant['summonerName']
                    #p_champion_id = participant['championId']
                    #p_team_id = participant['teamId']
                    #p_champion_name = champ_id_to_name.get(str(p_champion_id), "알 수 없는 챔피언")

                    #print(f"소환사 이름: {p_name}, 팀: {p_team_id}, 챔피언: {p_champion_name}")

    else:
        await ctx.send("음성 채널에 연결되어 있지 않거나 올바르지 않은 채널 ID를 제공하셨습니다.")



app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/api/greet', methods=['GET'])
def greet_api():
    print("greet_api")
    users = [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "age": 30
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "age": 28
        },
        {
            "id": 3,
            "name": "Bob Brown",
            "email": "bob.brown@example.com",
            "age": 22
        }
    ]
    return jsonify({"message": "Hello from the API!", "users": users})

@app.route('/api/game_list', methods=['GET'])
def game_list_api():
    global gameIDList
    print("game_list_api")
    print(gameIDList)
    return jsonify(gameIDList)

@app.route('/api/game_result', methods=['POST'])
def game_result():
    print('/api/game_result')
    """게임 결과 데이터를 받아 처리하는 엔드포인트."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # 여기서 데이터를 처리하거나 데이터베이스에 저장할 수 있습니다.
    # 예: save_to_database(data)

    print(data)
    spreadSheet.input_data_to_spreadsheet(data)

    return jsonify({"message": "Game data received successfully!"}), 200


def run_web_server():
    port = int(os.environ.get('PORT', 5000))
    try:
        app.run(host='0.0.0.0', port=port, use_reloader=False)
        print("Web server started successfully!")
    except Exception as e:
        print(f"Error starting web server: {e}")

def shutdown_handler(signum, frame):
    print("서버 죽음")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.logout())
    # 웹 서버 종료 로직 추가 (예: Flask의 경우 `stop()` 함수 등)
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, shutdown_handler)
    t = threading.Thread(target=run_web_server)
    t.start()
    bot.run(os.environ['Token'])

