from discord.ext import commands
import sys
import discord

sys.path.insert(0, r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0")
from random import randint


class Features(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll", aliases=['r'])
    async def roll(self, ctx, rollRange=3):
        await ctx.send(f"{randint(1, rollRange)}")

    # noinspection PyTypeChecker
    @commands.command(name="grow_castle", aliases=["gc"])
    async def grow_castle(self, ctx, waves, heroDmgLvl):
        waves, heroDmgLvl = int(waves), int(heroDmgLvl)
        embed = discord.Embed(title="Grow Castle", color=0x80cee1)
        embed.add_field(name="XP Tree", value=round(heroDmgLvl, 0), inline=False)
        embed.add_field(name="HP:", value=round(heroDmgLvl / 2, 0), inline=True)
        embed.add_field(name="Gold:", value=round((1/6) * heroDmgLvl, 0), inline=True)
        embed.add_field(name="Mana:", value=round((1/6) * heroDmgLvl, 0), inline=True)
        embed.add_field(name="Town Archer:", value=round(heroDmgLvl / 12, 0), inline=True)
        embed.add_field(name="Waves", value=waves, inline=False)
        embed.add_field(name="Hero:", value=round(0.06 * waves, 0), inline=True)
        embed.add_field(name="Flying Orc:", value=round(0.05 * waves, 0), inline=True)
        embed.add_field(name="Goblin/Cannon:", value=round(0.04 * waves, 0), inline=True)
        embed.add_field(name="Other Heroes/Towers/Worm:", value=round(0.03 * waves, 0), inline=True)
        embed.add_field(name="Castle Level:", value=round(0.1 * waves, 0), inline=True)
        embed.set_footer(text="If you have extra gold use for main hero.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Features(bot))
