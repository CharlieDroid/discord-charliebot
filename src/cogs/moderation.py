from app import common
import discord
from difflib import SequenceMatcher
from discord.ext import commands
import datetime


"""
4 counts before violation - "I can see that you've been sending too many messages you should slow down"
2 counts before violation - "I suggest you stop sending messages until this message disappears"
"This is your _ violation/s. You are muted for _ minute/s. You will be kicked in _ violations"
1 violation - 1 minute
4 violations - 30 minutes
8 violations - 1 hr
10 violations - kick
"""

async def warning(message, count, isCounter, duration=0):
    if isCounter:
        counts_until = common.counter_threshold - count
        if counts_until in (4, 2):
            embed = discord.Embed(color=0xff6961)
            embed.set_footer(text=f"{counts_until} messages until you're muted")
            if counts_until > 2:
                embed.add_field(name="You've been sending too many messages too fast, you should slow down.",
                                value="", inline=False)
                await message.reply(embed=embed)
            else:
                embed.add_field(name="I suggest you send a message after this message disappears", value='', inline=False)
                await message.reply(embed=embed, delete_after=common.minutes_to_seconds(common.temporary_duration))
    else:
        counts_until = common.violation_threshold - count
        embed = discord.Embed(color=0xff6961)
        embed.set_footer(text=f"You will be kicked in {counts_until} violation{common.check_plural(counts_until)}")
        embed.add_field(name=f"This is your {common.ordinal(count)} violation{common.check_plural(count)}.",
                        value=f"You are muted for {duration} minute{common.check_plural(duration)}.", inline=False)
        await message.reply(embed=embed)


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if not message.author.bot and not message.content.startswith(common.bot_prefixes) and message.content != '' and message.guild.id == common.oasis_guild_id:
                timestampLastMessage = \
                    common.database.get([("memberID", message.author.id), ("timestampLastMessage", "")])[0][0]
                totalTimeMessage = (datetime.datetime.now() - common.timestamp_convert(timestampLastMessage)).seconds
                lastMessage = common.database.get([("memberID", message.author.id), ("lastMessage", "")])[0][0]
                # reset counter if it's over the temporary duration (3 minutes in common)
                if totalTimeMessage > common.minutes_to_seconds(common.temporary_duration):
                    common.database.update([("memberID", message.author.id), ("counter", 0)])
                # check if less than 2 seconds or same message as before
                elif (totalTimeMessage < 4) or (
                        SequenceMatcher(None, message.content, lastMessage).real_quick_ratio() > 0.8):
                    await self.add_counter(message)
                # updates last message sent and timestamp of it
                common.database.update([("memberID", message.author.id), ("lastMessage", message.content)])
                common.database.update([("memberID", message.author.id),
                                        ("timestampLastMessage", common.snowflake_to_timestamp(message.id))])
        except (AttributeError, IndexError):
            pass

    async def add_violation(self, message):
        reason = "spamming messages"
        author_id = message.author.id
        numViolations = common.database.get([("memberID", author_id), ("numViolations", "")])[0][0] + 1
        timestampLastViolation = common.database.get([("memberID", author_id), ("timestampLastViolation", "")])[0][0]
        common.database.update([("memberID", author_id), ("numViolations", numViolations)])
        common.database.update([("memberID", author_id),
                                ("timestampLastViolation", common.snowflake_to_timestamp(message.id))])
        datetimeLastViolation = common.timestamp_convert(timestampLastViolation)
        totalTimeViolation = (datetime.datetime.now() - datetimeLastViolation).seconds
        if totalTimeViolation > common.minutes_to_seconds(common.violation_reset_time):
            common.database.update([("memberID", author_id), ("numViolations", 0)])
        elif numViolations >= (common.violation_threshold - 2):
            await message.author.timeout_for(datetime.timedelta(0, common.third_violation_duration), reason=reason)
        elif numViolations >= (common.violation_threshold - 4):
            await message.author.timeout_for(datetime.timedelta(0, common.second_violation_duration), reason=reason)
        else:
            await message.author.timeout_for(datetime.timedelta(0, common.first_violation_duration), reason=reason)
        await warning(message, numViolations, False)

    async def add_counter(self, message):
        counter = common.database.get([("memberID", message.author.id), ("counter", "")])[0][0] + 1
        common.database.update([("memberID", message.author.id), ("counter", counter)])
        if counter >= common.counter_threshold:
            await self.add_violation(message)
        else:
            await warning(message, counter, True)

    @commands.command(name="violations")
    async def violations(self, ctx, memberNameID):
        member = common.get_member(self.bot, memberNameID)
        numViolations = common.database.get([("memberID", member.id), ("numViolations", "")])[0][0]
        await ctx.send(f"{member.name} has {numViolations} violations.")

    # @commands.command(name='test')
    # async def test(self, ctx):
    #     await ctx.send("moderation.py has been loaded bossing")

    @commands.command(name="dj")
    async def dj(self, ctx, memberNameID):
        member = await self.check_author(memberNameID, ctx.author, ctx=ctx)
        if member:
            await member.add_roles(discord.Object(common.dj_role_id),
                                   reason=common.dj_message(ctx.author.name, member.name))


def setup(bot):
    bot.add_cog(Moderation(bot))
