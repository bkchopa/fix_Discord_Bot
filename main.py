import discord
import os
import json
from discord.ext import commands, tasks
import datetime
import random
import asyncio
from collections import defaultdict
import spreadSheet
from spreadSheet import player_info


intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

macpanList = dict()
maxTeam = 3

waitList = list()
team1 = "890160695499423774"
team2 = "921703036294926366"
team3 = "921703123221884969"
team4 ="1040618972497854565"
test = "927502689913430057"
auction = 988117624468680794
currentCount = -1
topbidder = ""
topprice = 0
lastMember =""
lastBidder =""
lastPrice = 0



remainMileageDic = dict()
memberListDic = defaultdict(list)
memberList = list()
missedMemberList = list()
currentAuctionMember = str()

def player_statistics(player_data):
    # Define positions in the order you want
    positions = ["TOP", "JUG", "MID", "ADC", "SUP"]

    total_games = len(player_data)
    wins = sum(1 for game in player_data if game['result'] == '승')
    losses = total_games - wins
    win_rate = (wins / total_games) * 100

    total_kills = sum(int(game['kill']) for game in player_data)
    total_deaths = sum(int(game['death']) for game in player_data)
    total_assists = sum(int(game['assist']) for game in player_data)

    avg_kill = total_kills / total_games
    avg_death = total_deaths / total_games
    avg_assist = total_assists / total_games

    kda = (total_kills + total_assists) / total_deaths if total_deaths != 0 else "Infinite"

    # Print overall statistics
    output = (f"총 전적 - {total_games}전 {wins}승/{losses}패 - {win_rate:.2f}% 승률 "
              f"Kill: {avg_kill:.2f} - Death: {avg_death:.2f} - Assist: {avg_assist:.2f} - KDA: {kda:.2f}\n")

    # Positional statistics
    for position in positions:
        position_games = [game for game in player_data if game['position'] == position]
        if not position_games:  # Skip if no games for this position
            continue

        pos_total_games = len(position_games)
        pos_wins = sum(1 for game in position_games if game['result'] == '승')
        pos_losses = pos_total_games - pos_wins
        pos_win_rate = (pos_wins / pos_total_games) * 100

        pos_total_kills = sum(int(game['kill']) for game in position_games)
        pos_total_deaths = sum(int(game['death']) for game in position_games)
        pos_total_assists = sum(int(game['assist']) for game in position_games)

        pos_avg_kill = pos_total_kills / pos_total_games
        pos_avg_death = pos_total_deaths / pos_total_games
        pos_avg_assist = pos_total_assists / pos_total_games

        pos_kda = (pos_total_kills + pos_total_assists) / pos_total_deaths if pos_total_deaths != 0 else "Infinite"

        output += (f"\n{position} 전적 - {pos_total_games}전 {pos_wins}승/{pos_losses}패 - {pos_win_rate:.2f}% 승률"
                   f"Kill: {pos_avg_kill:.2f} - Death: {pos_avg_death:.2f} - Assist: {pos_avg_assist:.2f} - KDA: {pos_kda:.2f}")

    return output

def player_statistics_resent10(player_data):
    recent_games = player_data[:10]
    recent_games = recent_games[::-1]
    returnTXT = ""
    winCnt = 0
    lossCnt = 0
    winStreak = 0
    lossStreak = 0
    for game in recent_games:
        champion = game['champion'].ljust(8)
        result = game['result'].center(2)
        if game['result'] == "승":
            winCnt += 1
            winStreak += 1
            lossStreak = 0
        else:
            lossCnt += 1
            lossStreak += 1
            winStreak = 0
        kda = f"{game['kill']}/{game['death']}/{game['assist']}".ljust(9)
        returnTXT += f"{champion} {result} {kda} \n"
    streak = ""
    if winStreak > lossStreak:
        streak = "(" + str(winStreak) + "연승중!)"
    else:
        streak = "(" + str(lossStreak) + "연패중 ㅜ)"

    return {
        "totalMatchCnt" : len(recent_games),
        "winCnt": winCnt,
        "lossCnt": lossCnt,
        "streak": streak,
        "result": returnTXT
    }

