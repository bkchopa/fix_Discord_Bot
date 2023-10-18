import asyncio
import datetime
from datetime import datetime
import discord
from discord.ext import commands
import spreadSheet
from spreadSheet import player_info
from spreadSheet import player_ranking
import common
import pytz

# 한국 시간대를 설정
KST = pytz.timezone('Asia/Seoul')

# 한국 시간대를 기준으로 현재 시간을 구합니다.
current_time = datetime.now(KST)

# 현재 시간을 'YYMM' 형식의 문자열로 변환합니다.
current_yymm = current_time.strftime('%y%m')

class PlayerStatistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def player_statistics(self, player_data, show_total=False, show_position=False):
        # Define positions in the order you want
        positions = ["TOP", "JUG", "MID", "ADC", "SUP"]

        total_games = len(player_data)
        wins = sum(1 for game in player_data if game['result'] == '승')
        losses = total_games - wins
        win_rate = (wins / total_games) * 100 if total_games != 0 else 0

        total_kills = sum(int(game['kill']) if game['kill'] else 0 for game in player_data)
        total_deaths = sum(int(game['death']) if game['death'] else 0 for game in player_data)
        total_assists = sum(int(game['assist']) if game['assist'] else 0 for game in player_data)

        avg_kill = total_kills / total_games if total_games != 0 else 0
        avg_death = total_deaths / total_games if total_games != 0 else 0
        avg_assist = total_assists / total_games if total_games != 0 else 0

        if total_deaths != 0:
            kda = (total_kills + total_assists) / total_deaths
            kda_str = f"{kda:.2f}"
        else:
            kda_str = "Infinite"
        output = ""
        # Print overall statistics
        if show_total:
            output = (f"전적 - {total_games}전 {wins}승/{losses}패 - {win_rate:.2f}% 승률 "
                      f" - KDA: {kda_str}\n")

        # Positional statistics
        if show_position:
            for position in positions:
                position_games = [game for game in player_data if game['position'] == position]
                pos_total_games = len(position_games)
                pos_wins = sum(1 for game in position_games if game['result'] == '승')
                pos_losses = pos_total_games - pos_wins
                pos_win_rate = (pos_wins / pos_total_games) * 100 if pos_total_games != 0 else 0

                pos_total_kills = sum(int(game['kill']) for game in position_games)
                pos_total_deaths = sum(int(game['death']) for game in position_games)
                pos_total_assists = sum(int(game['assist']) for game in position_games)

                pos_avg_kill = pos_total_kills / pos_total_games if pos_total_games != 0 else 0
                pos_avg_death = pos_total_deaths / pos_total_games if pos_total_games != 0 else 0
                pos_avg_assist = pos_total_assists / pos_total_games if pos_total_games != 0 else 0

                pos_kda = (pos_total_kills + pos_total_assists) / pos_total_deaths if pos_total_deaths != 0 else float(
                    'inf')  # 'Infinite' 대신에 float('inf')를 사용

                pos_kda_str = "Infinite" if pos_kda == float('inf') else f"{pos_kda:.2f}"
                if pos_total_games >= 5:
                    if pos_win_rate >= 60:
                        win_rate_symbol = "👍"
                    elif pos_win_rate < 40:
                        win_rate_symbol = "👎"
                    else:
                        win_rate_symbol = " "
                else:
                    win_rate_symbol = ""

                output += (
                    f"\n{win_rate_symbol} {position} - {pos_total_games}전 {pos_wins}승/{pos_losses}패 - {pos_win_rate:.2f}% 승률"
                    f" - KDA: {pos_kda_str}")

        return output

    def player_statistics_recent(self, player_data, recent_count):
        recent_games = player_data[-recent_count:]
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

        results_with_emojis = ""

        for game in recent_games:
            champion = game['champion'].ljust(8)
            emoji = "🔵" if game['result'] == "승" else "🔴"
            result = game['result'].center(2)
            kda = f"{game['kill']}/{game['death']}/{game['assist']}".ljust(9)
            results_with_emojis += f"{emoji} {champion} {kda} \n"

        return {
            "totalMatchCnt": len(recent_games),
            "winCnt": winCnt,
            "lossCnt": lossCnt,
            "streak": streak,
            "resultsWithEmojis": results_with_emojis.strip()
        }

    async def send_game_results(self, ctx, statistics):
        embed = discord.Embed(title="최근 10경기 결과",
                              description=f"전체: {statistics['totalMatchCnt']}전, 승: {statistics['winCnt']}승, 패: {statistics['lossCnt']}패 {statistics['streak']}")

        wins = ""
        losses = ""

        for line in statistics['result'].split("\n"):
            if "승" in line:
                wins += line + "\n"
            elif "패" in line:
                losses += line + "\n"

        if wins:
            embed.add_field(name="승", value=wins, inline=True)
        if losses:
            embed.add_field(name="패", value=losses, inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def 전적(self, ctx, *, text=None):
        if ctx.channel.id != 1154474032310259733:
            await ctx.send("fixgg 채널을 이용해주세요! 메세지는 4초 뒤 삭제됩니다")
            await asyncio.sleep(4)
            await ctx.channel.purge(limit=2)
            return

        arr = list()
        print("전적 검색")
        if text is None:
            arr.clear()
            nickname = ctx.message.author.nick
            arr.append(nickname.split('/')[0].lower())
        else:
            try:
                num = int(text)
                if num == 1:
                    ch1 = ctx.bot.get_channel(944246730722013194)
                    ch2 = ctx.bot.get_channel(1133763001766391808)
                    ch3 = ctx.bot.get_channel(890160695499423774)
                elif num == 2:
                    ch1 = ctx.bot.get_channel(890161063130177536)
                    ch2 = ctx.bot.get_channel(890161039793086465)
                    ch3 = ctx.bot.get_channel(921703036294926366)
                elif num == 3:
                    ch1 = ctx.bot.get_channel(920998312998502451)
                    ch2 = ctx.bot.get_channel(921018416473718834)
                    ch3 = ctx.bot.get_channel(921703123221884969)

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
        print("전적 검색2")
        embed = discord.Embed()
        # embed = discord.Embed(title=f"최근 전적 {spreadSheet.update_date}", color=discord.Color.blue())
        if len(arr) > 1:
            for name in arr:
                name = name.lower()
                if name == "트롤트롤":
                    name = "포롤포롤"

                if name in player_info:
                    result = self.player_statistics_recent(player_info[name], 5)

                    # 모스트3
                    most3_champs = spreadSheet.get_most_champions_for_nickname(name, 5)
                    champ_details = []
                    for champ in most3_champs:
                        champ_name = champ[0]  # 첫 번째 인덱스로 챔피언 이름에 접근
                        winrate = champ[1] * 100  # 두 번째 인덱스로 승률에 접근
                        total_picked = champ[2]  # 세 번째 인덱스로 게임 수에 접근
                        champ_details.append(f"{champ_name}: {total_picked}회, {winrate:.2f}%")
                        champ_text = "\n".join(champ_details)

                    embed.add_field(
                        name=f"{name}\n 최근 {result['totalMatchCnt']}전 {result['winCnt']}승 {result['lossCnt']}패\n {result['streak']}",
                        value=f"{result['resultsWithEmojis']} \nMost Pick\n {champ_text}", inline=True)





        else:
            print("전적 검색3")
            name = arr[0].lower()
            if name == "트롤트롤":
                name = "포롤포롤"

            if name in player_info:
                # 워크시트 선택
                currentMonth = self.player_statistics(spreadSheet.get_monthly_data(name, current_yymm), show_total=True,
                                                 show_position=False)
                total = self.player_statistics(player_info[name], show_total=True, show_position=True)
                total = f"이번 달 {currentMonth}\n통합 {total}"  # 두개를 합쳐!
                if name in player_ranking:
                    score = player_ranking[name]['score']
                    rank = player_ranking[name]['rank']
                    embed.add_field(name=f"{name} {rank}/{score}점", value=total, inline=False)
                else:
                    embed.add_field(name=f"{name}", value=total, inline=False)

                print("전적 검색4")
                # 모스트
                most3_champs = spreadSheet.get_most_champions_for_nickname(name, 10)
                champ_details = []
                for champ in most3_champs:
                    champ_name = champ[0]  # 첫 번째 인덱스로 챔피언 이름에 접근
                    winrate = champ[1] * 100  # 두 번째 인덱스로 승률에 접근
                    total_picked = champ[2]  # 세 번째 인덱스로 게임 수에 접근
                    champ_details.append(f"{champ_name}: {total_picked}회, {winrate:.2f}%")

                champ_text = "\n".join(champ_details)
                embed.add_field(name="Most Pick", value=champ_text, inline=True)
                print("전적 검색5")
                # 10전
                result = self.player_statistics_recent(player_info[name], 10)
                embed.add_field(
                    name=f"\n 최근 {result['totalMatchCnt']}전 {result['winCnt']}승 {result['lossCnt']}패\n {result['streak']}",
                    value=result['resultsWithEmojis'], inline=True)

        print("전적 검색6")
        field_count = len(embed.fields)
        if field_count > 0:
            await ctx.send(embed=embed)

    @commands.command(name='갱신')
    async def 전적갱신(self, ctx):
        if ctx.channel.id != 1154474032310259733:
            await ctx.send("fixgg 채널을 이용해주세요! 메세지는 4초 뒤 삭제됩니다")
            await asyncio.sleep(4)
            await ctx.channel.purge(limit=2)
            return

        try:
            await ctx.send('전적 갱신중.....')
            await spreadSheet.reload()  # reload 함수 호출
            await ctx.send('전적 갱신이 완료되었습니다.')
        except Exception as e:
            await ctx.send(f'오류가 발생했습니다: {str(e)}')


def setup(bot):
    bot.add_cog(PlayerStatistics(bot))