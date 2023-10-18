import discord
from discord.ext import commands, tasks
import random
from collections import defaultdict
import discord
import os

class AuctionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auction = 988117624468680794
        self.currentCount = -1
        self.topbidder = ""
        self.topprice = 0
        self.lastMember = ""
        self.lastBidder = ""
        self.lastPrice = 0
        self.remainMileageDic = dict()
        self.memberListDic = defaultdict(list)
        self.memberList = list()
        self.missedMemberList = list()
        self.currentAuctionMember = str()
        self.start_loop = os.environ.get('AUCTION', 'false').lower() == 'true'

    @commands.Cog.listener()
    async def on_ready(self):
        if self.start_loop:
            self.counter.start()  # 환경 변수가 true인 경우 루프 시작

    @tasks.loop(seconds=1)
    async def counter(self):
        if self.currentAuctionMember == "":
            return

        if self.currentCount < 0:
            return

        ch = self.bot.get_channel(self.auction)
        if self.currentCount == 0:
            if self.topprice == 0:
                self.missedMemberList.append(self.currentAuctionMember)
                await ch.send("유찰되었습니다 ㅜ")
            else:
                retStr = "경매종료:" + self.currentAuctionMember + " 낙찰자 : " + str(self.topbidder) + " 입찰가 : " + str(
                    self.topprice)
                self.memberListDic[self.topbidder].append(self.currentAuctionMember)
                self.remainMileageDic[self.topbidder] -= self.topprice
                await ch.send(retStr)

            self.lastMember = self.currentAuctionMember
            self.lastBidder = self.topbidder
            self.lastPrice = self.topprice
            self.currentAuctionMember = ""
            self.currentCount = -1
            self.topprice = 0
            self.topbidder = 0

            retStr = "현재 남은 매물 : "
            for member in self.memberList:
                retStr += member + " "

            retStr += "\n"

            retStr += "유찰 매물     : "
            for member in self.missedMemberList:
                retStr += member + " "

            retStr += "\n\n\n\n"

            for leader in self.remainMileageDic:
                tempStr = leader
                tempStr += "("
                tempStr += str(self.remainMileageDic[leader])
                tempStr += ") :"
                for name in self.memberListDic[leader]:
                    tempStr += name
                    tempStr += " "
                tempStr += "\n"
                retStr += tempStr

            await ch.send(retStr)
            return

        msg = await ch.send(self.currentCount)
        self.currentCount -= 1

    @commands.command()
    async def 경매시작(self, ctx):
        self.currentCount = 10

    @commands.command()
    async def 입찰(self, ctx, text):
        nickname = ctx.message.author.nick
        arr = nickname.split('/')
        leader = arr[0].replace(" ", "")
        if not leader in self.memberListDic:
            await ctx.send("당신은 팀장이 아닌걸요?")
            return

        if self.currentCount <= 0:
            return

        try:
            price = int(text)
        except ValueError:
            await ctx.send('잘못 된 입력')
            return

        if price <= self.topprice:
            return

        if self.remainMileageDic[leader] < price:
            await ctx.send(leader + "씨 돈이 부족해요")
            return

        if self.topbidder == leader:
            return

        self.currentCount = 10
        self.topprice = price
        self.topbidder = leader
        retStr = "현재 상위 입찰자 : " + str(self.topbidder) + " 입찰가 : " + str(self.topprice)
        await ctx.send(retStr)


    @commands.command()
    async def 매물등록(self, ctx, Participants):
        arr = Participants.split(',')
        if len(arr) == 0:
            return

        for Participant in arr:
            self.memberList.append(Participant)

    @commands.command()
    async def 매물추가(self, ctx, Participant):
        self.memberList.append(Participant)

    @commands.command()
    async def 매물제거(self, ctx, Participant):
        if Participant not in self.memberList:
            return

        self.memberList.remove(Participant)

    @commands.command()
    async def 매물섞기(self, ctx, Participant):
        random.shuffle(self.memberList)

    @commands.command()
    async def 다음매물(self, ctx):
        if len(self.memberList) == 0:
            return

        targetMember = self.memberList[0]
        await ctx.send('다음 매물은 ' + targetMember + '!')
        self.currentAuctionMember = targetMember
        self.memberList.remove(targetMember)

    @commands.command()
    async def 수동매물등록(self, ctx, member):
        if member not in self.memberList:
            return

        await ctx.send('다음 매물은 ' + member + '!')
        self.currentAuctionMember = member
        self.memberList.remove(member)

    @commands.command()
    async def 자동배정(self, ctx, leader, member):
        if not leader in self.memberListDic:
            await ctx.send("팀장을 잘못 적으셨어요")
            return

        if not member in self.memberList:
            await ctx.send("팀원을 잘못 적으셨어요")
            return

        self.memberListDic[leader].append(member)
        self.memberList.remove(member)

    @commands.command()
    async def 팀장등록(self, ctx, leader, mileage):
        try:
            price = int(mileage)
        except ValueError:
            await ctx.send('잘못 된 입력')
            return

        self.remainMileageDic[leader] = int(mileage)
        self.memberListDic[leader] = list()

    # ... 이전에 작성된 코드 ...

    @commands.command()
    async def 팀장제거(self, ctx, leader, mileage):
        if leader not in self.memberListDic:
            await ctx.send("팀장을 잘못 적으셨어요")
            return
        del self.remainMileageDic[leader]
        del self.memberListDic[leader]

    @commands.command()
    async def 팀장마일리지추가(self, ctx, leader, mileage):
        if not leader in self.memberListDic:
            await ctx.send("팀장을 잘못 적으셨어요")
            return

        try:
            price = int(mileage)
        except ValueError:
            await ctx.send('잘못 된 입력')
            return

        self.remainMileageDic[leader] += price

    @commands.command()
    async def 경매현황(self, ctx):
        retStr = "현재 남은 매물 : "
        for member in self.memberList:
            retStr += member + ","

        retStr += "\n\n"

        retStr += "유찰 매물     : "
        for member in self.missedMemberList:
            retStr += member + ","

        retStr += "\n\n\n\n"

        for leader in self.remainMileageDic:
            tempStr = leader
            tempStr += "("
            tempStr += str(self.remainMileageDic[leader])
            tempStr += ") :"
            for name in self.memberListDic[leader]:
                tempStr += name
                tempStr += " "
            tempStr += "\n"
            retStr += tempStr

        await ctx.send(retStr)

    @commands.command()
    async def 팀원제거(self, ctx, leader, member):
        if leader not in self.memberListDic:
            await ctx.send("팀장을 잘못 적으셨어요")
            return

        if member not in self.memberListDic[leader]:
            await ctx.send("그런 팀원 없어요")
            return

        self.memberListDic[leader].remove(member)
        self.memberList.append(member)

    @commands.command()
    async def 팀원추가(self, ctx, leader, member):
        if leader not in self.memberListDic:
            await ctx.send("팀장을 잘못 적으셨어요")
            return

        if member not in self.memberList:
            await ctx.send("그런 매물 없어요")
            return

        self.memberListDic[leader].append(member)
        self.memberList.remove(member)

    @commands.command()
    async def 유찰복구(self, ctx):
        self.memberList = self.missedMemberList.copy()
        self.missedMemberList.clear()

    @commands.command()
    async def 되돌리기(self, ctx):
        if self.lastMember == "":
            return

        if self.lastBidder == "":
            return

        if self.lastMember not in self.memberListDic[self.lastBidder]:
            await ctx.send("잘못 된 입력")
            return

        try:
            int(self.lastPrice)
        except ValueError:
            await ctx.send('잘못 된 입력')
            return

        self.memberListDic[self.lastBidder].remove(self.lastMember)
        self.memberList.append(self.lastMember)
        self.remainMileageDic[self.lastBidder] += int(self.lastPrice)
        self.lastMember = ""
        self.lastBidder = ""
        self.lastPrice = 0

    @commands.command()
    async def 대진표(self, ctx):
        teamList = list()
        for leader in self.memberListDic:
            teamList.append(leader)

        if len(teamList) == 0:
            return

        if len(teamList) % 2 != 0:
            return

        retStr = ""
        while len(teamList) != 0:

            team1 = random.choice(teamList)
            team2 = random.choice(teamList)
            if team1 == team2:
                continue

            retStr = team1 + " 팀 vs" + team2 + " 팀\n"
            teamList.remove(team1)
            teamList.remove(team2)

            await ctx.send(retStr)
            retStr = ""

    @commands.command()
    async def 경매종료(self, ctx):
        self.currentAuctionMember = ""
        self.currentCount = -1

    @commands.command()
    async def 경매리셋(self, ctx):
        self.topbidder = ""
        self.topprice = 0
        self.lastMember = ""
        self.lastBidder = ""
        self.lastPrice = 0

        self.remainMileageDic.clear()
        self.memberListDic.clear()
        self.memberList.clear()
        self.missedMemberList.clear()
        self.currentAuctionMember = ""