async def printlist(ctx: discord.ext.commands.context.Context):
    if len(waitList) == 0:
        await ctx.send('현재 대기 없음')
        return
    ret = "대기인원: "
    idx = 1
    for name in waitList:
        ret += str(idx)
        idx += 1
        ret += '. '
        ret += name
        ret += " "
    await ctx.send(ret)


async def not_here(ctx: discord.ext.commands.context.Context):
    await ctx.send("대기순번체크 채널을 이용해주세요! 메세지는 4초 뒤 삭제됩니다")
    await asyncio.sleep(4)
    await ctx.channel.purge(limit=2)

async def changetitle(ctx: discord.ext.commands.context.Context):
    return
    ch2 = bot.get_channel(927502689452040236)
    title = '대기순번체크 ' + str(len(waitList)) + '명'
    if len(waitList) == 0:
        await ctx.send('현재 대기 없음')
        return
    ret = ""
    idx = 1
    for name in waitList:
        ret += str(idx)
        idx += 1
        ret += '. '
        ret += name
        ret += " "
    await ch2.edit(topic=title)

@bot.event
async def on_ready():
    print(f"봇={bot.user.name}로 연결중")
    print('연결이 완료되었습니다.')
    ch = bot.get_channel(890160605246414848)
    i = 1
    while i <= maxTeam:
        macpanList[i] = 0
        i += 1


    #await ch.send("내전 봇 재시작(약 24시간마다 자동재시작)")
    resetList.start()
    counter.start()

    await bot.change_presence(status=discord.Status.online, activity=discord.Game("내전 명단관리 열심히"))

    bot_messages = await ch.history(limit=100).flatten()
    bot_messages = [msg for msg in bot_messages if msg.author == bot.user]
    #await ch.send("재시작전 대기인원을 불러옵니다...")
    for bot_msg in bot_messages:
        if bot_msg.content[:5] == "대기인원:":
            message_content = bot_msg.content
            text = message_content.replace("대기인원:", "").strip()
            start = int()
            end = int()
            i = 1
            while True:
                start = text.find(str(i) + '.')
                end = text.find(str(i + 1) + '.')
                if start == -1:
                    #await printlist(ch)
                    return

                if end == -1:
                    end = len(text) + 1

                nickName = text[start + 3:end - 1]
                waitList.append(nickName)
                i += 1
            return






@bot.command()
async def 막판(ctx, team, count, *, text=None):
    if team[1] != '팀':
        await ctx.send('잘못된 입력')
        return
    if count[1] != '명':
        await ctx.send('잘못된 입력')
        return

    team_int = 0
    count_int = 0

    try:
        team_int = int(team[0])
    except ValueError:
        await ctx.send('잘못된 입력')
        return

    try:
        count_int = int(count[0])
    except ValueError:
        await ctx.send('잘못된 입력')
        return

    macpanList[team_int] = count_int

    retStr = "막판  "
    retStr += "1팀 "
    retStr += str(macpanList[1]) + "명   "
    retStr += "2팀 "
    retStr += str(macpanList[2]) + "명    "
    retStr += "3팀 "
    retStr += str(macpanList[3]) + "명    "

    await bot.change_presence(activity=discord.Game(retStr))



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
async def 테스트(ctx):
    waitList.append('쵸파1')
    waitList.append('쵸파2')
    waitList.append('쵸파3')
    waitList.append('쵸파4')
    waitList.append('쵸파5')
    waitList.append('쵸파6')
    waitList.append('쵸파7')
    waitList.append('쵸파8')
    waitList.append('쵸파9')
    waitList.append('쵸파10')
    waitList.append('쵸파11')
    waitList.append('쵸파12')


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

    await changetitle(ctx)

@bot.command(aliases=["취","ㅊㅅ","ct","CT"])
async def 취소(ctx, *, text=None):
    if ctx.channel.id != 890160605246414848:
        await not_here(ctx)
        return
    if text is None:
        nickname = ctx.message.author.nick
        arr = nickname.split('/')
        if arr[0] in waitList:
            waitList.remove(arr[0])
            print('취소 :')
            print(arr[0])

        await printlist(ctx)
        return
    try:
        string_int = int(text)
        string_int -= 1
        if string_int < 0 or string_int >= len(waitList):
            await ctx.send('없는 번호')
            return
        print('취소 :')
        print(waitList[string_int])
        del waitList[string_int]

        await printlist(ctx)
    except ValueError:
        if text in waitList:
            print('취소 :')
            print(text)
            waitList.remove(text)
        else:
            await ctx.send('없는 닉네임')



