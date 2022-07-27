import discord
import io
import asyncio
from discord.ext import commands
from discord.ui import Button
from PIL import Image
from datetime import datetime
from src.app import common
from src.app.level_card import LevelCard
from src.app.leaderboard import Leaderboard
from src.app.common import number_readability as nr
from math import ceil, exp


def next_level(level):
    return 123. * level * level * level


async def add_message_count(member_id):
    messages = common.database.get([("memberID", member_id), ("messages", '')], dbTable="leveling")[0][0]
    common.database.update([("memberID", member_id), ("messages", messages + 1)], dbTable="leveling")


async def add_voice_minutes(member_id, voice_minutes):
    old_voice_minutes = common.database.get([("memberID", member_id), ("voiceMinutes", '')], dbTable="leveling")[0][0]
    common.database.update(
        [("memberID", member_id), ("voiceMinutes", common.round_off(old_voice_minutes + voice_minutes))],
        dbTable="leveling")


async def add_passive_hours(member_id, passive_hours):
    inServer = common.database.get([("memberID", member_id), ("inServer", '')])[0][0]
    if inServer:
        old_passive_hours = common.database.get([("memberID", member_id), ("passiveHours", '')], dbTable="leveling")[0][
            0]
        common.database.update(
            [("memberID", member_id), ("passiveHours", common.round_off(old_passive_hours + passive_hours))],
            dbTable="leveling")


async def add_reaction_count(member_id):
    reactions = common.database.get([("memberID", member_id), ("reactions", '')], dbTable="leveling")[0][0]
    common.database.update([("memberID", member_id), ("reactions", reactions + 1)], dbTable="leveling")


async def remove_reaction_count(member_id):
    reactions = common.database.get([("memberID", member_id), ("reactions", '')], dbTable="leveling")[0][0]
    common.database.update([("memberID", member_id), ("reactions", reactions - 1)], dbTable="leveling")


async def add_experience(xp, member_id, timestamp_update=None, in_server=True):
    if in_server:
        xp = common.round_off(xp)
        old_experience = common.database.get([("memberID", member_id), ("experience", '')], dbTable='leveling')[0][0]
        common.database.update([("memberID", member_id), ("experience", xp + old_experience)], dbTable='leveling')
    if timestamp_update:
        common.database.update([("memberID", member_id), ("timestampLastUpdate", timestamp_update)], dbTable='leveling')


async def remove_experience(xp, member_id, timestamp_update=None, in_server=True):
    if in_server:
        xp = common.round_off(xp)
        old_experience = common.database.get([("memberID", member_id), ("experience", '')], dbTable='leveling')[0][0]
        common.database.update([("memberID", member_id), ("experience", old_experience - xp)], dbTable='leveling')
    if timestamp_update:
        common.database.update([("memberID", member_id), ("timestampLastUpdate", timestamp_update)], dbTable='leveling')


async def update_passive_xp(member_id):
    in_server = common.database.get([("memberID", member_id), ("inServer", '')])[0][0]
    if in_server:
        ts = common.database.get([("memberID", member_id), ("timestampLastUpdate", '')], dbTable="leveling")[0][0]
        if ts > 0:
            dt = common.timestamp_convert(ts)
        else:
            dt = common.timestamp_convert(common.database.get([("memberID", member_id), ("timestampJoined", "")])[0][0])
        now = datetime.now()
        passive_hours = common.time_delta_to_hours(now - dt)
        xp = passive_hours * common.passive_xp
        await add_experience(xp, member_id, timestamp_update=common.timestamp_convert(now))
        await add_passive_hours(member_id, passive_hours)


async def update_voice(member_id):
    xp_mult = common.database.get([("memberID", member_id), ("xpMult", '')], dbTable="leveling")[0][0]
    if xp_mult:
        # update last voice timestamp and add xp and stats
        dt_last_voice = common.timestamp_convert(
            common.database.get([("memberID", member_id), ("timestampLastVoice", '')], dbTable="leveling")[0][0])
        now = datetime.now()
        common.database.update([("memberID", member_id), ("timestampLastVoice", now.timestamp())],
                               dbTable="leveling")
        minutes = common.time_delta_to_minutes(now - dt_last_voice)
        xp_gain = common.voice_xp * minutes * xp_mult
        await add_experience(xp_gain, member_id)
        await add_voice_minutes(member_id, minutes)


