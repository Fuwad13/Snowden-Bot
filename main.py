import time
import aiohttp
import discord
import random
import asyncio
import typing
import os
from discord.ext import commands, tasks
from itertools import cycle
from discord.ext.commands import BucketType
from dotenv import load_dotenv
from utility import help_cmd 




import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


load_dotenv()  # take environment variables from .env.
os.environ["JISHAKU_HIDE"] = "True"
# --------tokens and keys-----------------

TOKEN = os.getenv("TOKEN")

UPTIME_DICT = {'uts': ""}


# ======================= Bot constructor =====================
intents = discord.Intents(messages=True, guilds=True,
                          reactions=True, members=True, presences=True, emojis=True)


def get_prefix(bot, message):

    prefixes = ['sd', 'Sd', 'snow']

    if not message.guild:

        return 'sd'

    return commands.when_mentioned_or(*prefixes)(bot, message)


bot = commands.AutoShardedBot(
    command_prefix=get_prefix, intents=intents, case_insensitive=True, strip_after_prefix=True, slash_commands = True)





# extensions
INITIAL_EXTENSIONS = ['jishaku']

ALL_EXTENSIONS = ['cogs.scores', 'cogs.games', 'cogs.weather',
                  'cogs.image', 'cogs.web_search', 'cogs.info', "cogs.misc", 'cogs.error_handler', 'jishaku']


if __name__ == "__main__":
    for e in INITIAL_EXTENSIONS:
        bot.load_extension(e)

bot.help_command = help_cmd.SnowdenHelp()

#events =========
@bot.event
async def on_ready():
    UPTIME_DICT["uts"] = str(int(time.time()))
    bot.uptime = int(UPTIME_DICT["uts"])
    #activity_change_.start()
    print(f'logged in as {bot.user}')
    bot.get_command("jishaku").hidden = True

@bot.event
async def on_command(ctx):
    logger.warning(f"command invoked : {ctx.command} in {ctx.channel.id} by {ctx.author}")

#tasks


@tasks.loop(seconds=60, count=2)
async def activity_change_():
    print("1")
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=f"@Snowden"))

# dev essential commands


@bot.command(name="loadcog", aliases=['lc', 'loadc'], hidden=True, brief="Loads a cog")
@commands.is_owner()
async def _loadcog(ctx, cogname: str):
    try:
        tick = bot.get_emoji(880695423516430336)
        cname = f"{cogname}"

        bot.load_extension(cname)
        em = discord.Embed(
            title=f"{tick} Successfully Loaded  `{cogname}`",  color=0x2F3136)
        await ctx.channel.send(embed=em)
    except Exception as e:
        await ctx.channel.send(e)


@_loadcog.error
async def _loadcogerror(ctx, error):
    await ctx.channel.send(f"`Error`: `{error}`")


@bot.command(name="unloadcog", aliases=["uc"], hidden=True, brief="Unloads a cog")
@commands.is_owner()
async def _unloadcog(ctx, cogname: str):

    try:
        tick = bot.get_emoji(880695423516430336)
        cname = f"{cogname}"

        bot.unload_extension(cname)
        em = discord.Embed(
            title=f"{tick} Successfully unloaded  `{cogname}`",  color=0x2F3136)
        await ctx.channel.send(embed=em)
    except Exception as e:
        await ctx.channel.send(e)


@_unloadcog.error
async def _unloadcogerror(ctx, error):
    await ctx.channel.send(f"`Error`: `{error}`")


@bot.command(name="reloadall", aliases=["ra", "rela"], hidden=True, brief="Reloads all cogs, [if not loaded previously, then loads the cog]")
@commands.is_owner()
async def reloadall(ctx):
    success_s = ""
    tick = bot.get_emoji(880695423516430336)
    for e in ALL_EXTENSIONS:
        try:
            bot.reload_extension(e)
            tt = f"{str(tick)} `{e.split('cogs.')[-1]}`\n"
            success_s += tt
        except commands.ExtensionNotLoaded:
            bot.load_extension(e)
            tt = f"{str(tick)} `{e.split('cogs.')[-1]}`\n"
            success_s += tt
    em = discord.Embed(
        title="Success!", description=f"Successfully reloaded these cogs!\n{success_s}", color=0x2F3136)
    await ctx.channel.send(embed=em)
    

@reloadall.error
async def reloadallerror(ctx, error):
    await ctx.channel.send(f"`ERROR` : `{error}`")


@bot.command(name="reloadcog", aliases=["rc", "r"], hidden=True, brief="Reloads a cog")
@commands.is_owner()
async def _reloadcog(ctx, cogname: str):
    try:
        tick = bot.get_emoji(880695423516430336)
        cname = f"{cogname}"
        bot.reload_extension(cname)
        em = discord.Embed(
            title=f"Cogs Reloader", description=f"{tick} Successfully reloaded the cog `{cogname}`", timestamp=ctx.message.created_at)
        await ctx.channel.send(embed=em)
    except commands.ExtensionNotLoaded:
        await ctx.channel.send("This cog was not loaded")


@_reloadcog.error
async def reloaderror(ctx, error):
    await ctx.channel.send(f"`ERROR` : `{error}`")






bot.run(TOKEN)