@bot.command(aliases=["부취"])
async def 부분취소(ctx, text):
    arr = text.split(',')
    count = 0
    arr.sort(key=int)
    print('부분취소 :')
    print(text)
    for num in arr:
        try:
            string_int = int(num)
            string_int -= 1
            string_int -= count
            if string_int < 0 or string_int >= len(waitList):
                await ctx.send('없는 번호')
                return
            del waitList[string_int]
            count += 1
        except ValueError:
            continue
    await printlist(ctx)
    await changetitle(ctx)


@bot.command(aliases=["범취"])
async def 범위취소(ctx, text):
    arr = text.split('~')
    print('범위취소 :')
    print(text)
    count = 0
    try:
        string_int1 = int(arr[0])
        string_int2 = int(arr[1])
        string_int1 -= 1
        string_int2 -= 1
        if (string_int1 < 0 or string_int1 >= len(waitList)) or (string_int2 < 0 or string_int2 >= len(waitList)):
            await ctx.send('잘못된 번호')
            return
        while string_int1 <= string_int2:
            temp = string_int1 - count
            del waitList[temp]
            string_int1 += 1
            count += 1
    except ValueError:
        await ctx.send('잘못된 입력')
        return
    await printlist(ctx)
    await changetitle(ctx)


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
    await changetitle(ctx)


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
        ch = bot.get_channel(int(team1))
    elif num == 2:
        ch = bot.get_channel(int(team2))
    elif num == 3:
        ch = bot.get_channel(int(team3))
    elif num == 4:
        ch = bot.get_channel(int(team4))

    for member in ch.members:
        #if member.voice.self_mute:
            #continue
        nickname = member.nick
        realNick = nickname.split('/')[0]

        if realNick in waitList:
            waitList.remove(realNick)

    await printlist(ctx)
    await changetitle(ctx)


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
        ch = bot.get_channel(int(team1))
    elif num == 2:
        ch = bot.get_channel(int(team2))
    elif num == 3:
        ch = bot.get_channel(int(team3))

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


@bot.command(aliases=["1팀", "2팀", "3팀", "4팀"])
async def 막판방지(ctx, *, text):
    await ctx.send('!막판 *팀 *명 입니다 선생님')


@bot.command(aliases=["ㄽ"])
async def 리셋(ctx):
    if ctx.channel.id != 890160605246414848:
        await not_here(ctx)
        return
    waitList.clear()
    ctx.send('리셋됨')
    await changetitle(ctx)

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






@tasks.loop(hours=1)
async def resetList():
    await spreadSheet.reload() #1시간마다 한번씩 시트 읽어오기
    hour = datetime.datetime.now().hour
    if hour is 22:
        ch = bot.get_channel(890160605246414848)
        await ch.send("명단 리셋합니다!")
        waitList.clear()
        await printlist(ch)


@bot.command()
async def 경매시작(ctx):
    global currentCount
    currentCount = 10



@bot.command()
async def 입찰(ctx, text):
    nickname = ctx.message.author.nick
    arr = nickname.split('/')
    leader = arr[0].replace(" " , "")
    if not leader in memberListDic:
        await ctx.send("당신은 팀장이 아닌걸요?")
        return

    global currentCount
    global topprice
    global topbidder
    if currentCount <= 0:
        return

    try:
        price = int(text)
    except ValueError:
        await ctx.send('잘못 된 입력')
        return

    if price <= topprice:
        return

    if remainMileageDic[leader] < price:
        await ctx.send(leader + "씨 돈이 부족해요")
        return


    if topbidder == leader:
        return

    currentCount = 10
    topprice = price
    topbidder = leader
    retStr = "현재 상위 입찰자 : " + str(topbidder) +" 입찰가 : " + str(topprice)
    await ctx.send(retStr)




