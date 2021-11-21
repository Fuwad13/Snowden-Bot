import asyncio
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.errors import NoPrivateMessage


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise NoPrivateMessage("This command can run only in a guild channel.")
        else:
            return True

def setup(bot):
    bot.add_cog(Utility(bot))
