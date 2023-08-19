import asyncio
import io
import discord
from discord.ext import commands
from app import common
from app.common import add_experience
from app.quest import QuestBoard, QuestCard
import random
from datetime import datetime


def get_daily_quest():
    guild_id = common.oasis_guild_id
    types = common.database.get([("guildID", guild_id), ("questType", '')], dbTable="memory")[0][0]
    reqs = common.database.get([("guildID", guild_id), ("questReq", '')], dbTable="memory")[0][0]
    return types.split(','), [float(x) for x in reqs.split(',')]


async def parse_quest_progress(member_id, q_type, q_val):
    quest_data = get_daily_quest()
    if q_type in quest_data[0]:
        idx = quest_data[0].index(q_type)
        fin = common.database.get([("memberID", member_id), ("questFin", '')], dbTable="game")[0][0].split(',')
        fin = [int(x) for x in fin]
        # for speed
        if not fin[idx]:
            prog = common.database.get([("memberID", member_id), ("questProg", '')], dbTable="game")[0][0].split(',')
            # if it is the correct index and does not go below 0
            dummy = []
            for i, x in enumerate(prog):
                val = common.rnd(float(x) + q_val)
                if (i == idx) and (val > 0):
                    dummy.append(str(val))
                else:
                    dummy.append(x)
            prog = dummy
            common.database.update([("memberID", member_id), ("questProg", ','.join(prog))], dbTable="game")

            # check if finished then update
            if float(prog[idx]) >= quest_data[1][idx]:
                dummy = []
                for i, x in enumerate(fin):
                    if i == idx:
                        dummy.append(str(1))
                        xp = common.quest_xp
                        if i == 0:
                            xp >>= 1
                        elif i == 2:
                            xp <<= 1
                        await add_experience(xp, member_id)
                    else:
                        dummy.append(str(x))
                fin = dummy
                common.database.update([("memberID", member_id), ("questFin", ','.join(fin))], dbTable="game")


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quest = QuestCard(common.quest_xp)

    async def update_daily_quest(self):
        # default_format = "%m-%d-%Y %H:%M:%S"
        # dt = datetime.strptime("07-25-2023 08:00:00", "%m-%d-%Y %H:%M:%S")
        # utc = timestamp
        guild_id = common.oasis_guild_id
        quest_utc = common.database.get([("guildID", guild_id), ("questTimestamp", '')], dbTable="memory")[0][0]
        quest_date = datetime.fromtimestamp(quest_utc)
        now = datetime.now()
        if (now - quest_date).days:
            data = common.quest_defaults
            quest = []
            for diff in range(3):
                chosen = random.choice(data)
                data.remove(chosen)
                req = chosen[1]
                if diff == 0:
                    req = chosen[1] >> 1
                elif diff == 3:
                    req = chosen[1] << 1
                quest.append((chosen[0], req))

            q_types = []
            q_reqs = []
            for q_type, q_req in quest:
                q_types.append(q_type)
                q_reqs.append(str(q_req))
            common.database.update([("guildID", guild_id), ("questType", ','.join(q_types))], dbTable="memory")
            common.database.update([("guildID", guild_id), ("questReq", ','.join(q_reqs))], dbTable="memory")
            # testing timestamp = 1686758400
            common.database.update([("guildID", guild_id), ("questTimestamp", quest_utc + 86400.)], dbTable="memory")
            await self.questboard()

            # resetting all member progress
            for member_id in common.database.get_ids():
                common.database.update([("memberID", member_id), ("questProg", "0.,0.,0.")], dbTable="game")
                common.database.update([("memberID", member_id), ("questFin", "0,0,0")], dbTable="game")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Updating daily quests...")
        while True:
            await self.update_daily_quest()
            await asyncio.sleep(180)

    async def questboard(self, guild_id=common.oasis_guild_id):
        questboard_channel = await self.bot.fetch_channel(common.questboard_channel_id)
        message_id = common.database.get([('guildID', guild_id), ("questboardMessageID", '')],
                                         dbTable="memory")[0][0]
        orig_message = await questboard_channel.fetch_message(message_id)
        board = QuestBoard()
        board.draw_quests(get_daily_quest(), common.quest_xp)
        card = io.BytesIO()
        board.canvas.save(card, "PNG")
        card.seek(0)
        message = await questboard_channel.send(file=discord.File(fp=card, filename="quest.png"))
        await orig_message.delete()
        common.database.update([('guildID', guild_id), ('questboardMessageID', message.id)], dbTable="memory")

    @commands.command(name="spawn_questboard", aliases=["sq"])
    async def spawn_questboard(self, ctx):
        if ctx.author.id in common.the_council_id:
            questboard_channel = await self.bot.fetch_channel(common.questboard_channel_id)
            board = QuestBoard()
            board.draw_quests(get_daily_quest(), common.quest_xp)
            card = io.BytesIO()
            board.canvas.save(card, "PNG")
            card.seek(0)
            message = await questboard_channel.send(file=discord.File(fp=card, filename="quest.png"))
            common.database.update([('guildID', ctx.guild.id), ('questboardMessageID', message.id)], dbTable="memory")

    @commands.command(name="quest", aliases=['q'])
    async def quest_prog(self, ctx, memberNameID=None):
        if not memberNameID:
            id = ctx.author.id
        else:
            id = common.get_member(self.bot, memberNameID).id
        q_types, q_reqs = get_daily_quest()
        q_prog = common.database.get([("memberID", id), ("questProg", '')], dbTable="game")[0][0].split(',')
        q_fin = common.database.get([("memberID", id), ("questFin", '')], dbTable="game")[0][0].split(',')
        data = [(float(p), float(r), t, int(f)) for p, r, t, f, in zip(q_prog, q_reqs, q_types, q_fin)]
        self.quest.draw_quests(data)
        card = io.BytesIO()
        self.quest.canvas.save(card, "PNG")
        card.seek(0)
        await ctx.send(file=discord.File(fp=card, filename=f"{ctx.author.name} quest progress.png"))
        self.quest = QuestCard(common.quest_xp)

    @commands.command(name="test")
    async def test(self, ctx):
        member = common.get_member(self.bot, ctx.author.id)
        print(member)
        print(member.voice.self_stream)


def setup(bot):
    bot.add_cog(Game(bot))
