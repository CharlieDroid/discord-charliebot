import discord
from discord.ext import commands
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from app import common
from cogs.leveling import update_voice

"""
order of checking will be verification, moderation, features, uno
"""

load_dotenv()
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='~', intents=intents)


async def check_user_id(ctx):
    if ctx.author.id != common.owner_id:
        await ctx.send("You are not my father")
        return False
    return True


@bot.command()
async def reload(ctx, extension):
    if await check_user_id(ctx):
        cog_extension = f"cogs.{extension}"
        try:
            bot.reload_extension(cog_extension)
            await ctx.send(f"{cog_extension} was reloaded")
        except discord.ExtensionNotLoaded:
            await ctx.send(f"{cog_extension} was not reloaded")


@bot.command()
async def load(ctx, extension):
    if await check_user_id(ctx):
        cog_extension = f"cogs.{extension}"
        bot.load_extension(cog_extension)
        await ctx.send(f"{cog_extension} was loaded")


@bot.command()
async def unload(ctx, extension):
    if await check_user_id(ctx):
        cog_extension = f"cogs.{extension}"
        bot.unload_extension(cog_extension)
        await ctx.send(f"{cog_extension} was unloaded")


@bot.command()
async def shutdown(ctx):
    if ctx.author.id == common.owner_id:
        await ctx.send("Shutting down...")
        print("Shutting down...")
        for memberID in common.database.get_actives():
            await update_voice(memberID)
            common.database.update([("memberID", memberID), ("xpMult", 0)], dbTable="leveling")
        await bot.close()
        sys.exit()


@bot.event
async def on_ready():
    activity = discord.Activity(name="Detroit: Become Human", type=5)
    await bot.change_presence(activity=activity)

    print(f"{bot.user} is connected to the following guild:")
    for guild in bot.guilds:
        print(f"{guild.name} (id: {guild.id})")


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        cog_extension = f"cogs.{filename[:-3]}"
        try:
            bot.load_extension(cog_extension)
            print(f"{cog_extension} loaded")
        except Exception as err:
            print(err)

bot.run(TOKEN)
