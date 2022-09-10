import discord
from discord.ext import commands, tasks
import datetime
import random
import asyncio

bot = commands.Bot(command_prefix='!')
waitList = list()
team1 = "890160695499423774"
team2 = "921703036294926366"
team3 = "921703123221884969"
test = "927502689913430057"
auction = 988117624468680794
currentCount = -1
topbidder = ""
topprice = 0



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
    await ch.send("내전 봇 재시작(약 24시간마다 자동재시작)")
    resetList.start()
    #counter.start()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("내전 명단관리 열심히"))


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
async def 양보(ctx, text):
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
async def 취소(ctx, text=None):
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

    nickname = ctx.message.author.nick
    arr = nickname.split('/')
    realnick = arr[0]
    if topbidder == realnick:
        return

    topprice = price
    topbidder = realnick
    retStr = "현재 상위 입찰자 : " + str(topbidder) +" 입찰가 : " + str(topprice)
    await ctx.send(retStr)
    currentCount = 10



@tasks.loop(seconds=1)
async def counter():
    global currentCount

    if currentCount < 0:
        return

    ch = bot.get_channel(auction)
    if currentCount == 0:
        global topprice
        global topbidder
        if topprice == 0:
            await ch.send("유찰되었습니다 ㅜ")
        else:
            retStr = "경매종료 낙찰자 : " + str(topbidder) +" 입찰가 : " + str(topprice)
            await ch.send(retStr)

        currentCount -= 1
        topprice = 0
        topbidder = 0
        return

    msg = await ch.send(currentCount)
    currentCount-=1


bot.run("OTI3NTA1NDYwMzU2MDgzNzUy.YdLMxQ.vxxK7lKSvqQbx_yv_gIj0RGwau0")
