import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import sys
sys.path.insert(0, r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0")
import common
from discord_components import DiscordComponents

load_dotenv()
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='~',
                   intents=intents)
DiscordComponents(bot)


async def check_user_id(ctx):
    if ctx.author.id == common.blue_bird_id:
        await ctx.send('Are you mama?')
        return False
    elif ctx.author.id != common.owner_id:
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
        except discord.ext.commands.errors.ExtensionNotLoaded:
            await ctx.send(f"{cog_extension} was not loaded")


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


@bot.event
async def on_ready():
    activity = discord.Activity(name="Detroit: Become Human", type=5)
    await bot.change_presence(activity=activity)

    print(f"{bot.user} is connected to the following guild:")
    for guild in bot.guilds:
        print(f"{guild.name} (id: {guild.id})")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)
