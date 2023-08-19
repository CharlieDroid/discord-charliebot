from discord.ext import commands
import discord
from app import common
from random import random


def interpolate(x, x1, x2, y1, y2):
    return y1 + (x - x1) * ((y2 - y1)/(x2 - x1))


def roll(member_id):
    output = None
    pulls = common.database.get([("memberID", member_id), ("nPulls", '')], dbTable="game")[0][0]
    rng = random()
    if pulls >= 200:
        if pulls <= 250:
            if rng < interpolate(pulls, 200, 250, common.ur_prob, common.ur_max_prob):
                output = 'ur'
            elif rng < interpolate(pulls, 200, 250, common.sr_prob, common.sr_max_prob):
                output = 'sr'
            elif rng < interpolate(pulls, 200, 250, common.r_prob, common.r_max_prob):
                output = 'r'
        else:
            if rng < common.ur_max_prob:
                output = 'ur'
            elif rng < common.sr_max_prob:
                output = 'sr'
            elif rng < common.r_max_prob:
                output = 'r'
    else:
        if rng < common.ur_prob:
            output = 'ur'
        elif rng < common.sr_prob:
            output = 'sr'
        elif rng < common.r_prob:
            output = 'r'
    return output


class Gacha(commands.Cog):

    def __init__(self, bot):
        self.bot = bot




def setup(bot):
    bot.add_cog(Gacha(bot))
