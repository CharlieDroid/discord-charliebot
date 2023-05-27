"""
Don't use fetch_guild bro
"""
from app import common
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


class View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


class Verification(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="spawn_welcome", aliases=["sw"])
    async def spawn_welcome(self, ctx):
        view = View()
        view.clear_items()
        button = discord.ui.Button(emoji=common.check_emoji, label="V E R I F Y", custom_id="wc",
                                   style=discord.ButtonStyle.green)
        view.add_item(button)
        if ctx.author.id in common.the_council_id:
            welcome_channel = await self.bot.fetch_channel(common.welcome_channel_id)
            message = await welcome_channel.send(content=":point_down::point_down:", view=view)
            print(message.id)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.custom_id == "wc" and interaction.message.id == common.welcome_message_id:
            await interaction.user.remove_roles(discord.Object(common.unknown_role_id), reason="Agreed with rules")
            await interaction.user.add_roles(discord.Object(common.member_role_id), reason="Agreed with rules")
            common.database.update([("memberID", interaction.user.id), ("rulesReaction", 1)])
            await interaction.response.send_message(content="Welcome:confetti_ball:, you are now verified!! You have "
                                                            "unlocked the server :book:", ephemeral=True,
                                                    delete_after=60)

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
                                      rulesReaction=1)
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
                                      rulesReaction=1)
                await ctx.send(f"{member.name} welcome message sent!")
            else:
                await ctx.send(f"{memberNameID} not found!")

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
                                      rulesReaction=1)
                await ctx.send(f"{name} added to database!")
            else:
                await ctx.send(f"{message[0]} not found!")


def setup(bot):
    bot.add_cog(Verification(bot))