@tasks.loop(seconds=1)
async def counter():
    global currentCount
    global currentAuctionMember
    global lastMember
    global lastBidder
    global lastPrice

    if currentAuctionMember == "":
        return

    if currentCount < 0:
        return

    ch = bot.get_channel(auction)
    if currentCount == 0:
        global topprice
        global topbidder
        if topprice == 0:
            missedMemberList.append(currentAuctionMember)
            await ch.send("유찰되었습니다 ㅜ")
        else:
            retStr = "경매종료:" + currentAuctionMember + " 낙찰자 : " + str(topbidder) +" 입찰가 : " + str(topprice)
            memberListDic[topbidder].append(currentAuctionMember)
            remainMileageDic[topbidder] -= topprice
            await ch.send(retStr)


        lastMember = currentAuctionMember
        lastBidder = topbidder
        lastPrice = topprice
        currentAuctionMember = ""
        currentCount = -1
        topprice = 0
        topbidder = 0

        retStr = "현재 남은 매물 : "
        for member in memberList:
            retStr += member + " "

        retStr += "\n"

        retStr += "유찰 매물     : "
        for member in missedMemberList:
            retStr += member + " "

        retStr += "\n\n\n\n"

        for leader in remainMileageDic:
            tempStr = leader
            tempStr += "("
            tempStr += str(remainMileageDic[leader])
            tempStr += ") :"
            for name in memberListDic[leader]:
                tempStr += name
                tempStr += " "
            tempStr += "\n"
            retStr += tempStr

        await ch.send(retStr)
        return

    msg = await ch.send(currentCount)
    currentCount-=1


@bot.command()
async def 매물등록(ctx, Participants):
    arr = Participants.split(',')
    if len(arr) == 0:
        return

    for Participant in arr:
        memberList.append(Participant)

@bot.command()
async def 매물추가(ctx, Participant):
    memberList.append(Participant)

@bot.command()
async def 매물제거(ctx, Participant):
    if Participant not in memberList:
        return

    memberList.remove(Participant)

@bot.command()
async def 매물섞기(ctx, Participant):
    random.shuffle(memberList)

@bot.command()
async def 다음매물(ctx):
    if len(memberList) == 0:
        return

    targetMember = memberList[0]
    #targetMember = random.choice(memberList)
    await ctx.send('다음 매물은 ' + targetMember + '!')
    global currentAuctionMember
    currentAuctionMember = targetMember
    memberList.remove(targetMember)

@bot.command()
async def 수동매물등록(ctx, member):
    if member not in memberList:
        return

    await ctx.send('다음 매물은 ' + member + '!')
    global currentAuctionMember
    currentAuctionMember = member
    memberList.remove(member)

@bot.command()
async def 자동배정(ctx, leader, member):
    if not leader in memberListDic:
        await ctx.send("팀장을 잘못 적으셨어요")
        return

    if not member in memberList:
        await ctx.send("팀원을 잘못 적으셨어요")
        return

    memberListDic[leader].append(member)
    memberList.remove(member)

@bot.command()
async def 팀장등록(ctx, leader, mileage):
    try:
        price = int(mileage)
    except ValueError:
        await ctx.send('잘못 된 입력')
        return

    remainMileageDic[leader] = int(mileage)
    memberListDic[leader] = list()

@bot.command()
async def 팀장제거(ctx, leader, mileage):
    if leader not in memberListDic:
        await ctx.send("팀장을 잘못 적으셨어요")
        return
    del remainMileageDic[leader]
    del memberListDic[leader]

@bot.command()
async def 팀장마일리지추가(ctx, leader, mileage):
    if not leader in memberListDic:
        await ctx.send("팀장을 잘못 적으셨어요")
        return

    try:
        price = int(mileage)
    except ValueError:
        await ctx.send('잘못 된 입력')
        return

    remainMileageDic[leader] += price


@bot.command()
async def 경매현황(ctx):
    retStr =  "현재 남은 매물 : "
    for member in memberList:
        retStr += member + ","

    retStr += "\n\n"

    retStr += "유찰 매물     : "
    for member in missedMemberList:
        retStr += member + ","

    retStr += "\n\n\n\n"

    for leader in remainMileageDic:
        tempStr = leader
        tempStr += "("
        tempStr += str(remainMileageDic[leader])
        tempStr += ") :"
        for name in memberListDic[leader]:
            tempStr += name
            tempStr += " "
        tempStr += "\n"
        retStr += tempStr

    await ctx.send(retStr)


@bot.command()
async def 팀원제거(ctx, leader, member):
    if leader not in memberListDic:
        await ctx.send("팀장을 잘못 적으셨어요")
        return

    if member not in memberListDic[leader]:
        await ctx.send("그런 팀원 없어요")
        return

    memberListDic[leader].remove(member)
    memberList.append(member)

