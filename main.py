import discord
from discord.ext import commands, tasks
import datetime
import random
import asyncio
from collections import defaultdict


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

async def printlist(ctx: discord.ext.commands.context.Context):
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


    await ch.send("내전 봇 재시작(약 24시간마다 자동재시작)")
    #resetList.start()
    counter.start()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("내전 명단관리 열심히"))

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



@bot.command(aliases=["check", "췤", "첵", "쳌", "채크", "ㅊㅋ","cz"])
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

@bot.command(aliases=["취","ㅊㅅ","ct"])
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


@bot.command(aliases=["ㄷㄱ","er"])
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


@bot.command(aliases=["팀취"])
async def 팀취소(ctx, teamNum):
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


@bot.command()
async def 리셋(ctx):
    if ctx.channel.id != 890160605246414848:
        await not_here(ctx)
        return
    waitList.clear()
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
            await changetitle(ctx)
            return

        if end == -1:
            end = len(text) + 1

        nickName = text[start + 3:end - 1]
        waitList.append(nickName)
        i += 1






@tasks.loop(hours=1)
async def resetList():
    hour = datetime.datetime.now().hour
    if hour is 22:
        ch = bot.get_channel(890160605246414848)
        await ch.send("명단  리셋합니다!")
        waitList.clear()


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
async def 다음매물(ctx):
    if len(memberList) == 0:
        return

    targetMember = random.choice(memberList)
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
    
    if len(index) > 1 and index[1] == '~':
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

        retStr += text

        await ctx.send(retStr)


bot.run("OTI3NTA1NDYwMzU2MDgzNzUy.YdLMxQ.vxxK7lKSvqQbx_yv_gIj0RGwau0")
