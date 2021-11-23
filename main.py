import os
import random
import asyncio
import typing
import time
import json
import difflib
import aiohttp
import discord
from discord.ext import commands, tasks
from discord.ext.commands import BucketType
from dotenv import load_dotenv
from utils import help_cmd , buttons_and_selects
import asyncpg
import logging
import ast
import re
import inspect
from utils.context_managers import UserLock
from utils.errors import Blacklisted

def source(o):
    s = inspect.getsource(o).split("\n")
    indent = len(s[0]) - len(s[0].lstrip())
    return "\n".join(i[indent:] for i in s)


def ready():
  source_ = source(discord.gateway.DiscordWebSocket.identify)
  patched = re.sub(
      r'([\'"]\$browser[\'"]:\s?[\'"]).+([\'"])',
      r"\1Discord Android\2",
      source_
  )
  loc = {}
  exec(compile(ast.parse(patched), "<string>", "exec"),
       discord.gateway.__dict__, loc)
  discord.gateway.DiscordWebSocket.identify = loc["identify"]

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




# ======================= Bot constructor =====================
intents = discord.Intents(messages=True, guilds=True,
                          reactions=True, members=True, emojis=True, bans = True)


def get_prefix(bot, message):

    prefixes = ['sd', 'Sd', 'S/', 'SD', 's/']

    if not message.guild:

        return 's/'

    return commands.when_mentioned_or(*prefixes)(bot, message)

class SnowdenContext(commands.Context):
    
    async def send(self, content = None, **kwargs):
        ch = random.choice(
            [":star: I'm still under development, don't expect too much from me!", ":star: More features will be added , keep patience!", ":star: Vote me to get exclusive rewards!"]
        )
        if random.randint(1,15) == 9:
            content = f"{ch}\n\n{str(content) if content else ''}"
            return await super().send(content, **kwargs)

        return await super().send(content, **kwargs)

class SnowdenBot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blacklist = {}
        self.automod_guilds = {}
        self.user_lock = {}
        self.command_running = {}

    def add_user_lock(self, lock : UserLock):
        self.user_lock.update({lock.user.id: lock})

    async def check_user_lock(self, user: typing.Union[discord.Member, discord.User]):
        if lock := self.user_lock.get(user.id):
            if lock.locked():
                if isinstance(lock, UserLock):
                    raise lock.error
                raise commands.CommandError("You can't invoke another command while another command is running.")
            else:
                self.user_lock.pop(user.id, None)

    async def running_command(self, ctx: SnowdenContext, **flags):
        dispatch = flags.pop("dispatch", True)
        if dispatch:
            self.dispatch('command', ctx)
        try:
            await self.check_user_lock(ctx.author)
            check = await self.can_run(ctx, call_once=flags.pop("call_once", True))
            if check or not flags.pop("call_check", True):
                ctx.running = True
                await ctx.trigger_typing()
                await ctx.command.invoke(ctx)
            else:
                raise commands.CheckFailure('The global check once functions failed.')
        except commands.CommandError as exc:
            if dispatch:
                await ctx.command.dispatch_error(ctx, exc)
            if flags.pop("redirect_error", False):
                raise
        else:
            if dispatch:
                self.dispatch('command_completion', ctx)
        finally:
            ctx.running = False
            self.command_running.pop(ctx.message.id, None)

    async def invoke(self, ctx: SnowdenContext, **flags) -> None:
        dispatch = flags.get("dispatch", True)
        if ctx.command is not None:
            run_in_task = flags.pop("in_task", True)
            if run_in_task:
                command_task = self.loop.create_task(self.running_command(ctx, **flags))
                self.command_running.update({ctx.message.id: command_task})
            else:
                await self.running_command(ctx, **flags)
        elif ctx.invoked_with:
            exc = commands.CommandNotFound('Command "{}" is not found'.format(ctx.invoked_with))
            if dispatch:
                self.dispatch('command_error', ctx, exc)

            if flags.pop("redirect_error", False):
                raise exc

        

        

    async def get_context(self, message, *, cls=SnowdenContext):
        return await super().get_context(message, cls=cls)



bot = SnowdenBot(
    command_prefix=get_prefix, intents=intents, case_insensitive=True, strip_after_prefix=True,slash_commands=True, chunk_guilds_at_startup = False)





