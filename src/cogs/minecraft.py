from mcstatus import MinecraftServer
from discord.ext import commands
from dotenv import load_dotenv
import sys

sys.path.insert(0, r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0")
import common
import socket
import os


class Minecraft(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.key = 'MINECRAFT_SERVER_ADDRESS'

    # @commands.command(name='check_backup', aliases=['cb'])
    # async def check_backup(self, ctx, server_address=None):
    #     if common.kou_id != ctx.author.id:
    #         load_dotenv()
    #         if not server_address:
    #             server_address = os.getenv(self.key)
    #         try:
    #             MinecraftServer.lookup(server_address).status()
    #             await ctx.send('Server is online')
    #         except socket.timeout:
    #             await ctx.send('Server is offline')
    #     else:
    #         await ctx.send('kinda useless ngl')

    # @commands.Cog.listener()


def setup(bot):
    bot.add_cog(Minecraft(bot))
