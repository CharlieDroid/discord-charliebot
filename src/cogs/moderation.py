from src.app import common
import discord
import asyncio
from better_profanity import profanity
from difflib import SequenceMatcher
from random import choice
from profanity_check import predict_prob
from discord.ext import commands
from datetime import datetime

profanity.load_censor_words(common.bad_words, whitelist_words=common.good_words)


async def violation_warning(message, numViolations, messageType):
    embed = discord.Embed(
        title=f"You have {numViolations} violation{common.check_plural(numViolations)} now.",
        colour=discord.Colour.from_rgb(255, 69, 61))
    if (common.mute_violation_count - 2) < numViolations < common.mute_violation_count:
        leftViolations = common.mute_violation_count - numViolations + 1
        embed.set_footer(text=f"{leftViolations} violation{common.check_plural(leftViolations)} left until muted.")
    elif (common.kick_violation_count - 3) < numViolations < common.kick_violation_count:
        leftViolations = common.kick_violation_count - numViolations + 1
        embed.set_footer(text=f"{leftViolations} violation{common.check_plural(leftViolations)} left until kicked.")
    elif (common.ban_violation_count - 3) < numViolations < common.ban_violation_count:
        leftViolations = common.ban_violation_count - numViolations + 1
        embed.set_footer(text=f"{leftViolations} violation{common.check_plural(leftViolations)} left until banned.")
    if messageType == 0:
        embed.set_image(url=choice(common.profanity))
    elif messageType == 1:
        embed.set_image(url=choice(common.spamming))
    await message.reply(embed=embed)


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def check_author(self, memberNameID, author, ctx=None):
        member = None
        if (author.id in common.the_council_id + [common.bot_id]) or (author.top_role.id == common.admin_role_id):
            member = common.get_member(self.bot, memberNameID)
            if member is None:
                if ctx is not None:
                    await ctx.send(common.member_not_found(memberNameID))
                return None
        return member

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if not message.author.bot and not message.content.startswith(common.bot_prefixes) \
                    and message.guild.id == common.oasis_guild_id and not message.channel.is_nsfw() \
                    and not message.content == '':
                timestampLastMessage = \
                    common.database.get([("memberID", message.author.id), ("timestampLastMessage", "")])[0][0]
                totalTimeMessage = (datetime.now() - common.timestamp_convert(timestampLastMessage)).seconds
                lastMessage = common.database.get([("memberID", message.author.id), ("lastMessage", "")])[0][0]
                # check profanity
                if predict_prob([message.content])[0] > 0.7 or profanity.contains_profanity(message.content):
                    await self.add_violation(message)
                # check if less than 2 seconds or same message as before
                elif (totalTimeMessage < 2) or (SequenceMatcher(None, message.content, lastMessage).quick_ratio() > 0.7):
                    await self.add_counter(message)
                # reset counter if it's over the temporary duration
                elif totalTimeMessage > common.minutes_to_seconds(common.temporary_duration):
                    common.database.update([("memberID", message.author.id), ("counter", 0)])

                # updates last message sent and timestamp of it
                common.database.update([("memberID", message.author.id), ("lastMessage", message.content)])
                common.database.update([("memberID", message.author.id),
                                        ("timestampLastMessage", common.snowflake_to_timestamp(message.id))])
        except (AttributeError, IndexError):
            pass

    async def add_violation(self, message, messageType=0):
        author_id = message.author.id
        numViolations = common.database.get([("memberID", author_id), ("numViolations", "")])[0][0] + 1
        timestampLastViolation = common.database.get([("memberID", author_id), ("timestampLastViolation", "")])[0][0]
        common.database.update([("memberID", author_id), ("numViolations", numViolations)])
        common.database.update([("memberID", author_id),
                                ("timestampLastViolation", common.snowflake_to_timestamp(message.id))])

        datetimeLastViolation = common.timestamp_convert(timestampLastViolation)
        totalTimeViolation = (datetime.now() - datetimeLastViolation).seconds
        muteViolationCount = common.mute_violation_count
        kickViolationCount = common.kick_violation_count
        banViolationCount = common.ban_violation_count
        muteTimeSeconds = common.minutes_to_seconds(common.mute_violation_time)
        kickTimeSeconds = common.minutes_to_seconds(common.kick_violation_time)
        banTimeSeconds = common.minutes_to_seconds(common.ban_violation_time)

        ctx = await self.bot.get_context(message)
        # if violations more than 0 and
        # if the last time violation till now is greater than 90 minutes then reset violations
        if (numViolations > 0) and (totalTimeViolation > banTimeSeconds):
            common.database.update([("memberID", author_id), ("numViolations", 0)])
            return
        elif (muteViolationCount <= numViolations <= muteViolationCount) and (totalTimeViolation < muteTimeSeconds):
            return await self.tempmute(ctx, author_id, reason=common.violation_reason(muteViolationCount, "muted"))
        elif (kickViolationCount <= numViolations <= kickViolationCount) and (totalTimeViolation < kickTimeSeconds):
            return await self.kick(ctx, author_id, reason=common.violation_reason(kickViolationCount, "kicked"))
        elif (banViolationCount <= numViolations <= banViolationCount) and (totalTimeViolation < banTimeSeconds):
            return await self.tempban(ctx, author_id, reason=common.violation_reason(banViolationCount, "banned"))
        elif numViolations > common.threshold_count:
            return await self.ban(ctx, author_id, reason="Too many violations")
        await violation_warning(message, numViolations, messageType)

    async def add_counter(self, message):
        counter = common.database.get([("memberID", message.author.id), ("counter", "")])[0][0] + 1
        common.database.update([("memberID", message.author.id), ("counter", counter)])
        if counter >= common.counter_count:
            await self.add_violation(message, messageType=1)

    @commands.command(name="violations")
    async def violations(self, ctx, memberNameID):
        member = common.get_member(self.bot, memberNameID)
        numViolations = common.database.get([("memberID", member.id), ("numViolations", "")])[0][0]
        await ctx.send(f"{member.name} has {numViolations} violations.")

    @commands.command(name="tempmute")
    async def tempmute(self, ctx, memberNameID, duration=5, reason=None):
        member = await self.check_author(memberNameID, ctx.author, ctx=ctx)
        if member:
            if not isinstance(duration, int):
                await ctx.send(f"Mute duration of {duration} is not possible.")
            else:
                await self.mute(ctx, memberNameID, reason)
                await ctx.send(common.temp_message(member.name, duration, "muted"))
                await asyncio.sleep(common.minutes_to_seconds(duration))
                await self.unmute(ctx, memberNameID)
                await ctx.send(f"{memberNameID} has been unmuted.")

    @commands.command(name="tempban")
    async def tempban(self, ctx, memberNameID, duration=5, reason=None):
        member = await self.check_author(memberNameID, ctx.author, ctx=ctx)
        if member:
            if not isinstance(duration, int):
                await ctx.send(f"Ban duration of {duration} is not possible.")
            else:
                await self.ban(ctx, memberNameID)
                await ctx.send(common.temp_message(member.name, duration, "banned"))
                await asyncio.sleep(common.minutes_to_seconds(duration))
                await self.unban(ctx, memberNameID)
                await ctx.send(f"{memberNameID} has been unbanned.")

    @commands.command(name="mute")
    async def mute(self, ctx, memberNameID, reason=None):
        member = await self.check_author(memberNameID, ctx.author, ctx=ctx)
        if member:
            await member.add_roles(discord.Object(common.muted_role_id), reason=reason)

    @commands.command(name="unmute")
    async def unmute(self, ctx, memberNameID, reason=None):
        member = await self.check_author(memberNameID, ctx.author, ctx=ctx)
        if member:
            await member.remove_roles(discord.Object(common.muted_role_id), reason=reason)

    @commands.command(name="kick")
    async def kick(self, ctx, memberNameID, reason=None):
        member = await self.check_author(memberNameID, ctx.author, ctx=ctx)
        if member:
            await member.kick(reason=reason)

    @commands.command(name="ban")
    async def ban(self, ctx, memberNameID, reason=None):
        member = await self.check_author(memberNameID, ctx.author, ctx=ctx)
        if member:
            await member.ban(reason=reason)

    @commands.command(name="unban")
    async def unban(self, ctx, memberNameID, reason=None):
        member = await self.check_author(memberNameID, ctx.author, ctx=ctx)
        if member:
            await member.unban(reason=reason)

    @commands.command(name="dj")
    async def dj(self, ctx, memberNameID):
        member = await self.check_author(memberNameID, ctx.author, ctx=ctx)
        if member:
            await member.add_roles(discord.Object(common.dj_role_id),
                                   reason=common.dj_message(ctx.author.name, member.name))


def setup(bot):
    bot.add_cog(Moderation(bot))