# extensions
INITIAL_EXTENSIONS = ['cogs.games',
                      'cogs.image','cogs.moderation', 'cogs.info', "cogs.misc",'cogs.error_handler','cogs.events', 'jishaku', 'cogs.owner']

ALL_EXTENSIONS = ['cogs.games',
                  'cogs.image', 'cogs.info', "cogs.misc",'cogs.automod', 'cogs.error_handler','cogs.events', 'jishaku', 'cogs.owner']


if __name__ == "__main__":
    for e in INITIAL_EXTENSIONS:
        bot.load_extension(e)

bot.help_command = help_cmd.SnowdenHelp()


# database

async def create_db_pool():
    credential = "postgres://jqqsebpbrbqxac:7a794f0e39633d490eb582e9dd531b77e85af2995eddd9c9f9fc8ce2b72a4f07@ec2-44-198-204-136.compute-1.amazonaws.com:5432/d5ipdv1nvq274t"
    bot.db = await asyncpg.create_pool(dsn = f'{credential}')
    bot.session = aiohttp.ClientSession()
    

    

#events =========
@bot.check
async def black_list(ctx):
    
    mf = ctx.bot.blacklist.get(str(ctx.author.id))
    
    if mf:
        raise Blacklisted(f"You have been blacklisted from using any commands.\nreason: {mf}")

    else:
        return True

@bot.event
async def on_ready():
    bot.uptime = int(time.time())
    #activity_change_.start()
    print(f'logged in as {bot.user}')

#tasks
async def run_once_when_ready():
    await bot.wait_until_ready()
    bl_w = await bot.db.fetch("select guild_id , bl_words from guilds;")
    for g in bl_w:
        k = str(g['guild_id'])
        v = json.loads(g['bl_words'])
        bot.automod_guilds[k] = v
    print("Blacklisted words loaded")
    



# dev essential commands


@bot.command(name="loadcog", aliases=['lc', 'loadc'], hidden=True, brief="Loads a cog")
@commands.is_owner()
async def _loadcog(ctx, *, cogname: str):
    try:
        tick = bot.get_emoji(880695423516430336)
        cname = difflib.get_close_matches(cogname.lower(), ALL_EXTENSIONS, n=1, cutoff= 0.5)
        cname = cname[0]

        bot.load_extension(cname)
        em = discord.Embed(
            title=f"{tick} Successfully Loaded  `{cname}`",  color=0x2F3136)
        await ctx.channel.send(embed=em)
    except Exception as e:
        await ctx.channel.send(e)


@_loadcog.error
async def _loadcogerror(ctx, error):
    await ctx.channel.send(f"`Error`: `{error}`")


@bot.command(name="unloadcog", aliases=["unload"], hidden=True, brief="Unloads a cog")
@commands.is_owner()
async def _unloadcog(ctx, *,cogname: str):

    try:
        tick = bot.get_emoji(880695423516430336)
        cname = difflib.get_close_matches(cogname.lower(), ALL_EXTENSIONS, n=1, cutoff= 0.5)
        cname = cname[0]
        bot.unload_extension(cname)
        em = discord.Embed(
            title=f"{tick} Successfully unloaded  `{cname}`",  color=0x2F3136)
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
async def _reloadcog(ctx, *, cogname: str):
    try:
        tick = bot.get_emoji(880695423516430336)
        cname = difflib.get_close_matches(cogname.lower(), ALL_EXTENSIONS, n=1, cutoff= 0.5)
        cname = cname[0]
        bot.reload_extension(cname)
        em = discord.Embed(
            title=f"Cogs Reloader", description=f"{tick} Successfully reloaded the cog `{cname}`", timestamp=ctx.message.created_at)
        await ctx.channel.send(embed=em)
    except commands.ExtensionNotLoaded:
        await ctx.channel.send("This cog was not loaded")


@_reloadcog.error
async def reloaderror(ctx, error):
    await ctx.channel.send(f"`ERROR` : `{error}`")




if __name__ == "__main__":
    bot.loop.run_until_complete(create_db_pool())
    #bot.loop.create_task(run_once_when_ready())
    ready()
    bot.run(TOKEN)

