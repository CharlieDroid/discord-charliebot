from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import discord
import random

sys.path.insert(0, r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0")
from random import randint
from src.app import common


class Features(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll", aliases=['r'])
    async def roll(self, ctx, rollRange=2):
        if rollRange == 2:
            rollDict = {True: "Yes", False: "No"}
            await ctx.send(f"{rollDict[bool(randint(0, rollRange - 1))]}")
        else:
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

    @commands.command(name="epic_scrape", aliases=["es"])
    async def epic_scrape(self, ctx):
        await ctx.trigger_typing()
        r = requests.get(r"https://progameguides.com/lists/epic-games-store-free-games-list/")
        soup = BeautifulSoup(r.content, "html.parser")
        games = soup.find_all("h3")[:-6]
        games = [game.get_text() for game in games[:-6]]
        dates = soup.find_all("p", "has-text-align-center")[:len(games)]
        dates = [date.get_text() for date in dates]
        embed = discord.Embed(title="Current Free Games in Epic Games", color=0xffffff)
        for i in range(len(dates)):
            embed.add_field(name=games[i], value=dates[i], inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="study", aliases=["st"])
    async def study(self, ctx, num=1):
        exam = pd.read_csv(r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0\data\midterm exam.csv")
        num_rows = exam.shape[0]
        rand_rows = random.sample(range(num_rows + 1), num)
        rows = exam.iloc[rand_rows].drop("Your Answer", axis=1).values.tolist()
        messages = []
        for row in rows:
            messages.append(f"{row[0]}. {row[1]} :arrow_forward:  ||{row[2]}||")
        await ctx.send('\n'.join(messages))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.errors.Forbidden):
            await ctx.send(f"I am missing permissions.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == 873790063836790794 and (before.channel is None and after.channel.id == 811395892338622512):
            general_channel = await self.bot.fetch_channel(common.general_channel_id)
            message = random.choices(["Hi people", "Hi guys"], weights=(0.6, 0.4))[0]
            await general_channel.send(message)


def setup(bot):
    bot.add_cog(Features(bot))
