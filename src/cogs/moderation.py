import sys

sys.path.insert(0, r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0")
import common
import discord
import asyncio
from difflib import SequenceMatcher
from random import choice
from profanity_check import predict_prob
from discord.ext import commands
from datetime import datetime


def check_author(bot, memberNameID, author_id, author_role_id):
    if (author_id in common.the_council_id) or (author_role_id == common.admin_role_id):
        return common.get_member(bot, memberNameID)
    return 2


async def violation_warning(message, numViolations, messageType):
    embed = discord.Embed(
        title=f"You have {numViolations} violation{'s' if numViolations > 1 else ''} now.",
        colour=discord.Colour.from_rgb(255, 69, 61))
    if (common.mute_violation_count - 2) < numViolations < common.mute_violation_count:
        leftViolations = common.mute_violation_count - numViolations
        embed.set_footer(text=f"{leftViolations} violation{'s' if leftViolations > 1 else ''} left until muted.")
    elif (common.kick_violation_count - 3) < numViolations < common.kick_violation_count:
        leftViolations = common.kick_violation_count - numViolations
        embed.set_footer(text=f"{leftViolations} violation{'s' if leftViolations > 1 else ''} left until kicked.")
    elif (common.ban_violation_count - 3) < numViolations < common.ban_violation_count:
        leftViolations = common.ban_violation_count - numViolations
        embed.set_footer(text=f"{leftViolations} violation{'s' if leftViolations > 1 else ''} left until banned.")
    if messageType == 0:
        embed.set_image(url=choice(common.profanity))
    elif messageType == 1:
        embed.set_image(url=choice(common.spamming))
    await message.reply(embed=embed)


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild.id == common.oasis_guild_id and message.author.id != common.bot_id:
            totalTimeMessage = (datetime.now() - common.timestamp_convert(common.database.get(
                [("memberID", message.author.id), ("timestampLastMessage", "")]
            )[0][0])).seconds
            lastMessage = common.database.get([("memberID", message.author.id), ("lastMessage", "")])[0][0]
            if predict_prob([message.content]) > 0.7 and message.channel.id != common.nsfw_channel_id:
                await self.add_violation(message)
            elif (totalTimeMessage < 3) or (SequenceMatcher(None, message.content, lastMessage).quick_ratio() > 0.7):
                await self.add_counter(message)
            elif totalTimeMessage > common.minutes_to_seconds(common.temporary_duration):
                common.database.update([("memberID", message.author.id),
                                        ("counter", 0)])
            common.database.update([("memberID", message.author.id), ("lastMessage", message.content)])
            common.database.update([("memberID", message.author.id),
                                    ("timestampLastMessage", common.timestamp_convert(datetime.now()))])

    async def add_violation(self, message, messageType=0):
        numViolations = common.database.get([("memberID", message.author.id),
                                             ("numViolations", "")])[0][0]
        timestampLastViolation = common.database.get([("memberID", message.author.id),
                                                      ("timestampLastViolation", "")])[0][0]
        numViolations += 1
        common.database.update([("memberID", message.author.id), ("numViolations", numViolations)])
        common.database.update([("memberID", message.author.id),
                                ("timestampLastViolation", common.timestamp_convert(datetime.now()))])

        datetimeLastViolation = common.timestamp_convert(timestampLastViolation)
        totalTimeViolation = (datetime.now() - datetimeLastViolation).seconds
        muteViolationCount = common.mute_violation_count
        kickViolationCount = common.kick_violation_count
        banViolationCount = common.ban_violation_count
        muteTimeSeconds = common.minutes_to_seconds(common.mute_violation_time)
        kickTimeSeconds = common.minutes_to_seconds(common.kick_violation_time)
        banTimeSeconds = common.minutes_to_seconds(common.ban_violation_time)

        ctx = await self.bot.get_context(message)
        if (muteViolationCount < numViolations < (muteViolationCount + 2)) and (totalTimeViolation < muteTimeSeconds):
            return await self.tempmute(ctx, message.author.id)
        elif (kickViolationCount < numViolations < (kickViolationCount + 2)) and (totalTimeViolation < kickTimeSeconds):
            return await self.kick(ctx, message.author.id)
        elif (banViolationCount < numViolations < (banViolationCount + 2)) and (totalTimeViolation < banTimeSeconds):
            return await self.ban(ctx, message.author.id)
        elif totalTimeViolation > banTimeSeconds:
            numViolations = 0
            common.database.update([("memberID", message.author.id), ("numViolations", numViolations)])
        await violation_warning(message, numViolations, messageType)

    async def add_counter(self, message):
        counter = common.database.get([("memberID", message.author.id), ("counter", "")])[0][0]
        counter += 1
        common.database.update([("memberID", message.author.id), ("counter", counter)])
        if counter > common.counter_count:
            await self.add_violation(message, messageType=1)

    @commands.command(name="violations")
    async def violations(self, ctx, memberNameID):
        member = common.get_member(self.bot, memberNameID)
        numViolations = common.database.get([("memberID", member.id),
                                             ("numViolations", "")])[0][0]
        await ctx.send(f"{member.name} has {numViolations} violations.")

    @commands.command(name="mute")
    async def mute(self, ctx, memberNameID):
        member = check_author(self.bot, memberNameID, ctx.author.id, ctx.author.top_role.id)
        if not member:
            await ctx.send(f"{memberNameID} not found!")
        elif member != 2:
            await member.add_roles(discord.Object(common.muted_role_id), reason="Violation/command from user")

    @commands.command(name="unmute")
    async def unmute(self, ctx, memberNameID):
        member = check_author(self.bot, memberNameID, ctx.author.id, ctx.author.top_role.id)
        if not member:
            await ctx.send(f"{memberNameID} not found!")
        elif member != 2:
            await member.remove_roles(discord.Object(common.muted_role_id),
                                      reason="Done serving his violation/command from user")
            await ctx.send(f"{member.name} has been unmuted.")

    @commands.command(name="tempmute")
    async def tempmute(self, ctx, memberNameID, duration=5):
        member = check_author(self.bot, memberNameID, ctx.author.id, ctx.author.top_role.id)
        if not member:
            await ctx.send(f"{memberNameID} not found!")
        elif member != 2:
            if type(duration) == str:
                await ctx.send(f"Mute duration of {duration} is not possible.")
            else:
                await self.mute(ctx, memberNameID)
                await ctx.send(f"{member.name} has been muted for {duration} minute{'s' if duration > 1 else ''}.")
                await asyncio.sleep(common.minutes_to_seconds(duration))
                await self.unmute(ctx, memberNameID)

    @commands.command(name="ban")
    async def ban(self, ctx, memberNameID, reason=None):
        member = check_author(self.bot, memberNameID, ctx.author.id, ctx.author.top_role.id)
        if not member:
            await ctx.send(f"{memberNameID} not found!")
        elif member != 2:
            await member.ban(reason=reason)

    @commands.command(name="unban")
    async def unban(self, ctx, memberNameID, reason=None):
        member = check_author(self.bot, memberNameID, ctx.author.id, ctx.author.top_role.id)
        if not member:
            await ctx.send(f"{memberNameID} not found!")
        elif member != 2:
            await member.unban(reason=reason)

    @commands.command(name="tempban")
    async def tempban(self, ctx, memberNameID, duration=5, reason=None):
        member = check_author(self.bot, memberNameID, ctx.author.id, ctx.author.top_role.id)
        if not member:
            await ctx.send(f"{memberNameID} not found!")
        elif member != 2:
            if type(duration) == str:
                await ctx.send(f"Ban duration of {duration} is not possible.")
            else:
                await self.ban(ctx, memberNameID)
                await ctx.send(f"{member.name} has been banned for {duration} minute{'s' if duration > 1 else ''}.")
                await asyncio.sleep(common.minutes_to_seconds(duration))
                await self.unban(ctx, memberNameID)

    @commands.command(name="kick")
    async def kick(self, ctx, memberNameID, reason=None):
        member = check_author(self.bot, memberNameID, ctx.author.id, ctx.author.top_role.id)
        if not member:
            await ctx.send(f"{memberNameID} not found!")
        elif member != 2:
            try:
                await member.kick(reason=reason)
                await ctx.send(f"{member.name} has been kicked.")
            except discord.errors.Forbidden:
                await ctx.send(f"{member.name} cannot be kicked. I am missing permissions.")

    @commands.command(name="dj")
    async def dj(self, ctx, memberNameID):
        member = check_author(self.bot, memberNameID, ctx.author.id, ctx.author.top_role.id)
        if not member:
            await ctx.send(f"{memberNameID} not found!")
        elif member != 2:
            await member.add_roles(discord.Object(common.dj_role_id), reason=None)

    @commands.command(name="test", aliases=['t'])
    async def test(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Moderation(bot))