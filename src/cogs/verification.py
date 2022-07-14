"""
Don't use fetch_guild bro
"""
import sys

sys.path.insert(0, r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0")
from src.app import common
import discord
from discord.ext import commands
from datetime import datetime


async def database_insert(memberID, memberUsername, timestampJoined, timestampLastMessage, rulesReaction,
                          memberName="N/A", numViolations=0, timestampLastViolation=0, lastMessage=None,
                          inServer=True, counter=0):
    common.database.insert(memberID=memberID,
                           memberUsername=memberUsername,
                           memberName=memberName,
                           timestampJoined=timestampJoined,
                           timestampLastMessage=timestampLastMessage,
                           rulesReaction=rulesReaction,
                           numViolations=numViolations,
                           timestampLastViolation=timestampLastViolation,
                           lastMessage=lastMessage,
                           counter=counter,
                           inServer=inServer)


class Verification(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            timestamp_now = common.timestamp_convert(datetime.now())
            await member.send(common.welcome_message(member))
            await member.add_roles(discord.Object(common.unknown_role_id), reason="Just joined")
            memberID = common.database.get([("memberID", member.id), ("1", '')])
            if not memberID:
                await database_insert(memberID=member.id,
                                      memberUsername=member.name,
                                      timestampJoined=timestamp_now,
                                      timestampLastMessage=timestamp_now,
                                      rulesReaction=await self.get_reaction_welcome_message(member))
            else:
                common.database.update([("memberID", member.id), ("timestampJoined", timestamp_now)])
                common.database.update([("memberID", member.id), ("timestampLastUpdate", timestamp_now)],
                                       dbTable="leveling")
                common.database.update([("memberID", member.id), ("inServer", True)])

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        common.database.update([("memberID", member.id), ("inServer", False)])

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
                                      rulesReaction=await self.get_reaction_welcome_message(member))
                await ctx.send(f"{member.name} welcome message sent!")
            else:
                await ctx.send(f"{memberNameID} not found!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == common.welcome_message_id:
            reaction = await self.get_reaction_welcome_message(payload.member)
            if reaction:
                await payload.member.send(f"Welcome:confetti_ball:, you have agreed with the rules.")
                await payload.member.remove_roles(discord.Object(common.unknown_role_id), reason="Agreed with rules")
                await payload.member.add_roles(discord.Object(common.member_role_id), reason="Agreed with rules")
            common.database.update([["memberID", payload.member.id], ["rulesReaction", reaction]])

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id == common.welcome_message_id:
            member = common.get_member(self.bot, payload.user_id)
            reaction = await self.get_reaction_welcome_message(member)
            if not reaction:
                await member.send(f"You have not agreed with the rules. Your roles are removed.:face_with_monocle:")
                for role in common.all_roles:
                    await member.remove_roles(discord.Object(role), reason="Did not agree with rules")
                await member.add_roles(discord.Object(common.unknown_role_id), reason="Did not agree with rules")
            common.database.update([["memberID", member.id], ["rulesReaction", reaction]])

    @commands.Cog.listener()
    async def on_ready(self):
        for memberID in common.database.get_ids():
            member = common.get_member(self.bot, memberID)
            if member is None:
                common.database.update([("memberID", memberID), ("inServer", False)])
            else:
                common.database.update([("memberID", memberID), ("memberUsername", member.name)])
                common.database.update([("memberID", memberID), ("inServer", True)])
        print("Member Usernames updated!")

    @commands.command(name='add_database', aliases=['ad'])
    async def add_to_database(self, ctx, *message):
        # memberUsername or ID, name, snowflake
        if ctx.author.id in common.the_council_id:
            member = common.get_member(self.bot, message[0])
            if member:
                name = message[1]
                snowflake = message[2]
                await database_insert(memberID=member.id,
                                      memberUsername=member.name,
                                      timestampJoined=common.snowflake_to_timestamp(int(snowflake)),
                                      timestampLastMessage=common.timestamp_convert(datetime.now()),
                                      rulesReaction=await self.get_reaction_welcome_message(member))
                await ctx.send(f"{name} added to database!")
            else:
                await ctx.send(f"{message[0]} not found!")

    async def get_reaction_welcome_message(self, member):  # checks the member's reaction
        welcome_channel = await self.bot.fetch_channel(common.welcome_channel_id)
        welcome_message = await welcome_channel.fetch_message(common.welcome_message_id)
        reactions_list = welcome_message.reactions
        check_index = [r.emoji for r in reactions_list].index(common.check_emoji)
        check_reaction = reactions_list[check_index]
        check_users = [m.id for m in await check_reaction.users().flatten()]
        return member.id in check_users
        # check or not check


def setup(bot):
    bot.add_cog(Verification(bot))