class View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activeIDs = set()
        self.creatingLeaderboard = False
        self.update = True

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.guild.id == common.oasis_guild_id and not message.author.bot:
                if message.content.startswith(common.bot_prefixes):
                    await add_message_count(message.author.id)
                    await add_experience(common.bot_message_xp, message.author.id)
                else:
                    await add_message_count(message.author.id)
                    await add_experience(common.normal_message_xp, message.author.id)
                await self.update_level(message.author.id)
        except AttributeError:
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.member.bot and payload.guild_id == common.oasis_guild_id:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if not message.author.bot:
                member_id = message.author.id
                await add_reaction_count(member_id)
                await add_experience(common.reaction_xp, member_id)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        member = common.get_member(self.bot, payload.user_id)
        if not member.bot and payload.guild_id == common.oasis_guild_id:
            channel = await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if not message.author.bot:
                member_id = message.author.id
                await remove_reaction_count(member_id)
                await remove_experience(common.reaction_xp, member_id)

    async def xp_mult_update(self, val, member_id):
        # 1 case joined member is the 1st member
        # 2 case joined member is the one who fifth man
        # 3 case joined member is the sixth man
        xp_m = common.database.get([("memberID", member_id), ("xpMult", '')], dbTable="leveling")[0][0]
        if xp_m > 0:
            await update_voice(member_id)
        else:
            common.database.update([("memberID", member_id), ("timestampLastVoice", common.timestamp_convert(
                datetime.now()))], dbTable="leveling")
        common.database.update([("memberID", member_id), ("xpMult", val)], dbTable="leveling")

        if val > 0:
            self.activeIDs.add(member_id)
            if len(self.activeIDs) >= common.num_active_double:
                for memberID in self.activeIDs:
                    await update_voice(memberID)
                    common.database.update([("memberID", memberID), ("xpMult", 2.)], dbTable="leveling")
        else:
            self.activeIDs.remove(member_id)
            if len(self.activeIDs) < common.num_active_double:
                for memberID in self.activeIDs.copy():
                    xp_m = common.database.get([("memberID", memberID), ("xpMult", '')], dbTable="leveling")[0][0]
                    if xp_m > 0:
                        await update_voice(memberID)
                    else:
                        common.database.update(
                            [("memberID", memberID), ("timestampLastVoice", common.timestamp_convert(
                                datetime.now()))], dbTable="leveling")
                    voice = common.get_member(self.bot, memberID).voice
                    if not voice or not voice.channel or voice.deaf or voice.self_deaf or voice.afk:
                        xp = 0.
                        self.activeIDs.remove(memberID)
                    elif voice.mute or voice.self_mute:
                        xp = .5
                    else:
                        xp = 1.
                    common.database.update([("memberID", memberID), ("xpMult", xp)], dbTable="leveling")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and (member.guild.id == common.oasis_guild_id):
            before_mute = before.mute or before.self_mute
            before_deaf = before.deaf or before.self_deaf
            after_mute = after.mute or after.self_mute
            after_deaf = after.deaf or after.self_deaf

            join = (not before.channel) and after.channel
            leave = before.channel and (not after.channel)
            muted = (not before_mute) and after_mute
            unmute = before_mute and (not after_mute)
            deafened = (not before_deaf) and after_deaf
            undeafen = before_deaf and (not after_deaf)
            afk = (not before.afk) and after.afk
            unafk = before.afk and (not after.afk)

            """
            Notes:
            check if update_voice is properly placed
            ensure that parameters inside a function that is inside a function are properly labeled
            """
            if leave or after.afk or after_deaf:
                await self.xp_mult_update(0., member.id)
            elif muted or (join and after_mute) or (undeafen and after_mute) or (unafk and after_mute):
                await self.xp_mult_update(.5, member.id)
            elif join or unmute or (unafk and not after_mute):
                await self.xp_mult_update(1., member.id)

    @commands.Cog.listener()
    async def on_ready(self):
        for memberID in common.database.get_actives():
            common.database.update([("memberID", memberID), ("xpMult", 0)], dbTable="leveling")
        guild = self.bot.get_guild(common.oasis_guild_id)
        for voice_channel in guild.voice_channels:
            for member in voice_channel.members:
                if not member.bot:
                    voice = member.voice
                    if voice.channel and (not voice.deaf or not voice.self_deaf or not voice.afk):
                        await self.xp_mult_update(1., member.id)
                    elif voice.channel and (voice.mute or voice.self_mute):
                        await self.xp_mult_update(.5, member.id)
        while self.update:
            for memberID in common.database.get_ids():
                await update_passive_xp(memberID)
                await update_voice(memberID)
                await self.update_level(memberID)
            await asyncio.sleep(common.minutes_to_seconds(2))

    async def update_level(self, member_id):
        level = common.database.get([("memberID", member_id), ("level", '')], dbTable="leveling")[0][0]
        experience = common.database.get([("memberID", member_id), ("experience", '')], dbTable="leveling")[0][0]
        old_level = level
        while experience > next_level(level + 1):
            level += 1
        if old_level != level:
            common.database.update([("memberID", member_id), ("level", level)], dbTable="leveling")
            if (level < 4) or (level % ceil((5.01443 * (exp(-0.0350659 * level)))) == 0):
                general_channel = await self.bot.fetch_channel(common.general_channel_id)
                member = common.get_member(self.bot, member_id)
                if level <= 50:
                    await general_channel.send(f"Good job {member.name}:confetti_ball:, you progressed to level "
                                               f"{level}!:arrow_double_up:")
                else:
                    await general_channel.send(f"Good job @{member.id}:confetti_ball:, you progressed to level "
                                               f"{level}!:arrow_double_up:")

    @commands.command(name="level", alias=['l'])
    async def level(self, ctx, memberIDName=None):
        if memberIDName:
            author = common.get_member(self.bot, memberIDName)
        else:
            author = ctx.author

        if not author:
            await ctx.send(f"{memberIDName} not found!")
        else:
            await self.update_level(author.id)
            avatar = await author.display_avatar.read()
            thumbnail = Image.open(io.BytesIO(avatar))
            currentXP, rank, level = 0, 0, 0
            for stats in common.database.get_stats():
                if stats[-1] == author.id:
                    currentXP = stats[-3]
                    level = stats[-2]
                    rank = stats[0]
                    break
            neededXP = next_level(level + 1) - next_level(level)
            currentXP = currentXP - next_level(level)
            level_card = LevelCard(author.name, author.discriminator, nr(currentXP), nr(neededXP),
                                   currentXP / neededXP, rank, level, author.status, thumbnail)
            card = io.BytesIO()
            level_card.canvas.save(card, "PNG")
            card.seek(0)
            await ctx.send(file=discord.File(fp=card, filename=f"{author.name}.png"))

    async def leaderboard(self, page):
        # Rank, Username, voiceMinutes, messages, reactions, passiveHours, experience, level, memberID
        # 0,    1,        2,            3,        4,         5,            6,          7,     8
        row_data = []
        for stats in common.database.get_stats()[page * 10:page * 10 + 10]:
            avatar = await common.get_member(self.bot, stats[-1]).display_avatar.read()
            thumbnail = Image.open(io.BytesIO(avatar))
            level = stats[7]
            xp = stats[6]
            needed_xp = next_level(level + 1) - next_level(level)
            current_xp = xp - next_level(level)
            row = (stats[0] - 1, thumbnail, stats[1], nr(stats[2]), nr(stats[3]), nr(stats[4]), nr(stats[5]),
                   nr(xp), nr(level), current_xp / needed_xp)
            row_data.append(row)
        card = io.BytesIO()
        Leaderboard(row_data).canvas.save(card, "PNG")
        card.seek(0)
        return card

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if not self.creatingLeaderboard:
            self.creatingLeaderboard = True
            lbMessageID = common.database.get([('guildID', interaction.guild.id), ("leaderboardMessageID", '')],
                                              dbTable="memory")[0][0]
            if interaction.message.id == lbMessageID and interaction.custom_id.startswith("leader"):
                await interaction.response.send_message(content="Please wait...", ephemeral=True, delete_after=5)
                page = int(interaction.message.attachments[0].filename[0])
                total_count = common.database.get_count()
                if (total_count % 10) == 0:
                    last_page = (total_count // 10) - 1
                else:
                    last_page = total_count // 10
                control = int(interaction.custom_id[-1])
                control_values = (-last_page, -2, -1, 0, 1, 2, last_page)
                new_page = page + control_values[control]
                if new_page < 0:
                    new_page = 0
                elif new_page > last_page:
                    new_page = last_page
                card = await self.leaderboard(new_page)
                view = await self.create_view(new_page)
                message = await interaction.channel.send(file=discord.File(fp=card, filename=f"{new_page}.png"),
                                                         view=view)
                await interaction.message.delete()
                common.database.update([("guildID", interaction.guild.id), ("leaderboardMessageID", message.id)],
                                       dbTable="memory")
            self.creatingLeaderboard = False

    @commands.command(name="spawn_leaderboard", aliases=["sl"])
    async def spawn_leaderboard(self, ctx):
        if ctx.author.id in common.the_council_id:
            leaderboards_channel = await self.bot.fetch_channel(common.leaderboards_channel_id)
            card = await self.leaderboard(0)
            view = await self.create_view(0)
            message = await leaderboards_channel.send(file=discord.File(fp=card, filename="0.png"), view=view)
            common.database.update([('guildID', ctx.guild.id), ("leaderboardMessageID", message.id)], dbTable="memory")

    async def create_view(self, page):
        total_count = common.database.get_count()
        if (total_count % 10) == 0:
            last_page = (total_count // 10) - 1
        else:
            last_page = total_count // 10

        if page == 0:
            buttons = [Button(emoji=label, custom_id=f"leader{i + 3}") for
                       i, label in enumerate(common.leaderboard_controls[3:])]
        elif page == last_page:
            buttons = [Button(emoji=label, custom_id=f"leader{i}") for
                       i, label in enumerate(common.leaderboard_controls[:4])]
        else:
            buttons = [Button(emoji=label, custom_id=f"leader{i + 1}") for
                       i, label in enumerate(common.leaderboard_controls[1:-1])]
        view = View()
        view.clear_items()
        for button in buttons:
            button.callback = self.on_interaction
            view.add_item(button)
        return view

    @commands.command(name="active", aliases=["act"])
    async def active(self, ctx):
        if not len(self.activeIDs) and not len(common.database.get_actives()):
            await ctx.send(f"No member is active")
        else:
            for memberID in common.database.get_actives():
                member = common.get_member(self.bot, memberID)
                xp = common.database.get([("memberID", memberID), ("xpMult", '')], dbTable="leveling")[0][0]
                await ctx.send(f"{member.name} -> {xp}x")

    @commands.command(name="toggle_update", alias=['tu'])
    async def toggle_update(self, ctx):
        if ctx.author.id in common.the_council_id:
            if self.update:
                self.update = False
            else:
                self.update = True

    @commands.command(name="test", alias=['t'])
    async def test(self, ctx):
        print("hello there")
        # message_id = common.database.get([("guildID", common.oasis_guild_id), ("leaderboardMessageID", '')],
        #                                  dbTable="memory")[0][0]
        # message = await self.bot.get_channel(common.leaderboards_channel_id).fetch_message(message_id)
        # print(message.components[0].children)
        # for child in message.components[0].children:
        #     child.disabled = True
        # print("sleeping")
        # await asyncio.sleep(10)
        # for child in message.components[0].children:
        #     child.disabled = False


def setup(bot):
    bot.add_cog(Leveling(bot))
