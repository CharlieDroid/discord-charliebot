import sys

sys.path.insert(0, r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0")
import common
from profanity_check import predict_prob
from discord.ext import commands
from datetime import datetime


async def add_violation(message):
    numViolations = common.database.get([("memberID", message.author.id),
                                         ("numViolations", "")])[0][0]
    common.database.update([("memberID", message.author.id), ("numViolations", (numViolations + 1))])
    timestampLastViolation = common.database.get([("memberID", message.author.id),
                                                  ("timestampLastViolation", "")])[0][0]
    if timestampLastViolation == 0:
        common.database.update([("memberID", message.author.id),
                                ("timestampLastViolation", common.timestamp_convert(datetime.now()))])


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild.id == common.oasis_guild_id and message.author.id != common.bot_id:
            if predict_prob([message.content]) > 0.7:
                await add_violation(message)


def setup(bot):
    bot.add_cog(Moderation(bot))
