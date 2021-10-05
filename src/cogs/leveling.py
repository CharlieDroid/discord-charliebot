import sys

sys.path.insert(0, r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0")
import common
import asyncio
import io
import discord
from PIL import Image
from level_card import LevelCard
from datetime import datetime
from discord.ext import commands
from leaderboard import Leaderboard
from common import number_readability as nr


def next_level(level):
    return 33.8 * level * level * level


def nor(a, b):
    if (a == 0) and (b == 0):
        return 1
    elif (a == 0) and (b == 1):
        return 0
    elif (a == 1) and (b == 0):
        return 0
    elif (a == 1) and (b == 1):
        return 0


async def add_message_count(author_id):
    try:
        messages = common.database.get([("memberID", author_id), ("messages", '')], dbTable="leveling")[0][0]
        common.database.update([("memberID", author_id), ("messages", messages + 1)], dbTable="leveling")
    except IndexError:
        pass


async def add_voice_minutes(author_id, voice_minutes):
    old_voice_minutes = common.database.get([("memberID", author_id), ("voiceMinutes", '')], dbTable="leveling")[0][0]
    common.database.update(
        [("memberID", author_id), ("voiceMinutes", common.round_off(old_voice_minutes + voice_minutes))],
        dbTable="leveling")


async def add_passive_hours(author_id, passive_hours):
    inServer = common.database.get([("memberID", author_id), ("inServer", '')])[0][0]
    if inServer:
        old_passive_hours = common.database.get([("memberID", author_id), ("passiveHours", '')], dbTable="leveling")[0][
            0]
        common.database.update(
            [("memberID", author_id), ("passiveHours", common.round_off(old_passive_hours + passive_hours))],
            dbTable="leveling")


async def add_experience(xp, author_id, timestampUpdated=None):
    xp = common.round_off(xp)
    old_experience = common.database.get([("memberID", author_id), ("experience", "")],
                                         dbTable='leveling')[0][0]
    experience = xp + old_experience
    common.database.update([("memberID", author_id), ("experience", experience)], dbTable='leveling')
    common.database.update([("memberID", author_id), ("previousExperience", old_experience)],
                           dbTable="leveling")
    if timestampUpdated:
        common.database.update([("memberID", author_id), ("timestampLastUpdate", timestampUpdated)], dbTable='leveling')


async def update_passive_xp():
    memberID_list = common.database.get([('', ''), ("memberID", '')])
    for member_tuple in memberID_list:
        memberID = member_tuple[0]
        timestampLastUpdate = common.database.get(
            [("memberID", memberID), ("timestampLastUpdate", "")],
            dbTable="leveling")[0][0]
        now = datetime.now()

        async def update_xp_and_timestamp_updated(memberID, now, datetimeUpdate):
            deltaTime = now - datetimeUpdate
            passiveHours = common.time_delta_to_hours(deltaTime)
            xp = passiveHours * common.passive_xp
            await add_experience(xp, memberID, timestampUpdated=common.timestamp_convert(now))
            await add_passive_hours(memberID, passiveHours)

        if timestampLastUpdate != 0:
            datetimeLastUpdate = common.timestamp_convert(timestampLastUpdate)
            await update_xp_and_timestamp_updated(memberID, now, datetimeLastUpdate)
        else:
            datetimeJoined = common.timestamp_convert(common.database.get(
                [("memberID", memberID), ("timestampJoined", "")])[0][0])
            await update_xp_and_timestamp_updated(memberID, now, datetimeJoined)


async def update_voice_xp(author_id=None):
    async def add_voice_xp(author_id):
        addXPVoice = common.database.get([("memberID", author_id), ("addXPVoice", '')], dbTable="leveling")[0][0]
        if addXPVoice:
            now = datetime.now()
            datetimeLastVoice = common.timestamp_convert(
                common.database.get([("memberID", author_id), ("timestampLastVoice", "")],
                                    dbTable="leveling")[0][0])
            common.database.update([("memberID", author_id), ("timestampLastVoice", common.timestamp_convert(now))],
                                   dbTable="leveling")
            voiceMinutes = common.time_delta_to_minutes(now - datetimeLastVoice)
            xp = voiceMinutes * common.voice_xp
            await add_experience(xp, author_id)
            await add_voice_minutes(author_id, voiceMinutes)

    if author_id:
        await add_voice_xp(author_id)
    else:
        memberID_list = common.database.get([('', ''), ("memberID", '')])
        for member_tuple in memberID_list:
            memberID = member_tuple[0]
            await add_voice_xp(memberID)


async def check_add_xp():
    memberIDList = common.database.get([('', ''), ("memberID", '')])
    addXPMemberID = []
    for member_tuple in memberIDList:
        memberID = member_tuple[0]
        add_xp = common.database.get([("memberID", memberID), ("addXPVoice", '')], dbTable="leveling")[0][0]
        if add_xp:
            addXPMemberID.append(memberID)
    return addXPMemberID


class Leveling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
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
            avatar = await author.avatar_url_as(format="png", static_format="png").read()
            thumbnail = Image.open(io.BytesIO(avatar))
            author_id = author.id
            rank_memberID_experience_list = common.database.get_rank()
            currentXP, rank = 0, 0
            for rank_memberID_experience in rank_memberID_experience_list:
                if rank_memberID_experience[1] == author_id:
                    currentXP = rank_memberID_experience[2]
                    rank = rank_memberID_experience[0]
            level = common.database.get([("memberID", author_id), ("level", '')], dbTable="leveling")[0][0]
            neededXP = next_level(level + 1) - next_level(level)
            currentXP = currentXP - next_level(level)
            status = author.status
            statusDict = {discord.Status.online: "online",
                          discord.Status.idle: "idle",
                          discord.Status.dnd: "dnd"}
            try:
                status = statusDict[status]
            except KeyError:
                status = "unknown"
            level_card = LevelCard("", author.name, author.discriminator,
                                   currentXP, neededXP, rank, level, status, thumbnail)
            card = io.BytesIO()
            level_card.canvas.save(card, "PNG")
            card.seek(0)
            await ctx.send(file=discord.File(fp=card, filename=f"{author.name}.png"))

    async def leaderboard(self, page):
        page = int(page)
        if page < 0:
            page = 0
        stats_list = common.database.get_stats()[page * 10:page * 10 + 10]
        if stats_list:
            rowData = []
            for stats in stats_list:
                avatar = await common.get_member(self.bot, stats[-1]).avatar_url_as(format="png",
                                                                                    static_format="png").read()
                thumbnail = Image.open(io.BytesIO(avatar))
                level = stats[6]
                XP = stats[5]
                neededXP = next_level(level + 1) - next_level(level)
                currentXP = XP - next_level(level)
                row = (stats[0] - 1, thumbnail, stats[1], nr(stats[2]), nr(stats[3]), nr(stats[4]), nr(XP), nr(level),
                       currentXP / neededXP)
                rowData.append(row)
            board_card = Leaderboard(rowData)
            card = io.BytesIO()
            board_card.canvas.save(card, "PNG")
            card.seek(0)
        else:
            card = None
        return card

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not self.creatingLeaderboard:
            self.creatingLeaderboard = True
            leaderboardMessageID = common.database.get([('', ''), ("leaderboardMessageID", '')], dbTable="memory")[0][0]
            if payload.message_id == leaderboardMessageID and payload.user_id != common.bot_id:
                channel = await self.bot.fetch_channel(payload.channel_id)
                leaderboardMessage = await channel.fetch_message(leaderboardMessageID)
                leaderboardControls = common.leaderboard_controls
                page = int(float(leaderboardMessage.attachments[0].filename[0]))
                lastPage = int(common.database.get([('', ''), ("COUNT(*)", '')], dbTable="leveling")[0][0] / 10)
                leaderboardDict = {leaderboardControls[0]: 0,
                                   leaderboardControls[1]: page - 2,
                                   leaderboardControls[2]: page - 1,
                                   leaderboardControls[3]: page,
                                   leaderboardControls[4]: page + 1,
                                   leaderboardControls[5]: page + 2,
                                   leaderboardControls[6]: lastPage}
                newPage = leaderboardDict[payload.emoji.name]
                card = await self.leaderboard(newPage)
                if not card:
                    pass
                else:
                    message = await channel.send(file=discord.File(fp=card, filename=f"{str(newPage)}.png"))
                    await leaderboardMessage.delete()
                    common.database.update([('', ''), ("leaderboardMessageID", message.id)], dbTable="memory")
                    for control in common.leaderboard_controls:
                        await message.add_reaction(control)
            self.creatingLeaderboard = False

    @commands.Cog.listener()
    async def on_ready(self):
        await self.update_level_xp()

    @commands.command(name="toggle_update", alias=['tu'])
    async def toggle_update(self):
        if self.update:
            self.update = False
        else:
            self.update = True

    async def update_level_xp(self):
        while self.update:
            await update_passive_xp()
            await update_voice_xp()
            await self.update_level()
            await asyncio.sleep(common.minutes_to_seconds(2))

    async def update_level(self, author_id=None):
        async def level_check(memberID):
            general_channel = await self.bot.fetch_channel(common.general_channel_id)
            level = common.database.get([("memberID", memberID), ("level", '')], dbTable="leveling")[0][0]
            experience = common.database.get([("memberID", memberID), ("experience", '')], dbTable="leveling")[0][0]
            new_level = level
            while next_level(level) < experience:
                level += 1
            level -= 1
            if new_level != level:
                common.database.update([("memberID", memberID), ("level", level)], dbTable="leveling")
                member = common.get_member(self.bot, memberID)
                await general_channel.send(f"Good job <@{memberID}>:confetti_ball:, you progressed to level "
                                           f"{level}!:arrow_double_up:")

        if not author_id:
            memberID_list = common.database.get([('', ''), ("memberID", '')])
            for member_tuple in memberID_list:
                memberID = member_tuple[0]
                await level_check(memberID)
        else:
            await level_check(author_id)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and (member.guild.id == common.oasis_guild_id):
            before_mute = not nor(before.mute, before.self_mute)
            before_deaf = not nor(before.deaf, before.self_deaf)
            after_mute = not nor(after.mute, after.self_mute)
            after_deaf = not nor(after.deaf, after.self_deaf)
            join = (not before.channel) and after.channel
            leave = before.channel and (not after.channel)
            muted = (not before_mute) and after_mute
            unmuted = before_mute and (not after_mute)
            deafened = (not before_deaf) and after_deaf
            undeafened = before_deaf and (not after_deaf)
            afk = (not before.afk) and after.afk
            unafk = before.afk and (not after.afk)
            council_channel = await self.bot.fetch_channel(common.the_council_channel_id)

            if join and (after_mute or after_deaf):
                # join muted or deafened
                common.database.update([("memberID", member.id),
                                        ("timestampLastVoice", common.timestamp_convert(datetime.now()))],
                                       dbTable="leveling")
            elif (join and not (after_mute and after_deaf)) or unmuted or undeafened or (
                    unafk and not (after_mute and after_deaf)):
                # (join not muted and not deafened) or unmuted or undeafened or (unafk and not muted and not deafened)
                common.database.update([("memberID", member.id),
                                        ("timestampLastVoice", common.timestamp_convert(datetime.now()))],
                                       dbTable="leveling")
                common.database.update([("memberID", member.id), ("addXPVoice", True)], dbTable="leveling")
            elif leave or muted or deafened or afk:
                # leave or mute or deafen
                await update_voice_xp(member.id)
                common.database.update([("memberID", member.id), ("addXPVoice", False)], dbTable="leveling")
                if not (len(await check_add_xp()) > 0):
                    await council_channel.send(f"All members are not active")

    @commands.command(name="add_xp_members", aliases=["axm"])
    async def add_xp_members(self, ctx):
        addXPMemberID = await check_add_xp()
        for memberID in addXPMemberID:
            member = common.get_member(self.bot, memberID)
            await ctx.send(f"{member.name} is active")
        if not len(addXPMemberID):
            await ctx.send(f"No member is active")

    @commands.command(name="spawn_leaderboard", aliases=["sl"])
    async def spawn_leaderboard(self, ctx):
        achievements_channel = await self.bot.fetch_channel(common.achievements_channel_id)
        card = await self.leaderboard(0)
        message = await achievements_channel.send(file=discord.File(fp=card, filename=f"0.png"))
        common.database.update([('', ''), ("leaderboardMessageID", message.id)], dbTable="memory")
        for control in common.leaderboard_controls:
            await message.add_reaction(control)


def setup(bot):
    bot.add_cog(Leveling(bot))
