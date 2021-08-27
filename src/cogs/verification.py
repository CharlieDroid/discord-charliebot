"""
Don't use fetch_guild bro
"""
import sys
import asyncio

sys.path.insert(0, r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0")
import common
import discord
from discord.ext import commands
from datetime import datetime


async def get_reaction_welcome_message(bot, member):
    welcome_channel = await bot.fetch_channel(common.welcome_channel_id)
    welcome_message = await welcome_channel.fetch_message(common.welcome_message_id)
    reactions_list = welcome_message.reactions

    def get_index_emoji(reactions_list, reaction):
        return [r.emoji for r in reactions_list].index(reaction)

    check_reaction = reactions_list[get_index_emoji(reactions_list, common.check_emoji)]
    x_reaction = reactions_list[get_index_emoji(reactions_list, common.x_emoji)]
    check_users = [m.id for m in await check_reaction.users().flatten()]
    x_users = [m.id for m in await x_reaction.users().flatten()]
    if member.id in x_users:
        return 0
    elif member.id in check_users:
        return 1
    return 2


async def database_insert(memberID, memberUsername, timestampJoined, timestampLastMessage, rulesReaction,
                          memberName="N/A", numViolations=0, timestampLastViolation=0, lastMessage=None, counter=0):
    common.database.insert(memberID=memberID,
                           memberUsername=memberUsername,
                           memberName=memberName,
                           timestampJoined=timestampJoined,
                           timestampLastMessage=timestampLastMessage,
                           rulesReaction=rulesReaction,
                           numViolations=numViolations,
                           timestampLastViolation=timestampLastViolation,
                           lastMessage=lastMessage,
                           counter=counter)


class Verification(commands.Cog):

    def __init__(self, bot):
        self.numPasses = 0
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        timestamp_now = common.timestamp_convert(datetime.now())
        await member.send(common.welcome_message(member))
        if self.numPasses == 0:
            await member.add_roles(discord.Object(common.unknown_role_id), reason="Just joined")
        elif self.numPasses > 0:
            self.numPasses -= 1
            await member.add_roles(discord.Object(common.member_role_id), reason="Just joined")
        await database_insert(memberID=member.id,
                              memberUsername=member.name,
                              timestampJoined=timestamp_now,
                              timestampLastMessage=timestamp_now,
                              rulesReaction=await get_reaction_welcome_message(self.bot, member))

    @commands.command(name='welcome', aliases=['w'])
    async def welcome(self, ctx, memberNameID, snowflake):
        if ctx.author.id in common.the_council_id:
            member = common.get_member(self.bot, memberNameID)
            if member:
                await member.send(common.welcome_message(member))
                await member.add_roles(discord.Object(common.unknown_role_id), reason="Just joined")
                await database_insert(memberID=member.id,
                                      memberUsername=member.name,
                                      timestampJoined=common.snowflake_to_timestamp(int(snowflake)),
                                      timestampLastMessage=common.timestamp_convert(datetime.now()),
                                      rulesReaction=await get_reaction_welcome_message(self.bot, member))
            else:
                await ctx.send(f"{memberNameID} not found!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == common.welcome_message_id:
            reaction = await get_reaction_welcome_message(self.bot, payload.member)
            if not reaction:
                await payload.member.send(f"You have not agreed with the rules.")
                for role in common.all_roles:
                    await payload.member.remove_roles(discord.Object(role), reason="Did not agree with rules")
                await payload.member.add_roles(discord.Object(common.unknown_role_id),
                                               reason="Did not agree with rules")
            elif reaction == 1:
                await payload.member.send(f"Welcome:confetti_ball:, you have agreed with the rules.")
                await payload.member.remove_roles(discord.Object(common.unknown_role_id),
                                                  reason="Agreed with rules")
                await payload.member.add_roles(discord.Object(common.member_role_id), reason="Agreed with rules")

            common.database.update([["memberID", payload.member.id], ["rulesReaction", reaction]])

    @commands.Cog.listener()
    async def on_ready(self):
        memberID_list = common.database.get([['', ''], ['memberID', '']])
        for member_tuple in memberID_list:
            memberID = member_tuple[0]
            member = common.get_member(self.bot, memberID)
            common.database.update([['memberID', memberID], ['memberUsername', member.name]])
        print("Updated member usernames and formerly rules reaction!")

    @commands.command(name='add_database', aliases=['ad'])
    async def add_to_database(self, ctx, *message):
        # memberUsername or ID, name, snowflake
        if ctx.author.id in common.the_council_id:
            member = common.get_member(self.bot, message[0])
            if member:
                name = message[1]
                snowflake = message[2]
                common.database.insert(memberID=member.id,
                                       memberUsername=member.name,
                                       memberName=name,
                                       timestampJoined=common.snowflake_to_timestamp(int(snowflake)),
                                       timestampLastMessage=common.timestamp_convert(datetime.now()),
                                       rulesReaction=await get_reaction_welcome_message(self.bot, member))
                await ctx.send(f"{name} added to database!")
            else:
                await ctx.send(f"{message[0]} not found!")

    @commands.command(name="you_shall_pass")
    async def you_shall_pass(self, ctx, numPasses):
        self.numPasses = int(numPasses)

    @commands.command(name="charlie_analysis", aliases=["ca"])
    async def charlie_analysis(self, ctx):
        if ctx.author.id == common.owner_id:
            message = await ctx.reply(f":face_with_monocle:")
            await ctx.trigger_typing()
            await asyncio.sleep(8)
            await message.edit(content=f":cold_sweat:It looks Korean sir.:confounded:")


def setup(bot):
    bot.add_cog(Verification(bot))
