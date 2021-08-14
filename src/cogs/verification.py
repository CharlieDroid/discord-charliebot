"""
Don't use fetch_guild bro
"""
import sys

sys.path.insert(0, r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0")
import common
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


class Verification(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        timestamp_now = common.timestamp_convert(datetime.now())
        await member.send(common.welcome_message(member))
        oasis_guild = self.bot.get_guildd(common.oasis_guild_id)
        unknown_role = oasis_guild.get_role(common.unknown_role_id)
        await member.add_roles(unknown_role, reason=common.audit_log)
        common.database.insert(memberID=member.id,
                               memberUsername=member.name,
                               memberName='No Name',
                               timestampJoined=timestamp_now,
                               timestampLastMessage=common.timestamp_convert(datetime.now()),
                               rulesReaction=await get_reaction_welcome_message(self.bot, member),
                               isVerified=0)

    @commands.command(name='welcome', aliases=['w'])
    async def welcome(self, ctx, memberNameID, snowflake):
        if ctx.author.id in common.the_council_id:
            member = self.get_member(memberNameID)
            if member:
                await ctx.send(common.welcome_message(member))
                oasis_guild = self.bot.get_guild(common.oasis_guild_id)
                unknown_role = oasis_guild.get_role(common.unknown_role_id)
                await member.add_roles(unknown_role, reason=common.audit_log)
                common.database.insert(memberID=member.id,
                                       memberUsername=member.name,
                                       memberName='No Name',
                                       timestampJoined=common.snowflake_to_timestamp(int(snowflake)),
                                       timestampLastMessage=common.timestamp_convert(datetime.now()),
                                       rulesReaction=await get_reaction_welcome_message(self.bot, member),
                                       isVerified=0)
            else:
                await ctx.send('Member not found')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await member.send('Goodbyes are not forever, are not the end; it simply means I\'ll miss you until we meet again. :sob:')
        common.database.delete(member.id)

    @commands.command(name='unverify', aliases=['uv'])
    async def unverify(self, ctx, memberNameID):
        member = self.get_member(memberNameID)
        if member:
            common.database.update([('memberID', member.id), ('isVerified', 0)])
        else:
            await ctx.send('Member is not found')

    @commands.command(name='add_database', aliases=['ad'])
    async def add_to_database(self, ctx, *message):
        # memberUsername or ID, memberName, snowFlakeID, isVerified
        if ctx.author.id in common.the_council_id:
            database = common.database
            member = self.get_member(message[0])
            if member:
                database.insert(memberID=member.id,
                                memberUsername=member.name,
                                memberName=message[1],
                                timestampJoined=common.snowflake_to_timestamp(int(message[2])),
                                timestampLastMessage=common.timestamp_convert(datetime.now()),
                                rulesReaction=await get_reaction_welcome_message(self.bot, member),
                                isVerified=int(message[3]))
            else:
                await ctx.send('Member is not found')

    def get_member(self, memberNameID):
        oasis_guild = self.bot.get_guild(common.oasis_guild_id)
        member = oasis_guild.get_member_named(memberNameID)
        if not member:
            member = oasis_guild.get_member(int(memberNameID))
            if not member:
                return False
        return member

    @commands.command(name='test', aliases=['t'])
    async def test(self, ctx, *message):
        member = self.get_member(message[0])
        await ctx.send(common.welcome_message(member))


def setup(bot):
    bot.add_cog(Verification(bot))