@bot.command()
async def 팀원추가(ctx, leader, member):
    if leader not in memberListDic:
        await ctx.send("팀장을 잘못 적으셨어요")
        return

    if member not in memberList:
        await ctx.send("그런 매물 없어요")
        return

    memberListDic[leader].append(member)
    memberList.remove(member)

@bot.command()
async def 유찰복구(ctx):
    global memberList
    memberList = missedMemberList.copy()
    missedMemberList.clear()

@bot.command()
async def 되돌리기(ctx):
    global lastMember
    global lastBidder
    global lastPrice

    if lastMember == "":
        return

    if lastBidder == "":
        return


    if lastMember not in memberListDic[lastBidder]:
        await ctx.send("잘못 된 입력")
        return

    try:
        int(lastPrice)
    except ValueError:
        await ctx.send('잘못 된 입력')
        return


    memberListDic[lastBidder].remove(lastMember)
    memberList.append(lastMember)
    remainMileageDic[lastBidder] += int(lastPrice)
    lastMember = ""
    lastBidder = ""
    lastPrice = 0


@bot.command()
async def 대진표(ctx):
    teamList = list()
    for leader in memberListDic:
        teamList.append(leader)

    if len(teamList) == 0:
        return

    if len(teamList) % 2 != 0:
        return

    retStr =""
    while len(teamList) != 0:

        team1 = random.choice(teamList)
        team2 = random.choice(teamList)
        if team1 == team2:
            continue

        retStr = team1 + " 팀 vs" +team2 + " 팀\n"
        teamList.remove(team1)
        teamList.remove(team2)

        await ctx.send(retStr)
        retStr =""

@bot.command()
async def 경매종료(ctx):
    global currentAuctionMember
    global currentCount
    currentAuctionMember = ""
    currentCount = -1

@bot.command()
async def 경매리셋(ctx):
    global currentAuctionMember
    global topbidder
    global topprice
    global lastMember
    global lastBidder
    global lastPrice
    global remainMileageDic
    global memberListDic
    global memberList
    global missedMemberList

    topbidder = ""
    topprice = 0
    lastMember = ""
    lastBidder = ""
    lastPrice = 0

    remainMileageDic.clear()
    memberListDic.clear()
    memberList.clear()
    missedMemberList.clear()
    currentAuctionMember = ""

@bot.command(aliases=["도움"])
async def 도움말(ctx):
    retStr ="명령어 목록\n"
    retStr += "!체크 [닉네임] or [순번]    : 내전 대기열에 등록 합니다 닉네임을 입력하지 않으면 본인을 체크합니다.\n"
    retStr += "!취소 [닉네임] or [순번]     : 내전 대기열에서 등록취소 합니다 닉네임을 입력하지 않으면 본인이 취소됩니다.\n"
    retStr += "!범취 [순번1~순번2]         : 내전 대기열에서 순번1에서 순번2까지 해당되는 인원들을 등록 취소 합니다.\n"
    retStr += "!부취 [순번1,순번2,...]     : 내전 대기열에서 순번1,순번2,....에 해당되는 인원들을 등록 취소 합니다.\n"
    retStr += "!양보 [닉네임]              : 내전 대기열 맨 앞에 등록 합니다 닉네임을 입력하지 않으면 본인을 등록합니다.\n"
    retStr += "!새치기 [순번] [닉네임]      : 내전 대기열 순번에 해당되는 자리에 [닉네임]을 등록합니다.\n"
    retStr += "!리셋                     : 내전 대기열을 초기화 시킵니다.\n"
    retStr += "!팀취소 [팀번호]            : 해당팀 로비에 있는 인원을 내전 대기열에서 등록 취소 합니다.\n"
    retStr += "!막판 [팀번호]팀 [막판인원]명 : 오른쪽 상단 내전봇에 막판인원을 등록합니다/\n"

    await ctx.send(retStr)


@bot.command()
async def 경매도움말(ctx):
    retStr ="명령어 목록\n"
    retStr += "매물등록\n"
    retStr += "매물추가\n"
    retStr += "매물제거\n"
    retStr += "다음매물\n"
    retStr += "자동배정\n"
    retStr += "팀장등록\n"
    retStr += "팀장제거\n"
    retStr += "경매현황\n"
    retStr += "팀장마일리지추가\n"
    retStr += "대진표\n"

    await ctx.send(retStr)

