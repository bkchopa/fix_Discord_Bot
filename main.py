import discord
from discord.ext import commands, tasks
import datetime
import random

bot = commands.Bot(command_prefix='!')
waitList = list()
team1 = "890160695499423774"
team2 = "921703036294926366"
team3 = "921703123221884969"
teamlist = [0, 890160695499423774, 921703036294926366, 921703123221884969]
test = "927502689913430057"

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


@bot.event
async def on_ready():
    print(f"봇={bot.user.name}로 연결중")
    print('연결이 완료되었습니다.')
    ch = bot.get_channel(890160605246414848)

    resetList.start()
    autoCancel.start()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("내전 명단관리 열심히"))


@bot.command(aliases=["check", "췤", "첵", "쳌", "채크"])
async def 체크(ctx, *, text=None):
    print('체크 :')
    if text is None:
        nickname = ctx.message.author.nick
        arr = nickname.split('/')
        if arr[0] not in waitList:
            print(arr[0])
            waitList.append(arr[0])
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
    print('양보 :')
    print(text)
    if text in waitList:
        waitList.remove(text)

    waitList.insert(0, text)


@bot.command(aliases=["취"])
async def 취소(ctx, text=None):
    if text is None:
        nickname = ctx.message.author.nick
        arr = nickname.split('/')
        if arr[0] in waitList:
            waitList.remove(arr[0])
            print('취소 :')
            print(arr[0])
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


@bot.command()
async def 대기(ctx, text=None):
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

@bot.command(aliases=["팀취"])
async def 팀취소(ctx, teamNum):
    try:
        num = int(teamNum)
    except ValueError:
        await ctx.send('잘못 된 입력')
        return

    if num >= len(teamlist) or num <= 0:
        return

    ch = bot.get_channel(teamlist[num])

    for member in ch.members:
        if member.voice.self_mute:
            continue
        nickname = member.nick
        realNick = nickname.split('/')[0]

        if realNick in waitList:
            waitList.remove(realNick)

    await printlist(ctx)

@bot.command()
async def 팀뽑(ctx, teamNum):
    try:
        num = int(teamNum)
    except ValueError:
        await ctx.send('잘못 된 입력')
        return

    if num >= len(teamlist) or num <= 0:
        return

    ch = bot.get_channel(teamlist[num])

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
    waitList.clear()


@tasks.loop(hours=1)
async def resetList():
    print('명단리셋.')
    hour = datetime.datetime.now().hour
    if hour is 22:
        ch = bot.get_channel(890160605246414848)
        await ch.send("명단  리셋합니다!")
        waitList.clear()

@tasks.loop(seconds=10)
async def autoCancel():
    print('자동취소.')
    for i in range(1, len(teamlist)):
        ch = bot.get_channel(teamlist[i])
        if len(ch.members) == 0:
            return

        for member in ch.members:
            if member.voice.self_mute:
                continue
            nickname = member.nick
            realNick = nickname.split('/')[0]

            if realNick in waitList:
                waitList.remove(realNick)




        
bot.run("OTI3NTA1NDYwMzU2MDgzNzUy.YdLMxQ.vxxK7lKSvqQbx_yv_gIj0RGwau0")