@bot.command(aliases=["멘션","ㅁㅅ"])
async def 맨션(ctx, index, *, text=None):
    
    if len(index) > 1 and (index[1] == '~' or index[2] == '~'):
        arr = index.split('~')
        string_int1 = int(arr[0])
        string_int2 = int(arr[1])
        string_int1 -= 1
        string_int2 -= 1
        if (string_int1 < 0 or string_int1 >= len(waitList)) or (string_int2 < 0 or string_int2 >= len(waitList)):
            await ctx.send('잘못된 번호')
            return

        retStr = ""
        while string_int1 <= string_int2:
            waiting = waitList[string_int1]
            for member in ctx.guild.members:
                if member.nick is None:
                    continue

                nickname = member.nick
                arr = nickname.split('/')
                realNick = arr[0]
                if waiting == realNick:
                    retStr += "<@{}> ".format(member.id)

            string_int1 += 1

        if text is not None:
            retStr += text
        await ctx.send(retStr)
        return
    else:
        if len(index) == 1:
            arr = index
        else:
            arr = index.split(',')
            arr.sort(key=int)

        retStr = ""

        for num in arr:
            try:
                string_int = int(num)
                string_int -= 1
                if string_int < 0 or string_int >= len(waitList):
                    await ctx.send('없는 번호')
                    continue
            except ValueError:
                continue

            waiting = waitList[string_int]

            for member in ctx.guild.members:
                if member.nick is None:
                    continue

                nickname = member.nick
                arr = nickname.split('/')
                realNick = arr[0]
                if waiting == realNick:
                    retStr += "<@{}> ".format(member.id)

        if text is not None:
            retStr += text

        await ctx.send(retStr)



@bot.command()
async def 전적(ctx, *, text):
    arr = list()
    try:
        num = int(text)
        if num == 1:
            ch1 = bot.get_channel(944246730722013194)
            ch2 = bot.get_channel(1133763001766391808)
            ch3 = bot.get_channel(890160695499423774)
        elif num == 2:
            ch1 = bot.get_channel(890161063130177536)
            ch2 = bot.get_channel(921018416473718834)
            ch3 = bot.get_channel(921703036294926366)
        elif num == 3:
            ch1 = bot.get_channel(920998312998502451)
            ch2 = bot.get_channel(921018416473718834)
            ch3 = bot.get_channel(921703123221884969)

        for member in ch1.members:
            # if member.voice.self_mute:
            # continue
            nickname = member.nick
            realNick = nickname.split('/')[0]
            arr.append(realNick)

        for member in ch2.members:
            # if member.voice.self_mute:
            # continue
            nickname = member.nick
            realNick = nickname.split('/')[0]
            arr.append(realNick)

        for member in ch3.members:
            # if member.voice.self_mute:
            # continue
            nickname = member.nick
            realNick = nickname.split('/')[0]
            arr.append(realNick)

    except ValueError:
        arr = text.split(',')


    embed = discord.Embed(title="최근 전적", color=discord.Color.blue())
    if len(arr) > 1:
        for name in arr:
            if name == "트롤트롤":
                name = "포롤포롤"

            if name in player_info:
                result = player_statistics_resent10(player_info[name])
                embed.add_field(
                    name=f"\n 최근 {result['result']}전 {result['winCnt']}승 {result['lossCnt']}패 {result['streak']}", value=result['result'], inline=True)
    else:
        name = arr[0]
        if name == "트롤트롤":
            name = "포롤포롤"

        if name in player_info:
            output = player_statistics(player_info[name])
            embed.add_field(name=name, value=output, inline=False)
            result = player_statistics_resent10(player_info[name])
            embed.add_field(name=f"\n 최근 {result['totalMatchCnt']}전 {result['winCnt']}승 {result['lossCnt']}패 {result['streak']}", value=result['result'], inline=True)

    field_count = len(embed.fields)
    if field_count > 0:
        await ctx.send(embed=embed)



bot.run("OTI3NTA1NDYwMzU2MDgzNzUy.YdLMxQ.vxxK7lKSvqQbx_yv_gIj0RGwau0")
